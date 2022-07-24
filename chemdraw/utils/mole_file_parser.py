import numpy as np

from chemdraw.errors import MoleParsingError


def parse_mole_file(mole_file: str) -> tuple[list[str], np.ndarray, np.ndarray, str]:
    first_row, atom_block, bond_block = _parse_mole_file_main(mole_file)
    atom_symbols, atom_coordinates = _get_atoms(atom_block)
    bond_block = np.array(bond_block, dtype="int16")
    return atom_symbols, atom_coordinates, bond_block, first_row["file_version"]


def _get_atoms(atom_block: list[list]) -> tuple[list[str], np.ndarray]:
    atom_coordinates = np.empty((len(atom_block), 2), dtype="float64")
    atom_symbols = []
    for i, row in enumerate(atom_block):
        atom_coordinates[i] = (row[0], row[1])
        atom_symbols.append(row[3])

    return atom_symbols, atom_coordinates


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
    """[first_atom_index, second_atom_index, bond_type, stereochemistry]"""
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
