from typing import Any

import numpy as np
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


def get_rings(molecule) -> list[Ring]:
    ring_list = [[i for i in list(ring)] for ring in Chem.GetSymmSSSR(molecule)]
    aromatic = [molecule.GetAtomWithIdx(ring[0]).GetIsAromatic() for ring in ring_list]
    return [Ring(ring_list[i], i, aromatic[i]) for i in range(len(ring_list))]


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
        center += atom.position

    center /= len(atoms)
    return center


class Molecule:

    def __init__(self, smiles: str, name: str = None, position: np.ndarray = np.array([0, 0])):
        self.name = name
        self.smiles = smiles

        # get mole file and parse
        mole_file, _rdkit_molecule = get_mole_file(smiles)
        atoms, bonds, file_version = parse_mole_file(mole_file)
        self._rdkit_molecule = _rdkit_molecule
        self.atoms: list[Atom] = atoms
        self.bonds: list[Bond] = bonds
        self.file_version: str = file_version

        # position
        self._offset = None
        self._center = get_center(self.atoms)
        self._position = None
        self.position = position

        # get rings
        self.rings = get_rings(self._rdkit_molecule)
        add_atoms_bonds_to_rings(self.rings, self.bonds)

        # add molecule as parent
        for atom in self.atoms:
            atom.parent = self
        for bond in self.bonds:
            bond.parent = self
        for ring in self.rings:
            ring.parent = self

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
    def position(self) -> np.ndarray:
        return self._position

    @position.setter
    def position(self, position: np.ndarray):
        self._position = position
        self._offset = position - self._center

    @property
    def offset(self) -> np.ndarray:
        return self._offset

    @property
    def atom_highlights(self) -> bool:
        return any([atom.highlight for atom in self.atoms])

    @property
    def bond_highlights(self) -> bool:
        return any([bond.highlight for bond in self.bonds])

    @property
    def has_highlights(self) -> bool:
        return any([self.atom_highlights, self.bond_highlights])

    def get_top_atom(self):
        top = self.atoms[0]
        for atom in self.atoms:
            if atom.position[1] > top.position[1]:
                top = atom

        return top

    def get_bottom_atom(self):
        bottom = self.atoms[0]
        for atom in self.atoms:
            if atom.position[1] < bottom.position[1]:
                bottom = atom

        return bottom
