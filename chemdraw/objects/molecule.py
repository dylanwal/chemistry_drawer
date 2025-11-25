import pathlib

import numpy as np
from rdkit import Chem

from chemdraw.config.style_template import STYLE_TEMPLATE
from chemdraw.utils.mole_file_parser import parse_mole_file
from chemdraw.objects.atoms import Atom
from chemdraw.objects.bonds import Bond
from chemdraw.objects.rings import Ring
import chemdraw.utils.math_points as math_points


def count_digits_in_string(str_: str) -> int:
    digit_count = 0
    for char in str_:
        if char.isdigit():
            digit_count += 1
    return digit_count


def _process_molecule_inputs(input_: str | None):
    if isinstance(input_, Chem.Mol):
        smiles = Chem.MolToSmiles(input_)
        mole_file = Chem.MolToMolBlock(input_)
        return smiles, mole_file, input_

    if isinstance(input_, str):
        if input_.endswith(".mol"):
            input_ = pathlib.Path(input_)
        elif count_digits_in_string(input_) > 10 and input_.count(" ") > 10: # alot of numbers indicative of mole file
            try:
                _rdkit_molecule = Chem.MolFromMolBlock(input_)
                smiles = Chem.MolToSmiles(_rdkit_molecule)
                return smiles, input_, _rdkit_molecule
            except Exception as e:
                pass

        else:
            try:
                mol = Chem.MolFromSmiles(input_)
                mole_file = Chem.MolToMolBlock(mol)
                return input_, mole_file, mol
            except Exception as e:
                pass

    if isinstance(input_, pathlib.Path):
        input_ = input_.resolve()
        if not input_.exists():
            raise ValueError(f"Invalid file path. {input_}")

        with open(input_, "r") as f:
            mole_file = f.read()

        _rdkit_molecule = Chem.MolFromMolBlock(mole_file)
        mole_file = Chem.MolToMolBlock(_rdkit_molecule)
        smiles = Chem.MolToSmiles(_rdkit_molecule)
        return smiles, mole_file, _rdkit_molecule

    raise ValueError("'input_' not recognized type. Please provide a 'smiles' or 'mole_file'.")


class Molecule:

    def __init__(self,
                 input_: str | pathlib.Path | Chem.Mol,
                 label: str = None,
                 ):
        """
        Parameters
        ----------
        input_: str
            There are multiple accepted inputs:
            SMILES string
            mole_file: file path to mole file or mole file as string
            rdkit molecule
        label: str
            label of molecule
        """
        smiles, mole_file, _rdkit_molecule = _process_molecule_inputs(input_)
        self.label = label if label is not None else smiles
        self.smiles = smiles
        self._rdkit_molecule = _rdkit_molecule

        # parse mole file
        atom_symbols, atom_coordinates, bond_block, file_version, s_block = parse_mole_file(mole_file)
        self.coordinates = atom_coordinates.T   # [2,N] or [3, N] atoms coordinates are linked to this array (updates in ATOM class effect this)
        self.atoms: list[Atom] = self._add_atoms(atom_symbols, s_block)
        self.bonds: list[Bond] = self._add_bonds(bond_block)
        self.file_version: str = file_version

        # get rings
        self.rings = self._add_rings()

        self.objects = []  # parenthesis
        # get sblock
        # if  self._add_parenthesis(s_block)
        #     pass
        if STYLE_TEMPLATE.auto_rotate:
            self.coordinates = math_points.find_min_bbox_rotation_vector(self.coordinates.T).T
        if STYLE_TEMPLATE.auto_center:
            self.coordinates = math_points.transform_points(
                points=self.coordinates,
                move=-math_points.get_bounding_box_center(self.coordinates)
            )

    def __repr__(self) -> str:
        text = ""
        if self.label is not None:
            text += self.label + " || "
        text += f"# atoms: {self.number_atoms}, # bonds: {self.number_bonds}"
        return text

    @property
    def number_atoms(self) -> int:
        return len(self.atoms)

    @property
    def number_bonds(self) -> int:
        return len(self.bonds)

    @property
    def is_3D(self) -> bool:
        return self.coordinates.shape[0] == 3

    @property
    def atom_highlights(self) -> bool:
        return any([atom.highlight.show for atom in self.atoms])

    @property
    def bond_highlights(self) -> bool:
        return any([bond.highlight.show for bond in self.bonds])

    @property
    def ring_highlights(self) -> bool:
        return any([ring.highlight.show for ring in self.rings])

    @property
    def has_highlights(self) -> bool:
        return any([self.atom_highlights, self.bond_highlights])

    @property
    def center(self) -> np.ndarray:
        """ center of bounding box of molecule """
        return math_points.get_bounding_box_center(self.coordinates)

    @property
    def bounding_box(self) -> np.ndarray:
        return math_points.get_bounding_box(self.coordinates)

    def bond_in_ring(self, bond: Bond) -> list[int]:
        """ returns ring ids """
        rings = []
        for r in self.rings:
            hits = 0
            for a_ids in r.atom_ids:
                atom = self.atoms[a_ids]
                atom._get_bonds()
                if any(b.id_ == bond.id_ for b in atom._bonds):
                    hits += 1
            if hits > 1:
                rings.append(r.id_)
        return rings

    def _add_atoms(self, atom_symbols: list[str], sblock: dict[str, dict]) -> list[Atom]:
        atoms = [Atom(symbol=symbol, id_=i, parent=self) for i, symbol in enumerate(atom_symbols)]

        if 'CHG' in sblock:
            for i, v in sblock['CHG'].items():
                atoms[i-1].charge = v  # i-1 since python start a zero and mol file starts at 1
        if 'RAD' in sblock:
            for i, v in sblock['RAD'].items():
                atoms[i-1].radical = True # i-1 since python start a zero and mol file starts at 1
        return atoms

    def _add_bonds(self, bond_block: np.ndarray) -> list[Bond]:
        bonds = []
        for i, row in enumerate(bond_block):
            bonds.append(
                Bond(
                    atom1_id=row[0]-1, # -1 is to start counting at 0 instead of 1
                    atom2_id=row[1]-1, # -1 is to start counting at 0 instead of 1
                    bond_type=row[2],
                    id_=i,
                    stereo_chem=row[3],
                    parent=self
                )
            )

        return bonds

    def _add_rings(self) -> list[Ring]:
        ring_list = [[i for i in list(ring)] for ring in Chem.GetSymmSSSR(self._rdkit_molecule)]
        aromatic = [self._rdkit_molecule.GetAtomWithIdx(ring[0]).GetIsAromatic() for ring in ring_list]
        return [Ring(np.array(ring_list[i]), i, self, aromatic[i]) for i in range(len(ring_list))]
