import enum

import numpy as np

import chemdraw.rings
from chemdraw.errors import MoleParsingError


def parse_mol_file(file: str) -> tuple[dict, list[list], list[list]]:
    # separate and clean
    file_list = file.split("\n")
    file_list = clean_file_list(file_list)

    # first row
    first_row = parse_first_row(file_list.pop(0))

    # atom block
    atom_block_last_index = get_block_last_index(file_list)
    atom_block = split_block(file_list[:atom_block_last_index + 1])

    # bond block
    bond_block_last_index = get_block_last_index(file_list[atom_block_last_index + 1:])
    bond_block = split_block(file_list[atom_block_last_index + 1:atom_block_last_index + 2 + bond_block_last_index])

    # double checks for parse
    if first_row["number_atoms"] != len(atom_block):
        raise MoleParsingError(f"Number of atoms parsed does not match first row atom count. "
                               f"(first row: {first_row['number_atoms']}, parsed: {len(atom_block)})")
    if first_row["number_bonds"] != len(bond_block):
        raise MoleParsingError("Number of bonds parsed does not match first row bond count. "
                               f"(first row: {first_row['number_bonds']}, parsed: {len(bond_block)})")

    return first_row, atom_block, bond_block


def parse_first_row(first_row: str) -> dict:
    first_row = first_row.split()
    if len(first_row) != 11:
        raise MoleParsingError("First row not correct.", str(first_row))

    return {
        "number_atoms": int(first_row[0]),
        "number_bonds": int(first_row[1]),
        "chiral": bool(first_row[4]),
        "file_version": first_row[10]
    }


def split_block(block: list[str]) -> list[list[str]]:
    """[first_atom_index, second_atom_index, bond_type, sterochemistry]"""
    return [row.split() for row in block]


def clean_file_list(file_list: list[str]) -> list[str]:
    for i in range(len(file_list)):
        if "V2000" in file_list[i]:
            return file_list[i:]

    raise MoleParsingError("First row not found. (looking for 'V2000')")


def get_block_last_index(file_list: list[str]) -> int:
    row_length = len(file_list[0].split())
    for i, row in enumerate(file_list):
        if len(row.split()) != row_length:
            return i - 1

    raise MoleParsingError("No transition between atom and bond blocks found.")


#######################################################################################################################

def get_rings(graph: np.ndarray) -> list[list[int]]:
    return [[]]  # vizialization.rings.get_rings(graph)


def normalise(vector: np.ndarray) -> np.ndarray:
    """
    Object is guaranteed to be a unit quaternion after calling this
    operation UNLESS the object is equivalent to Quaternion(0)
    """
    n = np.sqrt(np.dot(vector, vector))
    if n > 0:
        return vector / n
    else:
        return vector


class BondType(enum.Enum):
    single = 1
    double = 2
    triple = 3


class Bond:
    def __init__(self, row: np.ndarray, id_: int, parent):
        self.id_ = id_
        self.atom_ids = row[:2]
        self.type_ = BondType(int(row[2]))
        self._x = None  # [x0, x1]
        self._y = None  # [y0, y1]
        self.atoms = []
        self.rings = []
        self._vector = None
        self._perpendicular = None
        self._alignment = None
        self._center = None
        self.parent = parent

    def __repr__(self) -> str:
        return f"{self.atoms[0].symbol} -> {self.atoms[1].symbol} || {self.type_.name}"

    @property
    def x(self):
        return self._x + self.parent.offset[0]

    @x.setter
    def x(self, x: np.ndarray):
        self._x = x - self.parent.offset[0]

    @property
    def y(self):
        return self._y + self.parent.offset[1]

    @y.setter
    def y(self, y: np.ndarray):
        self._y = y - self.parent.offset[1]

    @property
    def vector(self) -> np.ndarray:
        if self._vector is None:
            self._vector = normalise(np.array([self.x[0] - self.x[1], self.y[0] - self.y[1]]))
        return self._vector

    @property
    def perpendicular(self) -> np.ndarray:
        if self._perpendicular is None:
            self._perpendicular = np.array([-self.vector[1], self.vector[0]])
        return self._perpendicular

    @property
    def center(self) -> np.ndarray:
        return np.array([np.mean(self.x), np.mean(self.y)])

    def add_atoms(self, atom1, atom2):
        self.atoms = [atom1, atom2]
        self._x = np.array([atom1._x, atom2._x])
        self._y = np.array([atom1._y, atom2._y])
        self._center = np.array([np.mean(self._x), np.mean(self._y)])

    @property
    def alignment(self) -> int:
        """ 0: center, 1: with perpendicular, 2: opposite of perpendicular"""
        if self._alignment is None:
            self._alignment = self._get_alignment()

        return self._alignment

    def _get_alignment(self) -> int:
        # only look at double bonds
        if self.type_ != BondType.double:
            return 0

        # aromatic rings
        if self.rings:
            for ring in self.rings:
                if ring.aromatic:
                    self._alignment = alignment_decision(self.vector, np.array(
                        [ring.center[0] - self.center[0], ring.center[1] - self.center[1]]))
                    return self._alignment

        # general
        if self.atoms[0].number_of_bonds == 2 and self.atoms[1].number_of_bonds == 2:
            return 0
        elif self.atoms[0].number_of_bonds == 3 and self.atoms[1].number_of_bonds == 2:
            return alignment_decision(self.perpendicular, self.atoms[0].vector)
        elif self.atoms[0].number_of_bonds == 2 and self.atoms[1].number_of_bonds == 3:
            return alignment_decision(self.perpendicular, self.atoms[1].vector)
        elif self.atoms[0].number_of_bonds == 3 and self.atoms[1].number_of_bonds == 3:
            return alignment_decision(self.perpendicular, self.atoms[1].vector)
            # non-ring
            # ring
        elif self.atoms[0].number_of_bonds == 4 and self.atoms[1].number_of_bonds == 2:
            return 0
        elif self.atoms[0].number_of_bonds == 2 and self.atoms[1].number_of_bonds == 4:
            return 0
        elif self.atoms[0].number_of_bonds == 4 and self.atoms[1].number_of_bonds == 4:
            return 0
            # non-ring
            # ring
        elif self.atoms[0].number_of_bonds == 4 and self.atoms[1].number_of_bonds == 3:
            return alignment_decision(self.perpendicular, self.atoms[1].vector)
        elif self.atoms[0].number_of_bonds == 3 and self.atoms[1].number_of_bonds == 4:
            return alignment_decision(self.perpendicular, self.atoms[0].vector)


def alignment_decision(atom_vector: np.ndarray, bond_perpendicular: np.ndarray) -> int:
    """ True: same side as perpendicular, False: opposite side of perpendicular """
    dot = np.dot(atom_vector, bond_perpendicular)
    if dot >= 0:
        return 1
    return 2


class Atom:
    atom_valency = {
        "H": 1,
        "B": 3,
        "C": 4,
        "N": 3,
        "O": 2,
        "F": 1,
        "Si": 4,
        "P": 3,
        "S": 2,
        "Cl": 1,
        "Br": 1,
        "I": 1,
    }

    def __init__(self, row: list[str], id_: int, parent):
        self.id_ = id_
        self._x = float(row[0])
        self._y = float(row[1])
        self.symbol = row[3]
        self.number_hydrogens = Atom.atom_valency[self.symbol]
        self.bonds = []
        self.rings = []
        self._vector = None
        self._number_of_bonds = None
        self.parent = parent

    def __repr__(self) -> str:
        return f"{self.symbol} ({self.id_}) at [{self.x}, {self.y}] with {len(self.bonds)}"

    @property
    def x(self) -> float:
        return self._x + self.parent.offset[0]

    @x.setter
    def x(self, x: float):
        self._x = x - self.parent.offset[0]

    @property
    def y(self) -> float:
        return self._y + self.parent.offset[1]

    @y.setter
    def y(self, y: float):
        self._y = y - self.parent.offset[1]

    @property
    def vector(self) -> np.ndarray:
        if self._vector is None:
            x = np.mean([bond._center[0] - self._x for bond in self.bonds])
            y = np.mean([bond._center[1] - self._y for bond in self.bonds])
            self._vector = normalise(np.array([x, y]))

        return self._vector

    @property
    def part_of_ring(self) -> bool:
        return bool(self.rings)

    @property
    def number_of_bonds(self) -> int:
        if self._number_of_bonds is None:
            self._number_of_bonds = np.sum([bond.type_.value for bond in self.bonds])

        return self._number_of_bonds

    def add_bond(self, bond):
        self.bonds.append(bond)
        self.number_hydrogens -= bond.type_.value


class Ring:
    def __init__(self, atom_ids: list[int], id_: int, parent):
        self.id_ = id_
        self.atom_ids = atom_ids
        self.atoms = []
        self.bonds = []
        self._ring_center = None
        self.parent = parent

    @property
    def center(self) -> np.ndarray:
        """ [x,y] """
        if self._ring_center is None:
            center = np.empty(2, dtype="float64")
            center[0] = np.mean([atom.x for atom in self.atoms])
            center[1] = np.mean([atom.y for atom in self.atoms])
            self._ring_center = center

        return self._ring_center + self.parent.offset

    @property
    def aromatic(self) -> bool:
        double_bond_count = len([True for bond in self.bonds if bond.type_ == BondType.double])
        return len(self.bonds) / double_bond_count == 0.5

    def add(self, atoms: list):
        # add atoms to ring
        self.atoms = atoms

        # add bonds to ring
        bonds = []
        for atom in atoms:
            for bond in atom.bonds:
                if bond in bonds:
                    self.bonds.append(bond)
                else:
                    bonds.append(bond)

        # add ring to atoms
        for atom in self.atoms:
            atom.rings.append(self)

        # add ring to bond
        for bond in self.bonds:
            bond.rings.append(self)


class MoleFile:
    def __init__(self, text: str, name: str = None, position: np.ndarray = np.array([0, 0])):
        self.name = name
        self.text = text

        # parsing
        first_row, atom_block, bond_block = parse_mol_file(text)

        # first row
        self.number_atoms: int = first_row["number_atoms"]
        self.number_bonds: int = first_row["number_bonds"]
        self.chiral: bool = first_row["chiral"]
        self.file_version: int = first_row["file_version"]

        # blocks
        self.atom_block: list[list[str]] = atom_block
        self.bond_block: list[list[str]] = bond_block
        self._bond_block: np.ndarray = np.array(bond_block, dtype="int8")
        self._bond_block[:, :2] = self._bond_block[:, :2] - 1  # to start indexes at 1

        # atom, bond, ring lists
        self.atoms: list[Atom] = [Atom(row, i, self) for i, row in enumerate(self.atom_block)]
        self.bonds: list[Bond] = [Bond(row, i, self) for i, row in enumerate(self._bond_block)]
        self.rings: list[Ring] = [Ring(row, i, self) for i, row in enumerate(get_rings(self._bond_block[:, :2]))]
        self.number_rings = len(self.rings)
        self.position = position
        self._center = self._get_center()

        self._add_bond_atoms()
        self._add_rings()

    def __repr__(self) -> str:
        text = ""
        if self.name is not None:
            text += self.name + " || "
        return text + f"# atoms: {self.number_atoms}, # bonds: {self.number_bonds}"

    @property
    def offset(self) -> np.ndarray:
        return self.position - self._center

    def _add_bond_atoms(self):
        for bond in self.bonds:
            # add atoms to bond
            bond.add_atoms(self.atoms[bond.atom_ids[0]], self.atoms[bond.atom_ids[1]])

            # add bonds to atoms
            for atom in bond.atoms:
                atom.add_bond(bond)

    def _add_rings(self):
        for ring in self.rings:
            ring.add([self.atoms[id_] for id_ in ring.atom_ids])

    def _get_center(self) -> np.ndarray:
        atoms = np.array([row[:2] for row in self.atom_block], dtype="float64")
        x = np.mean(atoms[:, 0])
        y = np.mean(atoms[:, 1])
        return np.array([x, y])

    def get_top_atom(self):
        top = self.atoms[0]
        for atom in self.atoms:
            if atom.y > top.y:
                top = atom

        return top

    def get_bottom_atom(self):
        bottom = self.atoms[0]
        for atom in self.atoms:
            if atom.y < bottom.y:
                bottom = atom

        return bottom
