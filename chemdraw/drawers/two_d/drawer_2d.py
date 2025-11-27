from typing import Sequence


from chemdraw.objects.molecule import Molecule
from chemdraw.config.style_template import STYLE_TEMPLATE
import chemdraw.drawers.two_d.draw_debug as draw_debug
import chemdraw.drawers.two_d.draw_label as draw_label
import chemdraw.drawers.two_d.draw_atoms as draw_atoms
import chemdraw.drawers.two_d.draw_bonds as draw_bonds
import chemdraw.drawers.two_d.draw_atom_numbers as draw_atom_numbers
import chemdraw.drawers.two_d.draw_bond_numbers as draw_bond_numbers
import chemdraw.drawers.two_d.draw_ring_numbers as draw_ring_numbers
# import chemdraw.drawers.draw_parenthesis as draw_parenthesis
import chemdraw.drawers.two_d.draw_highlights as draw_highlights
# import chemdraw.drawers.draw_ring_highlights as draw_ring_highlights

from chemdraw.drawers.two_d.primitives_for_drawing import DrawingContainer, DrawingContainerGrid


DRAWERS = {
        "bonds": draw_bonds.draw_bonds,
        "atoms": draw_atoms.draw_atoms,
        "label": draw_label.draw_label,
        "debug": draw_debug.draw_debug,
        "atom_numbers": draw_atom_numbers.draw_atom_numbers,
        "bond_numbers": draw_bond_numbers.draw_bond_numbers,
        "ring_numbers": draw_ring_numbers.draw_ring_numbers,
        "highlights": draw_highlights.draw_highlights,
        # "ring_highlights": draw_ring_highlights.draw_ring_highlight,
        # "parenthesis": draw_parenthesis.draw_parenthesis,
    }

### drawing (first in list is drawn at the bottom)
# 'label' should be last as it needs the molecule built to know where it should be.
# self.draw_order = ["ring_highlights", "highlights", "parenthesis", ]
DRAW_ORDER = ["highlights", "bonds", "atoms", "debug", "bond_numbers", "atom_numbers", "ring_numbers", "label"]


def draw(molecule: str | Molecule):
    """
    Return a figure object for a single molecule.
    Figure object depends on plotting package used.

    Parameters
    ----------
    molecule: str | Molecule
        str = SMILES string

    Returns
    -------
    Plotly: go.Figure
    Matplotlib: plt.subplots

    """
    if isinstance(molecule, str):
        molecule = Molecule(molecule, label=molecule)

    container = DrawingContainer("base")
    for key in DRAW_ORDER:
        drawer = DRAWERS[key]
        drawer(container, molecule)

    container = container.prepare_for_drawing()
    plotter = STYLE_TEMPLATE.get_plotter()

    return plotter(container)


def draw_grid(molecules: Sequence[str] | Sequence[Molecule], shape: Sequence[int] | None = None):
    if isinstance(molecules[0], str):
        molecules = (Molecule(m) for m in molecules)

    container_grid = DrawingContainerGrid(shape)
    for m in molecules:
        container = DrawingContainer("base")
        for key in DRAW_ORDER:
            drawer = DRAWERS[key]
            drawer(container, m)
        container_grid.add(container)

    container_grid = container_grid.prepare_for_drawing()
    plotter = STYLE_TEMPLATE.get_plotter()

    return plotter(container_grid)