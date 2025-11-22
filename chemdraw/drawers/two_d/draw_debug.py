import numpy as np

from chemdraw.config.style_template import STYLE_TEMPLATE
from chemdraw.objects.molecule import Molecule
from chemdraw.drawers.two_d.primitives_for_drawing import DrawingContainer, Dot, Arrow, Line


def draw_debug(container: DrawingContainer, mol: Molecule) -> DrawingContainer:
    if not STYLE_TEMPLATE.debug:
        return container

    if STYLE_TEMPLATE.debug_show_molecule:
        draw_molecule_center(container, mol)
    if STYLE_TEMPLATE.debug_show_bond_vector:
        draw_bond_vector(container, mol)
    if STYLE_TEMPLATE.debug_show_bond_perpendicular:
        draw_bond_perpendicular(container, mol)
    if STYLE_TEMPLATE.debug_show_atom_vector:
        draw_atom_vector(container, mol)

    return container


def draw_molecule_center(container: DrawingContainer, mol: Molecule):
    d = Dot(
        x=mol.center[0],
        y=mol.center[1],
        color=STYLE_TEMPLATE.debug_molecule_color,
        size=STYLE_TEMPLATE.debug_molecule_size,
    )
    container.add_objects(d)
    b = Line(
        x=np.append(mol.bounding_box[0], mol.bounding_box[0][0]),
        y=np.append(mol.bounding_box[1], mol.bounding_box[1][0]),
        color=STYLE_TEMPLATE.debug_molecule_color,
        width=STYLE_TEMPLATE.debug_molecule_line_width,
        dash=STYLE_TEMPLATE.debug_molecule_dash,
    )
    container.add_objects(b)


def draw_bond_vector(container: DrawingContainer, mol: Molecule):
    for bond in mol.bonds:
        a = Arrow(
            x=np.array([bond.center[0], bond.center[0] + bond.vector[0]* STYLE_TEMPLATE.debug_bond_vector_length]),
            y=np.array([bond.center[1], bond.center[1] + bond.vector[1]* STYLE_TEMPLATE.debug_bond_vector_length]),
            color=STYLE_TEMPLATE.debug_bond_vector_color,
            line_width=STYLE_TEMPLATE.debug_bond_vector_line_width,
            head_width=STYLE_TEMPLATE.debug_bond_vector_head_width,
            head_height=STYLE_TEMPLATE.debug_bond_vector_head_height,
            dash=STYLE_TEMPLATE.debug_bond_vector_dash,
            style=STYLE_TEMPLATE.debug_bond_vector_style
        )
        container.add_objects(a)


def draw_bond_perpendicular(container: DrawingContainer, mol: Molecule):
    for bond in mol.bonds:
        a = Arrow(
            x=np.array([bond.center[0], bond.center[0] + bond.perpendicular[0] * STYLE_TEMPLATE.debug_bond_vector_length]),
            y=np.array([bond.center[1], bond.center[1] + bond.perpendicular[1] * STYLE_TEMPLATE.debug_bond_vector_length]) ,
            color=STYLE_TEMPLATE.debug_bond_vector_perp_color,
            line_width=STYLE_TEMPLATE.debug_bond_vector_line_width,
            head_width=STYLE_TEMPLATE.debug_bond_vector_head_width,
            head_height=STYLE_TEMPLATE.debug_bond_vector_head_height,
            dash=STYLE_TEMPLATE.debug_bond_vector_dash,
            style=STYLE_TEMPLATE.debug_bond_vector_style
        )
        container.add_objects(a)


def draw_atom_vector(container: DrawingContainer, mol: Molecule):
    for atom in mol.atoms:
        a = Arrow(
            x=np.array([atom.coordinates[0], atom.coordinates[0] + atom.vector()[0] * STYLE_TEMPLATE.debug_atom_vector_length]),
            y=np.array([atom.coordinates[1], atom.coordinates[1] + atom.vector()[1] * STYLE_TEMPLATE.debug_atom_vector_length]) ,
            color=STYLE_TEMPLATE.debug_atom_vector_color,
            line_width=STYLE_TEMPLATE.debug_atom_vector_line_width,
            head_width=STYLE_TEMPLATE.debug_atom_vector_head_width,
            head_height=STYLE_TEMPLATE.debug_atom_vector_head_height,
            dash=STYLE_TEMPLATE.debug_atom_vector_dash,
            style=STYLE_TEMPLATE.debug_atom_vector_style
        )
        container.add_objects(a)


# def _add_parenthesis(fig: go.Figure, parenthesis: list[Parenthesis]) -> go.Figure:
#     for parenthesis in parenthesis:
#         fig.add_annotation(
#             x=parenthesis.coordinates[0] + parenthesis.vector[0]*.3,
#             y=parenthesis.coordinates[1] + parenthesis.vector[1]*.3,
#             ax=parenthesis.coordinates[0],
#             ay=parenthesis.coordinates[1],
#             xref='x',
#             yref='y',
#             axref='x',
#             ayref='y',
#             showarrow=True,
#             arrowhead=3,
#             arrowsize=1,
#             arrowwidth=1,
#             arrowcolor="cyan"
#         )
#
#     return fig
