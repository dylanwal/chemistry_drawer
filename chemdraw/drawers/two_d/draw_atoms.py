from chemdraw.config.style_template import STYLE_TEMPLATE
from chemdraw.objects.molecule import Molecule
from chemdraw.objects.atoms import Atom
from chemdraw.objects.bonds import BondType

from chemdraw.drawers.two_d.primitives_for_drawing import DrawingContainer, Text


def draw_atoms(container: DrawingContainer, mol: Molecule):
    new_container = DrawingContainer("atoms")
    for atom in mol.atoms:
        if atom._show is False:
            continue

        objs = draw_atom(atom)
        if objs is None:
            continue

        # set style sheet values if not set locally.
        if not isinstance(objs, list):
            objs = [objs]
        for obj in objs:
            if obj.font is None:
                obj.font = STYLE_TEMPLATE.atom_font_family
            if obj.bold is None:
                obj.bold = STYLE_TEMPLATE.atom_font_bold
            if obj.color is None:
                obj.color = STYLE_TEMPLATE.get_atom_color(obj)
            if obj.size is None:
                obj.size = STYLE_TEMPLATE.atom_font_size

        new_container.add_objects(objs)

    container.containers.append(new_container)


def between_two_double_bonds(atom: Atom) -> bool:
    atom._get_bonds()
    if len(atom._bonds) != 2:
        return False
    return all(b.type_ == BondType.double for b in atom._bonds)


def draw_atom(atom: Atom) -> Text | None:
    if (
            not STYLE_TEMPLATE.atom_show_carbons and
            atom.symbol == "C" and
            atom.charge == 0 and
            not atom.radical and
            not between_two_double_bonds(atom)
    ):
        return None  # skip drawing carbons

    # symbol
    symbol = atom.symbol
    charge_offset = 0
    if atom.charge != 0:
        if abs(atom.charge) == 1:
            symbol += STYLE_TEMPLATE.make_superscript(f"{'+' if atom.charge > 0 else '-'}")
            charge_offset += 1
        else:
            symbol += STYLE_TEMPLATE.make_superscript(f"{'+' if atom.charge > 0 else ''}{atom.charge}")
            charge_offset += 2
    if atom.radical:
        symbol += STYLE_TEMPLATE.make_superscript("\u2022")
        charge_offset += 1

    h_text, h_offset, direction = get_hydrogen_data(atom)

    # add hydrogen to text
    if direction is None:
        if h_offset > 0:
            symbol += h_text
        else:
            symbol = h_text + symbol
    else:
        if direction == "up":
            symbol = [h_text, symbol]
        else:  # direction == "down":
            symbol = [symbol, h_text]

    # adjust position to account for charge and hydrogens
    x = atom.coordinates[0] + STYLE_TEMPLATE.atom_global_offset_x
    y = atom.coordinates[1] + STYLE_TEMPLATE.atom_global_offset_y
    x += charge_offset * STYLE_TEMPLATE.atom_charge_offset
    if direction is None:
        x += h_offset * STYLE_TEMPLATE.atom_H_offset_x
    else:
        if direction == "up":
            y -= STYLE_TEMPLATE.atom_H_offset_y
        else:
            y += STYLE_TEMPLATE.atom_H_offset_y

    return Text(x, y, symbol, color=atom.style.color, font=atom.style.family, size=atom.style.size,
                bold=atom.style.bold)


def get_hydrogen_data(atom: Atom) -> tuple[str, int, str | None]:
    """ add hydrogen and subscript to atoms"""
    if atom.number_hydrogens() == 0:
        return "", 0, None

    h_symbol = "H" if atom.number_hydrogens() == 1 else f"H{STYLE_TEMPLATE.make_subscript(str(atom.number_hydrogens()))}"
    offset = 1 if atom.number_hydrogens() == 1 else 1.6  # 0.4 is for the subscript
    vector = atom.vector()
    if abs(vector[0]) > abs(vector[1]) or atom.number_bonds() != 2:
        if vector[0] < 0:
            # hydrogen on left side of atom
            return h_symbol, -offset, None
        else:
            # hydrogen on right side of atom
            return h_symbol, offset, None
    else:
        if vector[1] > 0:
            # hydrogen on top side of atom
            return h_symbol, 0, "up"
        else:
            # hydrogen on right side of atom
            return h_symbol, 0, "down"
