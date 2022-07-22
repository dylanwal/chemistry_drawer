
import numpy as np
from rdkit import Chem

from chemdraw.objects.atoms import Atom
from chemdraw.objects.bonds import Bond
from chemdraw.utils.mole_file_parser import parse_mole_file
import chemdraw.utils.vector_math as vector_math


def get_mole_file(smiles: str) -> str:
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
    return Chem.MolToMolBlock(mol)


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
        mole_file = get_mole_file(smiles)
        atoms, bonds, file_version = parse_mole_file(mole_file)
        self.atoms: list[Atom] = atoms
        self.bonds: list[Bond] = bonds
        self.file_version: str = file_version

        # position
        self._offset = None
        self._center = get_center(self.atoms)
        self._position = None
        self.position = position

        # add molecule as parent
        for atom in self.atoms:
            atom.parent = self
        for bond in self.bonds:
            bond.parent = self

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
