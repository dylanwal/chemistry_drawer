
from chemdraw.config.style_template import STYLE_TEMPLATE
from chemdraw.objects.molecule import Molecule
from chemdraw.drawers.two_d.primitives_for_drawing import DrawingContainer, Text



def draw_ring_numbers(container: DrawingContainer, mol: Molecule) -> DrawingContainer:
    if not STYLE_TEMPLATE.ring_numbers_show:
        return container

    for ring in mol.rings:
        x = ring.center[0] + STYLE_TEMPLATE.ring_numbers_offset_x
        y = ring.center[1] + STYLE_TEMPLATE.ring_numbers_offset_y

        container.add_objects(
            Text(
                x=x,
                y=y,
                symbol=str(ring.label),
                color=STYLE_TEMPLATE.ring_numbers_font_color,
                font=STYLE_TEMPLATE.ring_numbers_font_family,
                size=STYLE_TEMPLATE.ring_numbers_font_size,
                bold=STYLE_TEMPLATE.ring_numbers_font_bold,
            )
        )

    return container

