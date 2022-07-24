from typing import Any

import numpy as np
from sklearn.decomposition import PCA
from rdkit import Chem

from chemdraw.objects.atoms import Atom
from chemdraw.objects.bonds import Bond
from chemdraw.objects.rings import Ring
from chemdraw.utils.mole_file_parser import parse_mole_file
import chemdraw.utils.vector_math as vector_math


def get_mole_file(smiles: str) -> tuple[str, Any]:
    """
    Use RDkit to get Mole File.

    Parameters
    ----------
    smiles:
        smiles string (simplified molecular-input line-entry system)

    Returns
    -------
    mole_file: str
        mole file

    """
    mol = Chem.MolFromSmiles(smiles)
    return Chem.MolToMolBlock(mol), mol


def add_atoms_bonds_to_rings(rings: list[Ring], bonds: list[Bond]):
    bond_set = [set(bond.atom_ids) for bond in bonds]
    for ring in rings:
        ring_atom_ids = set(ring.atom_ids)
        for i, bond in enumerate(bond_set):
            if bond.issubset(ring_atom_ids):
                ring.bonds.append(bonds[i])
                bonds[i].rings.append(ring)
                ring.add_atoms(bonds[i].atoms)
                bonds[i].atoms[0].rings.append(ring)
                bonds[i].atoms[1].rings.append(ring)

        ring._center = get_center(ring.atoms)


def get_center(atoms: list[Atom]) -> np.ndarray:
    center = np.zeros(2, dtype="float64")

    for atom in atoms:
        center += atom.coordinates

    center /= len(atoms)
    return center


def get_largest_principle_component(coordinates: np.ndarray) -> np.ndarray:
    pca = PCA(n_components=2)
    pca.fit(coordinates)
    return vector_math.normalize(pca.components_[0])


def _rotate_molecule(coordinates: np.ndarray, new_vector: np.ndarray = np.array([1, 0], dtype="float64")) -> np.ndarray:
    vector = get_largest_principle_component(coordinates)
    rot_matrix = vector_math.rotation_matrix(vector, new_vector)
    return np.dot(coordinates, rot_matrix)


def _add_bond_atoms(atoms: list[Atom], bonds: list[Bond]):
    for bond in bonds:
        # add atoms to bond
        bond.atoms = (atoms[bond.atom_ids[0]], atoms[bond.atom_ids[1]])

        # add bonds to atoms
        for atom in bond.atoms:
            atom.add_bond(bond)


class Molecule:

    def __init__(self, smiles: str, name: str = None, coordinates: np.ndarray = np.array([0, 0])):
        self.name = name
        self.smiles = smiles

        # get mole file and molecule
        mole_file, _rdkit_molecule = get_mole_file(smiles)
        self._rdkit_molecule = _rdkit_molecule

        # parse mole file
        atom_symbols, atom_coordinates, bond_block, file_version = parse_mole_file(mole_file)
        # move center to zero
        atom_coordinates = atom_coordinates - np.mean(atom_coordinates, axis=0)
        self._vector = np.array([1, 0], dtype="float64")
        atom_coordinates = _rotate_molecule(atom_coordinates, self._vector)

        self._atom_coordinates = np.copy(atom_coordinates)
        self.atom_coordinates = atom_coordinates  # atoms coordinates are linked to this array
        self.atoms: list[Atom] = self._add_atoms(atom_symbols)
        self.bonds: list[Bond] = self._add_bonds(bond_block)
        _add_bond_atoms(self.atoms, self.bonds)
        self.file_version: str = file_version

        # position
        self._coordinates = None
        self.coordinates = coordinates

        # get rings
        self.rings = self._add_rings()
        add_atoms_bonds_to_rings(self.rings, self.bonds)

    def __repr__(self) -> str:
        text = ""
        if self.name is not None:
            text += self.name + " || "
        return text + f"# atoms: {self.number_atoms}, # bonds: {self.number_bonds}"

    @property
    def number_atoms(self) -> int:
        return len(self.atoms)

    @property
    def number_bonds(self) -> int:
        return len(self.bonds)

    @property
    def coordinates(self) -> np.ndarray:
        return self._coordinates

    @coordinates.setter
    def coordinates(self, coordinates: np.ndarray):
        self._coordinates = coordinates
        self.atom_coordinates += coordinates

    @property
    def vector(self) -> np.ndarray:
        return self._vector

    @vector.setter
    def vector(self, vector: np.ndarray):
        vector = vector_math.normalize(vector)
        rot_matrix = vector_math.rotation_matrix(self.vector, vector)
        self.atom_coordinates = np.dot(self.atom_coordinates, rot_matrix)
        self._vector = vector

    @property
    def atom_highlights(self) -> bool:
        return any([atom.highlight for atom in self.atoms])

    @property
    def bond_highlights(self) -> bool:
        return any([bond.highlight for bond in self.bonds])

    @property
    def has_highlights(self) -> bool:
        return any([self.atom_highlights, self.bond_highlights])

    def _add_atoms(self, atom_symbols: list[str]) -> list[Atom]:
        atoms = []
        for i, symbol in enumerate(atom_symbols):
            atoms.append(
                Atom(symbol=symbol, id_=i, parent=self)
            )
        return atoms

    def _add_bonds(self, bond_block: np.ndarray) -> list[Bond]:
        bonds = []
        for i, row in enumerate(bond_block):
            # -1 is to start counting at 0 instead of 1
            bonds.append(Bond(atom_ids=row[:2]-1, bond_type=row[2], id_=i, parent=self))

        return bonds

    def _add_rings(self) -> list[Ring]:
        ring_list = [[i for i in list(ring)] for ring in Chem.GetSymmSSSR(self._rdkit_molecule)]
        aromatic = [self._rdkit_molecule.GetAtomWithIdx(ring[0]).GetIsAromatic() for ring in ring_list]
        return [Ring(ring_list[i], i, self, aromatic[i]) for i in range(len(ring_list))]

    def get_top_atom(self):
        top = self.atoms[0]
        for atom in self.atoms:
            if atom.coordinates[1] > top.coordinates[1]:
                top = atom

        return top

    def get_bottom_atom(self):
        bottom = self.atoms[0]
        for atom in self.atoms:
            if atom.coordinates[1] < bottom.coordinates[1]:
                bottom = atom

        return bottom
