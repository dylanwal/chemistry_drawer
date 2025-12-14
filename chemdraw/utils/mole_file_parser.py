import enum

import numpy as np

from chemdraw.errors import MoleParsingError


def parse_mole_file(mole_file: str) -> tuple[list[str], np.ndarray, np.ndarray, str, dict[str, dict]]:
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
    Parse mole file.py    Currently only supports v2000.  
    Parameters    ----------    file: str        mole file  
    Returns    -------    tuple:        first row: dict  
        atom_block: list[list]  
        bond_block: list[list]  
    """    # separate and clean
    file_list = file.split("\n")
    file_list = _clean_file_list(file_list)

    # first row
    first_row = _parse_first_row(file_list.pop(0))

    # atom block
    atom_block = _split_atom_block(file_list[:first_row["number_atoms"]])

    # bond block
    bond_block = _split_bond_block(file_list[first_row["number_atoms"]:first_row["number_atoms"] + first_row["number_bonds"]])

    # double checks for parse
    if first_row["number_atoms"] != len(atom_block):
        raise MoleParsingError(f"Number of atoms parsed does not match first row atom count. "  
                               f"(first row: {first_row['ring_size']}, parsed: {len(atom_block)})")
    if first_row["number_bonds"] != len(bond_block):
        raise MoleParsingError("Number of bonds parsed does not match first row bond count. "  
                               f"(first row: {first_row['number_bonds']}, parsed: {len(bond_block)})")

    # s group
    s_group = file_list[first_row["number_atoms"] + first_row["number_bonds"]:]

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


def _split_atom_block(block: list[str]) -> list[list[str]]:
    return [[row[0:10].strip(), row[10:20].strip(), row[20:30].strip(), row[30:33].strip(), row[33:36].strip(), row[36:39].strip(), row[39:42].strip(), row[42:45].strip(), row[45:48].strip(), row[48:51].strip(), row[51:54].strip(), row[54:57].strip(), row[57:60].strip(), row[60:63].strip(),row[63:66].strip(), row[66:69].strip()] for row in block]


def _split_bond_block(block: list[str]) -> list[list[str]]:
    """[first_atom_index, second_atom_index, bond_type, stereochemistry]"""
    return [[row[0:3].strip(), row[3:6].strip(), row[6:9].strip(), row[9:12].strip()] for row in block]


def _clean_file_list(file_list: list[str]) -> list[str]:
    for i in range(len(file_list)):
        if "V2000" in file_list[i]:
            return file_list[i:]

    raise MoleParsingError("First row not found. (looking for 'V2000')")


def _get_s_block(s_block: list[str]) -> dict[str, dict]:
    rows: dict[str, dict] = dict()
    for i in range(len(s_block)):
        try:
            line = s_block.pop(0)
        except IndexError:
            break

        if "END" in line:
            break
        if "CHG" in line:
            line_split = line.split()
            dict_ = dict()
            line_split = line_split[2:] # remove "M" "CHG"
            num_atoms = int(line_split.pop(0))
            for _ in range(num_atoms):
                atom_id = int(line_split.pop(0))
                charge = int(line_split.pop(0))
                dict_[atom_id] = charge

            rows["CHG"] = dict_
        if "RAD" in line:
            line_split = line.split()
            dict_ = dict()
            line_split = line_split[2:] # remove "M" "RAD"
            num_atoms = int(line_split.pop(0))
            for _ in range(num_atoms):
                atom_id = int(line_split.pop(0))
                charge = int(line_split.pop(0))
                dict_[atom_id] = charge

            rows["RAD"] = dict_

    return rows


def _get_s_block_attr(s_block: list[str]) -> dict:
    out = dict()

    for i, line in enumerate(s_block):
        if "END" in line or "STY" in line:
            del s_block[:i - 1]
            break

        # if "SCN" in line:
        #     out["connectivity"] = SgroupConnectivity[line.split()[4]]
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
