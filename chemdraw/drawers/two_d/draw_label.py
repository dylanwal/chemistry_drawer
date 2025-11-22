import numpy as np
import math

from chemdraw.config.style_template import STYLE_TEMPLATE
from chemdraw.objects.molecule import Molecule

from chemdraw.drawers.two_d.primitives_for_drawing import DrawingContainer, Text

def draw_label(container: DrawingContainer, mol: Molecule) -> DrawingContainer:
    label = mol.label
    if not STYLE_TEMPLATE.atom_numbers_show or label is None:
        return container

    new_container = DrawingContainer()
    new_container.containers.append(container)

    if STYLE_TEMPLATE.label_auto_wrap:
        number_lines = math.ceil(len(label)/ STYLE_TEMPLATE.label_auto_wrap_length)
    else:
        number_lines = 1

    bounding_box = container.bounding_box()
    x = float(np.mean(bounding_box[0,:])) # center it
    if STYLE_TEMPLATE.label_location == "top":
        y = np.max(bounding_box[1,:]) + STYLE_TEMPLATE.label_pad + number_lines * STYLE_TEMPLATE.label_font_size/100 * 0.5
    elif STYLE_TEMPLATE.label_location == "bottom":
        y = np.min(bounding_box[1,:]) - STYLE_TEMPLATE.label_pad - number_lines * STYLE_TEMPLATE.label_font_size/100 * 0.5
    else:
        raise ValueError("Invalid label location")

    text = []
    for i in range(number_lines):
        block = label[STYLE_TEMPLATE.label_auto_wrap_length * i: STYLE_TEMPLATE.label_auto_wrap_length * (1+i)]
        text.append(block)
    label = f"{STYLE_TEMPLATE.get_text_break()}".join(text)

    container.add_objects(
            Text(
                x=x,
                y=y,
                symbol=label,
                color=STYLE_TEMPLATE.label_font_color,
                font=STYLE_TEMPLATE.label_font_family,
                size=STYLE_TEMPLATE.label_font_size,
                bold=STYLE_TEMPLATE.label_font_bold,
            )
        )
    return new_container
