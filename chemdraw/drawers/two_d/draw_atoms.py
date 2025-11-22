
from chemdraw.config.style_template import STYLE_TEMPLATE
from chemdraw.objects.molecule import Molecule
from chemdraw.objects.atoms import Atom

from chemdraw.drawers.two_d.primitives_for_drawing import DrawingContainer, Text


def draw_atoms(container: DrawingContainer, mol: Molecule):
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

        container.add_objects(objs)


def draw_atom(atom: Atom) -> Text | None:
    if not STYLE_TEMPLATE.atom_show_carbons and atom.symbol == "C":
        return None  # skip drawing carbons

    # symbol
    symbol, align, direction = _add_hydrogen_text(atom)
    x, y = text_alignment(atom, align)

    # xy[counter, :] = [x, y - config.get_text_y_offset()]

    # add hydrogens that are above or below atom
    # if direction is not None:
    #     hydrogen_symbol = _get_hydrogen_symbol(atom)
    #     if config.font.get_attr("bold", atom.font):
    #         hydrogen_symbol = "<b>" + hydrogen_symbol + "</b>"
    #     symbols.append(hydrogen_symbol)
    #     top_offset = config.font.get_attr("top_offset", atom.font)
    #     if direction == "up":
    #         xy[counter, :] = [atom.coordinates[0], atom.coordinates[1] + top_offset - config.get_text_y_offset()]
    #     else:
    #         xy[counter, :] = [atom.coordinates[0], atom.coordinates[1] - top_offset - config.get_text_y_offset()]

    return Text(x, y, symbol, color=atom.style.color, font=atom.style.family, size=atom.style.size, bold=atom.style.bold)


def _add_hydrogen_text(atom: Atom) -> tuple[str, str, str | None]:
    """ add hydrogen and subscript to atoms"""
    if atom.number_hydrogens() < 1:
        return atom.symbol, "center", None

    vector = atom.vector()
    if abs(vector[0]) > abs(vector[1]) or atom.number_bonds != 2:
        if vector[0] < 0:
            # hydrogen on left side of atom
            return _get_hydrogen_symbol(atom) + atom.symbol, "left", None
        else:
            # hydrogen on right side of atom
            return atom.symbol + _get_hydrogen_symbol(atom), "right", None
    else:
        if vector[1] > 0:
            # hydrogen on top side of atom
            return atom.symbol, "center", "up"
        else:
            # hydrogen on right side of atom
            return atom.symbol, "center", "down"


def _get_hydrogen_symbol(atom: Atom) -> str:
    if atom.number_hydrogens == 0:
        return ""
    elif atom.number_hydrogens == 1:
        return "H"
    return f"H{STYLE_TEMPLATE.make_subscript(str(atom.number_hydrogens()))}"


def text_alignment(atom: Atom, align: str) -> tuple[float, float]:
    offset = STYLE_TEMPLATE.atom_text_x_offset
    if align == "center":
        return atom.coordinates[0], atom.coordinates[1]
    elif align == "left":
        return atom.coordinates[0] - offset, atom.coordinates[1]
    elif align == "right":
        return atom.coordinates[0] + offset, atom.coordinates[1]

    raise RuntimeError("Coding error")

