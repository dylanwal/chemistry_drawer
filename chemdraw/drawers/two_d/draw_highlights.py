
from chemdraw.config.style_template import STYLE_TEMPLATE
from chemdraw.objects.molecule import Molecule

from chemdraw.drawers.two_d.primitives_for_drawing import DrawingContainer, Line, Dot


def draw_highlights(container: DrawingContainer, mol: Molecule) -> DrawingContainer:
    if not mol.has_highlights:
        return container

    new_container = DrawingContainer()
    add_highlight_to_bonds(new_container, mol)
    add_highlight_to_atoms(new_container, mol)
    container.containers.insert(0, new_container) # make it the bottom layer

    return container


def add_highlight_to_atoms(container: DrawingContainer, mol: Molecule):
    for atom in mol.atoms:
        if atom.highlight.show:
            container.add_objects(
                Dot(
                    x=atom.coordinates[0],
                    y=atom.coordinates[1],
                    color=atom.highlight.color or STYLE_TEMPLATE.highlight_atom_color,
                    size=atom.highlight.size or STYLE_TEMPLATE.highlight_atom_size
                )
            )


def add_highlight_to_bonds(container: DrawingContainer, mol: Molecule):
    for bond in mol.bonds:
        if bond.highlight.show:
            container.add_objects(
                Line(
                    x=bond.coordinates[0],
                    y=bond.coordinates[1],
                    color=bond.highlight.color or STYLE_TEMPLATE.highlight_bond_color,
                    width=bond.highlight.size or STYLE_TEMPLATE.highlight_bond_size
                )
            )

