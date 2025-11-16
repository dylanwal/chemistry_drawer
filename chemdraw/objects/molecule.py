import pathlib

import numpy as np
from rdkit import Chem

from chemdraw.config.style_template import style_template
from chemdraw.utils.mole_file_parser import parse_mole_file, Sgroup
from chemdraw.objects.atoms import Atom
from chemdraw.objects.bonds import Bond, BOND_COUNT
from chemdraw.objects.rings import Ring
from chemdraw.utils.math_points import set_largest_axis

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
        self.coordinates = atom_coordinates   # [2,N] or [3, N] atoms coordinates are linked to this array (updates in ATOM class effect this)
        self.atoms: list[Atom] = self._add_atoms(atom_symbols)
        self.bonds: list[Bond] = self._add_bonds(bond_block)
        self.file_version: str = file_version

        # get rings
        self.rings = self._add_rings()

        self.objects = []  # parenthesis
        # get sblock
        # if  self._add_parenthesis(s_block)
        #     pass
        if style_template.auto_rotate:
            self.coordinates = set_largest_axis(self.coordinates)

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

    def _add_atoms(self, atom_symbols: list[str]) -> list[Atom]:
        atoms = []
        for i, symbol in enumerate(atom_symbols):
            atoms.append(
                Atom(symbol=symbol, id_=i, parent=self)  # TODO: add radical and charge to parser
            )
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
        return [Ring(ring_list[i], i, self, aromatic[i]) for i in range(len(ring_list))]
