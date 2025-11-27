import numpy as np

from chemdraw.config.style_template import STYLE_TEMPLATE
from chemdraw.objects.molecule import Molecule
from chemdraw.drawers.two_d.draw_bonds import determine_if_show_atom_label
from chemdraw.drawers.two_d.primitives_for_drawing import DrawingContainer, Text


def draw_atom_numbers(container: DrawingContainer, mol: Molecule):
    if not STYLE_TEMPLATE.atom_numbers_show:
        return

    new_container = DrawingContainer("atom_numbers")
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
            if determine_if_show_atom_label(atom):
                multiplier = 1.6
            else:
                multiplier = 1

            x = atom.coordinates[0] + atom.vector()[0] * offset*multiplier
            y = atom.coordinates[1] + atom.vector()[1] * offset*multiplier
            if STYLE_TEMPLATE.atom_numbers_box_type == "bottom_center":
                x, y = text_box_adjustment_bottom_center(
                    x,
                    y,
                    STYLE_TEMPLATE.atom_numbers_box_x,
                    STYLE_TEMPLATE.atom_numbers_box_y,
                    atom.vector()
                )

        new_container.add_objects(
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
        # y = y + box_height/2
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