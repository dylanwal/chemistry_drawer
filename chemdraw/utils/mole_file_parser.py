
import numpy as np

from chemdraw.errors import MoleParsingError
from chemdraw.objects.atoms import Atom
from chemdraw.objects.bonds import Bond


def parse_mole_file(mole_file: str) -> tuple[list[Atom], list[Bond], str]:
    first_row, atom_block, bond_block = _parse_mole_file_main(mole_file)
    atoms = _get_atoms(atom_block)
    bonds = _get_bonds(bond_block)
    _add_bond_atoms(atoms, bonds)
    return atoms, bonds, first_row["file_version"]


def _get_atoms(atom_block: list[list]) -> list[Atom]:
    atoms = []
    for i, row in enumerate(atom_block):
        atoms.append(
            Atom(symbol=row[3], position=np.array((row[0], row[1]), dtype="float64"), id_=i)
        )

    return atoms


def _get_bonds(bond_block: list[list]) -> list[Bond]:
    bond_block = np.array(bond_block, dtype="int16")
    bonds = []
    for i, row in enumerate(bond_block):
        bonds.append(Bond(atom_ids=row[:2]-1, bond_type=row[2], id_=i))  # -1 is to start counting at 0 instead of 1

    return bonds


def _add_bond_atoms(atoms: list[Atom], bonds: list[Bond]):
    for bond in bonds:
        # add atoms to bond
        bond.add_atoms(atoms[bond.atom_ids[0]], atoms[bond.atom_ids[1]])

        # add bonds to atoms
        for atom in bond.atoms:
            atom.add_bond(bond)


def _parse_mole_file_main(file: str) -> tuple[dict, list[list], list[list]]:
    """
    Parse mole file.py
    Currently only supports v2000.

    Parameters
    ----------
    file: str
        mole file

    Returns
    -------
    tuple:
        first row: dict

        atom_block: list[list]

        bond_block: list[list]

    """
    # separate and clean
    file_list = file.split("\n")
    file_list = _clean_file_list(file_list)

    # first row
    first_row = _parse_first_row(file_list.pop(0))

    # atom block
    atom_block_last_index = _get_block_last_index(file_list)
    atom_block = _split_block(file_list[:atom_block_last_index + 1])

    # bond block
    bond_block_last_index = _get_block_last_index(file_list[atom_block_last_index + 1:])
    bond_block = _split_block(file_list[atom_block_last_index + 1:atom_block_last_index + 2 + bond_block_last_index])

    # double checks for parse
    if first_row["ring_size"] != len(atom_block):
        raise MoleParsingError(f"Number of atoms parsed does not match first row atom count. "
                               f"(first row: {first_row['ring_size']}, parsed: {len(atom_block)})")
    if first_row["number_bonds"] != len(bond_block):
        raise MoleParsingError("Number of bonds parsed does not match first row bond count. "
                               f"(first row: {first_row['number_bonds']}, parsed: {len(bond_block)})")

    return first_row, atom_block, bond_block


def _parse_first_row(first_row: str) -> dict:
    first_row = first_row.split()
    if len(first_row) != 11:
        raise MoleParsingError("First row not correct.", str(first_row))

    return {
        "ring_size": int(first_row[0]),
        "number_bonds": int(first_row[1]),
        "chiral": bool(first_row[4]),
        "file_version": first_row[10]
    }


def _split_block(block: list[str]) -> list[list[str]]:
    """[first_atom_index, second_atom_index, bond_type, sterochemistry]"""
    return [row.split() for row in block]


def _clean_file_list(file_list: list[str]) -> list[str]:
    for i in range(len(file_list)):
        if "V2000" in file_list[i]:
            return file_list[i:]

    raise MoleParsingError("First row not found. (looking for 'V2000')")


def _get_block_last_index(file_list: list[str]) -> int:
    row_length = len(file_list[0].split())
    for i, row in enumerate(file_list):
        if len(row.split()) != row_length:
            return i - 1

    raise MoleParsingError("No transition between atom and bond blocks found.")
