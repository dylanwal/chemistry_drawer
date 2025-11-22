
from chemdraw.config.style_template import STYLE_TEMPLATE
from chemdraw.objects.molecule import Molecule

from chemdraw.drawers.two_d.primitives_for_drawing import DrawingContainer, Text


def draw_atom_numbers(container: DrawingContainer, mol: Molecule):
    if not STYLE_TEMPLATE.atom_numbers_show:
        return

    alignment = STYLE_TEMPLATE.atom_alignment
    offset = STYLE_TEMPLATE.atom_numbers_offset
    for atom in mol.atoms:
        if alignment == "left":
            x = atom.coordinates[0] + offset
            y = atom.coordinates[1]
        elif alignment == "right":
            x = atom.coordinates[0] - offset
            y = atom.coordinates[1]
        elif alignment == "top":
            x = atom.coordinates[0]
            y = atom.coordinates[1] + offset
        elif alignment == "bottom":
            x = atom.coordinates[0]
            y = atom.coordinates[1] - offset
        else:
            # best
            x = atom.coordinates[0] + atom.vector()[0] * offset
            y = atom.coordinates[1] + atom.vector()[1] * offset


        container.add_objects(
            Text(
                x=x,
                y=y,
                symbol=str(atom.label),
                color=STYLE_TEMPLATE.atom_numbers_font_color,
                font=STYLE_TEMPLATE.atom_numbers_font_family,
                size=STYLE_TEMPLATE.atom_numbers_font_size,
                bold=STYLE_TEMPLATE.atom_numbers_font_bold,
            )
        )
