import enum

import numpy as np

import chemdraw.utils.vector_math as vector_math


class BondType(enum.Enum):
    single = 1
    double = 2
    triple = 3


class BondAlignment(enum.Enum):
    center = 0
    perpendicular = 1
    opposite = 2


class Bond:
    def __init__(self, atom_ids: np.ndarray, bond_type: int, id_: int):
        self.atom_ids = atom_ids
        self.id_ = id_
        self.type_ = BondType(bond_type)

        self.atoms = []
        self.rings = []

        self._x = None  # [x0, x1]
        self._y = None  # [y0, y1]
        self._vector = None
        self._perpendicular = None
        self._alignment = None
        self._center = None

        self.parent = None

        # drawing stuff
        self.line_width = None
        self.highlight = None
        self.number = id_

    def __repr__(self) -> str:
        text = f"{self.atoms[0].symbol} ({self.atoms[0].id_}) -> {self.atoms[1].symbol} ({self.atoms[1].id_})"
        if self.type_ != BondType.single:
            text += f" || {self.type_.name}"
        return text

    @property
    def x(self) -> np.ndarray:
        return self._x + self.parent.offset[0]

    @property
    def y(self) -> np.ndarray:
        return self._y + self.parent.offset[1]

    @property
    def vector(self) -> np.ndarray:
        return self._vector

    @property
    def perpendicular(self) -> np.ndarray:
        return self._perpendicular

    @property
    def center(self) -> np.ndarray:
        return self._center + self.parent.offset

    @property
    def alignment(self) -> BondAlignment:
        """ 0: center, 1: with perpendicular, 2: opposite of perpendicular"""
        if self._alignment is None:
            self._alignment = self._get_alignment()

        return self._alignment

    @alignment.setter
    def alignment(self, value: int | str):
        if isinstance(value, int):
            self._alignment = BondAlignment(value)
            return
        else:
            values = set(item.name for item in BondAlignment)
            if value in values:
                self._alignment = BondAlignment[value]
                return

        raise ValueError("Invalid BondAlignment")

    @property
    def in_ring(self) -> bool:
        return bool(self.rings)

    def add_atoms(self, atom1, atom2):
        self.atoms = [atom1, atom2]
        self._update_position()
        self._update_vectors()

    def _update_position(self):
        self._x = np.array([self.atoms[0].position[0], self.atoms[1].position[0]])
        self._y = np.array([self.atoms[0].position[1], self.atoms[1].position[1]])

    def _update_vectors(self):
        if self.parent is None:
            self._vector = vector_math.normalize(np.array([self._x[1] - self._x[0], self._y[1] - self._y[0]]))
            self._perpendicular = np.array([-self.vector[1], self.vector[0]])
            self._center = np.array([np.mean(self._x), np.mean(self._y)])
        else:
            self._vector = vector_math.normalize(np.array([self.x[1] - self.x[0], self.y[1] - self.y[0]]))
            self._perpendicular = np.array([-self.vector[1], self.vector[0]])
            self._center = np.array([np.mean(self.x), np.mean(self.y)])

    def _get_alignment(self) -> BondAlignment:
        # only look at double bonds
        if self.type_ != BondType.double:
            return BondAlignment.center

        if self.in_ring:
            ring_ = self.rings[0]
            for ring in self.rings:
                if ring.aromatic:
                    ring_ = ring
                    break

            bond_ring_vector = ring_.center - self.center
            return alignment_decision(self.perpendicular, bond_ring_vector)

        # general
        if self.atoms[0].number_of_bonds == 2 and self.atoms[1].number_of_bonds == 2:
            return BondAlignment.center
        elif self.atoms[0].number_of_bonds == 3 and self.atoms[1].number_of_bonds == 2:
            return alignment_decision(self.perpendicular, self.atoms[0].vector)
        elif self.atoms[0].number_of_bonds == 2 and self.atoms[1].number_of_bonds == 3:
            return alignment_decision(self.perpendicular, self.atoms[1].vector)
        elif self.atoms[0].number_of_bonds == 3 and self.atoms[1].number_of_bonds == 3:
            return alignment_decision(self.perpendicular, self.atoms[1].vector)
            # non-ring
            # ring
        elif self.atoms[0].number_of_bonds == 4 and self.atoms[1].number_of_bonds == 2:
            return BondAlignment.center
        elif self.atoms[0].number_of_bonds == 2 and self.atoms[1].number_of_bonds == 4:
            return BondAlignment.center
        elif self.atoms[0].number_of_bonds == 4 and self.atoms[1].number_of_bonds == 4:
            return BondAlignment.center
            # non-ring
            # ring
        elif self.atoms[0].number_of_bonds == 4 and self.atoms[1].number_of_bonds == 3:
            return alignment_decision(self.perpendicular, self.atoms[1].vector)
        elif self.atoms[0].number_of_bonds == 3 and self.atoms[1].number_of_bonds == 4:
            return alignment_decision(self.perpendicular, self.atoms[0].vector)


def alignment_decision(atom_vector: np.ndarray, bond_perpendicular: np.ndarray) -> BondAlignment:
    """ True: same side as perpendicular, False: opposite side of perpendicular """
    dot = np.dot(atom_vector, bond_perpendicular)
    if dot >= 0:
        return BondAlignment.perpendicular
    return BondAlignment.opposite
