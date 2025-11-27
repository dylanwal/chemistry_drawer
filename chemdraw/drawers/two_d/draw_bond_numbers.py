import numpy as np

from chemdraw.config.style_template import STYLE_TEMPLATE
from chemdraw.objects.molecule import Molecule
from chemdraw.objects.bonds import BondType

from chemdraw.drawers.two_d.primitives_for_drawing import DrawingContainer, Text


def draw_bond_numbers(container: DrawingContainer, mol: Molecule):
    if not STYLE_TEMPLATE.bond_numbers_show:
        return

    new_container = DrawingContainer("bond_numbers")
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
            if bond.type_ == BondType.triple:
                multiplier = 1.3
            elif bond.type_ == BondType.double:
                multiplier = 1.3
            else:
                multiplier = 1
            x = bond.center[0] + bond.perpendicular[0] * offset
            y = bond.center[1] + bond.perpendicular[1] * offset
            if STYLE_TEMPLATE.bond_numbers_box_type == "bottom_center":
                x, y = text_box_adjustment_bottom_center(
                    x,
                    y,
                    STYLE_TEMPLATE.bond_numbers_box_x * len(str(bond.label)) * multiplier,
                    STYLE_TEMPLATE.bond_numbers_box_y * multiplier,
                    bond.perpendicular,
                )


        new_container.add_objects(
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

    container.containers.append(new_container)


def text_box_adjustment_bottom_center(
        x: float,
        y: float,
        box_width: float,
        box_height: float,
        vector: np.ndarray,
) -> tuple[float, float]:
    # adjust to text box location (text box origin is bottom center)
    if vector[0] > 0.45 and 0 < vector[1]:
        # pointing right 30-60 up
        x = x + box_width/2
        y = y - box_height/2
    elif vector[0] > 0.45 and 0 > vector[1]:
        # pointing right 30-60 up
        x = x + box_width/2
        y = y - box_height
    elif -0.5 > vector[0]and 0 < vector[1]:
        # pointing left 30-60
        x = x - box_width/2
    elif -0.5 > vector[0] and 0 > vector[1]:
        # pointing right 30-60 up
        x = x - box_width/2
        y = y - box_height
    elif 0.87 < vector[0]:
        # point right
        x = x + box_width/2
        y = y - box_height/2
    elif 0 > vector[1]:
        # point point down
        # x = x + box_width/2
        y = y - box_height

    return x, y