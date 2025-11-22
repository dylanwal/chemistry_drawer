
from chemdraw.config.style_template import STYLE_TEMPLATE
from chemdraw.objects.molecule import Molecule

from chemdraw.drawers.two_d.primitives_for_drawing import DrawingContainer, Text


def draw_bond_numbers(container: DrawingContainer, mol: Molecule):
    if not STYLE_TEMPLATE.bond_numbers_show:
        return

    alignment = STYLE_TEMPLATE.bond_alignment
    offset = STYLE_TEMPLATE.bond_numbers_offset
    for bond in mol.bonds:
        if alignment == "left":
            x = bond.center[0] + offset
            y = bond.center[1]
        elif alignment == "right":
            x = bond.center[0] - offset
            y = bond.center[1]
        elif alignment == "top":
            x = bond.center[0]
            y = bond.center[1] + offset
        elif alignment == "bottom":
            x = bond.center[0]
            y = bond.center[1] - offset
        else:
            # best
            x = bond.center[0] + bond.perpendicular[0] * offset
            y = bond.center[1] + bond.perpendicular[1] * offset


        container.add_objects(
            Text(
                x=x,
                y=y,
                symbol=str(bond.label),
                color=STYLE_TEMPLATE.bond_numbers_font_color,
                font=STYLE_TEMPLATE.bond_numbers_font_family,
                size=STYLE_TEMPLATE.bond_numbers_font_size,
                bold=STYLE_TEMPLATE.bond_numbers_font_bold,
            )
        )
