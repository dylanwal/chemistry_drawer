import os
from typing import Any

import numpy as np
from sklearn.decomposition import PCA
from rdkit import Chem

from chemdraw.data_types import PointType
from chemdraw.errors import RDKitError
from chemdraw.utils.mole_file_parser import parse_mole_file, Sgroup
from chemdraw.objects.atoms import Atom
from chemdraw.objects.bonds import Bond
from chemdraw.objects.rings import Ring
from chemdraw.parenthesis import Parenthesis
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


def _process_molecule_inputs(smiles: str | None, mole_file: str | None):
    if smiles is not None:  # get mole file from SMILES
        try:
            mole_file, _rdkit_molecule = get_mole_file(smiles)
        except Exception as e:
            raise RDKitError("RDKit could not parse your SMILES string.")

    elif mole_file is not None:  # get SMILES from mole file
        if os.path.isfile(mole_file):
            with open(mole_file, 'r') as file:
                mole_file = file.read()
        try:
            _rdkit_molecule = Chem.MolFromMolBlock(mole_file)
        except Exception as e:
            raise RDKitError("RDKit could not parse your mole file.")
        smiles = Chem.MolToSmiles(_rdkit_molecule)
    else:
        raise ValueError("Please provide a 'smiles' or 'mole_file'.")

    return smiles, mole_file, _rdkit_molecule


class Molecule:
    def __init__(self,
                 smiles: str = None,
                 mole_file: str = None,
                 name: str = None,
                 coordinates: PointType = (0, 0)
                 ):
        """
        Parameters
        ----------
        smiles: str
            SMILES string
        mole_file: str
            file path to mole file or mole file as string
        name: str
            name of molecule
        coordinates: np.ndarray

        """
        smiles, mole_file, _rdkit_molecule = _process_molecule_inputs(smiles, mole_file)
        self.name = name
        self.smiles = smiles
        self._rdkit_molecule = _rdkit_molecule

        # parse mole file
        atom_symbols, atom_coordinates, bond_block, file_version, s_block = parse_mole_file(mole_file)
        self._atom_coordinates = np.copy(atom_coordinates)
        self.atom_coordinates = atom_coordinates  # atoms coordinates are linked to this array
        self.atoms: list[Atom] = self._add_atoms(atom_symbols)
        self.bonds: list[Bond] = self._add_bonds(bond_block)
        _add_bond_atoms(self.atoms, self.bonds)
        self.file_version: str = file_version

        # position
        self._coordinates = None
        self.parenthesis_coordinates = None
        self.coordinates = coordinates

        # get rings
        self.rings = self._add_rings()
        add_atoms_bonds_to_rings(self.rings, self.bonds)

        # get sblock
        self.parenthesis = self._add_parenthesis(s_block)

        # move center to zero
        shift_amount = np.mean(atom_coordinates, axis=0)
        self.atom_coordinates -= shift_amount
        if self.parenthesis_coordinates is not None:
            self.parenthesis_coordinates -= shift_amount
            self._vector = self.parenthesis[0].vector
        else:
            # rotate if no parenthesis
            self._vector = np.array([1, 0], dtype="float64")
            self.atom_coordinates = _rotate_molecule(atom_coordinates, self._vector)

    def __repr__(self) -> str:
        text = ""
        if self.name is not None:
            text += self.name + " || "
        text += f"# atoms: {self.number_atoms}, # bonds: {self.number_bonds}"
        if self.parenthesis is not None:
            text += f", # parenthesis: {len(self.parenthesis)}"
        return text

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
        if self.parenthesis_coordinates is not None:
            self.parenthesis_coordinates += coordinates

    @property
    def vector(self) -> np.ndarray:
        return self._vector

    @vector.setter
    def vector(self, vector: np.ndarray):
        vector = vector_math.normalize(vector)
        rot_matrix = vector_math.rotation_matrix(self.vector, vector)
        self.atom_coordinates = np.dot(self.atom_coordinates, rot_matrix)
        if self.parenthesis is not None:
            for parenthesis_ in self.parenthesis:
                parenthesis_.vector = np.dot(parenthesis_.vector, rot_matrix)
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
            bonds.append(Bond(atom_ids=row[:2]-1, bond_type=row[2], id_=i, stereo_chem=row[3], parent=self))

        return bonds

    def _add_rings(self) -> list[Ring]:
        ring_list = [[i for i in list(ring)] for ring in Chem.GetSymmSSSR(self._rdkit_molecule)]
        aromatic = [self._rdkit_molecule.GetAtomWithIdx(ring[0]).GetIsAromatic() for ring in ring_list]
        return [Ring(ring_list[i], i, self, aromatic[i]) for i in range(len(ring_list))]

    def _add_parenthesis(self, s_block: dict) -> list[Parenthesis]:
        counter = 0
        parenthesis_list = []
        for k, v in s_block.items():
            if v["type_"] == Sgroup.SRU or v["type_"] == Sgroup.GEN:
                kwargs = dict(
                    atoms=[self.atoms[i] for i in v['atoms']],
                    contained_bonds=[self.atoms[i] for i in v['bonds']],
                    parent=self
                )
                pos = np.array(v["position"])
                coordinate1 = np.array([np.mean([pos[0], pos[2]]), np.mean([pos[1], pos[3]])])
                coordinate2 = np.array([np.mean([pos[4], pos[6]]), np.mean([pos[5], pos[7]])])
                self._add_parenthesis_coordinates([coordinate1, coordinate2])
                vector = vector_math.normalize(np.array(coordinate1-coordinate2))

                par1 = Parenthesis(**kwargs, id_=counter, vector=-vector)
                counter += 1
                par2 = Parenthesis(**kwargs, id_=counter, vector=vector,
                                   sub_script=v["label"], super_script=v["connectivity"].name)
                counter += 1
                par1.parenthesis_partner = par2
                par2.parenthesis_partner = par1
                parenthesis_list += [par1, par2]

        return parenthesis_list

    def _add_parenthesis_coordinates(self, points: list[np.ndarray]):
        for point in points:
            if self.parenthesis_coordinates is None:
                self.parenthesis_coordinates = point.reshape((1, 2))
            else:
                self.parenthesis_coordinates = np.vstack((self.parenthesis_coordinates, point))

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
