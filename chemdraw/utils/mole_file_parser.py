import enum

import numpy as np

from chemdraw.errors import MoleParsingError


def parse_mole_file(mole_file: str) -> tuple[list[str], np.ndarray, np.ndarray, str, dict]:
    first_row, atom_block, bond_block, s_block = _parse_mole_file_main(mole_file)
    atom_symbols, atom_coordinates = _get_atoms(atom_block)
    bond_block = np.array(bond_block, dtype="int16")
    s_group = _get_s_block(s_block)

    return atom_symbols, atom_coordinates, bond_block, first_row["file_version"], s_group


def _get_atoms(atom_block: list[list]) -> tuple[list[str], np.ndarray]:
    atom_coordinates = np.empty((len(atom_block), 2), dtype="float64")
    atom_symbols = []
    for i, row in enumerate(atom_block):
        atom_coordinates[i] = (row[0], row[1])
        atom_symbols.append(row[3])

    return atom_symbols, atom_coordinates


def _parse_mole_file_main(file: str) -> tuple[dict, list[list], list[list], list[str]]:
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
    if first_row["number_atoms"] != len(atom_block):
        raise MoleParsingError(f"Number of atoms parsed does not match first row atom count. "
                               f"(first row: {first_row['ring_size']}, parsed: {len(atom_block)})")
    if first_row["number_bonds"] != len(bond_block):
        raise MoleParsingError("Number of bonds parsed does not match first row bond count. "
                               f"(first row: {first_row['number_bonds']}, parsed: {len(bond_block)})")

    # s group
    s_group = file_list[atom_block_last_index + 2 + bond_block_last_index:]

    return first_row, atom_block, bond_block, s_group


def _parse_first_row(first_row: str) -> dict:
    if len(first_row) != 39:
        raise MoleParsingError("First row not correct.", str(first_row))

    return {
        "number_atoms": int(first_row[0:3]),
        "number_bonds": int(first_row[3:6]),
        "chiral": bool(first_row[12:15]),
        "file_version": first_row[34:39]
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


class Sgroup(enum.Enum):
    SUP = 1  # superatom
    MUL = 2  # multiple group
    SRU = 3  # structural repeat unit
    MON = 4  # monomer
    MER = 5  # mer type
    GRA = 6  # graft
    COM = 7  # component
    MIX = 8  # mixture
    FOR = 9  # formulation
    DAT = 10  # data
    ANY = 11  # any polymer
    GEN = 12  # generic


class SgroupConnectivity(enum.Enum):
    HH = 1  # head-to-head
    HT = 2  # head-to-tail
    EU = 3  # unknown


def _get_s_block(s_block: list[str]) -> dict:
    out = dict()
    for i in range(len(s_block)):
        try:
            line = s_block.pop(0)
        except IndexError:
            break

        if "END" in line:
            break
        if "STY" in line:
            line = line.split()
            id_ = int(line[3])
            type_ = Sgroup[line[4].strip()]
            attr_ = _get_s_block_attr(s_block)
            out[id_] = dict(type_=type_) | attr_

    return out


def _get_s_block_attr(s_block: list[str]) -> dict:
    out = dict()

    for i, line in enumerate(s_block):
        if "END" in line or "STY" in line:
            del s_block[:i - 1]
            break

        if "SCN" in line:
            out["connectivity"] = SgroupConnectivity[line.split()[4]]
        elif "SMT" in line:
            out["label"] = line.split()[3]
        elif "SAL" in line:
            out["atoms"] = [int(ii)-1 for ii in line.split()[4:]]  # -1 is to start counting at 0
        elif "SBL" in line:
            out["bonds"] = [int(ii)-1 for ii in line.split()[4:]]  # -1 is to start counting at 0
        elif "SDI" in line:
            if "position" in out:
                out["position"] += [float(ii) for ii in line.split()[4:]]
            else:
                out["position"] = [float(ii) for ii in line.split()[4:]]

    return out
