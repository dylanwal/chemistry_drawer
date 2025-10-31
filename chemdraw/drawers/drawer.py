
import plotly.graph_objs as go

from chemdraw.objects.molecule import Molecule
from chemdraw.config.style_template import StyleTemplate
import chemdraw.drawers.draw_debug as draw_debug
import chemdraw.drawers.draw_label as draw_label
import chemdraw.drawers.draw_atoms as draw_atoms
import chemdraw.drawers.draw_bonds as draw_bonds
import chemdraw.drawers.draw_atom_numbers as draw_atom_numbers
import chemdraw.drawers.draw_bond_numbers as draw_bond_numbers
import chemdraw.drawers.draw_ring_numbers as draw_ring_numbers
import chemdraw.drawers.draw_parenthesis as draw_parenthesis
import chemdraw.drawers.draw_highlights as draw_highlights
import chemdraw.drawers.draw_ring_highlights as draw_ring_highlights


DRAWERS = {
        "bonds": draw_bonds.draw_bonds,
        "atoms": draw_atoms.draw_atoms,
        "label": draw_label.draw_label,
        "debug": draw_debug.draw_debug,
        "atom_numbers": draw_atom_numbers.draw_atom_numbers,
        "bond_numbers": draw_bond_numbers.draw_bond_numbers,
        "ring_numbers": draw_ring_numbers.draw_ring_numbers,
        "highlights": draw_highlights.draw_highlights,
        "ring_highlights": draw_ring_highlights.draw_ring_highlight,
        "parenthesis": draw_parenthesis.draw_parenthesis,
    }


def draw(molecule: str | Molecule, template: StyleTemplate = None) -> go.Figure:
    if isinstance(molecule, str):
        molecule = Molecule(molecule, label=molecule)

    fig = go.Figure()
    for key in template.draw_order:
        drawer = DRAWERS[key]
        fig = drawer(fig, molecule, template)

    return fig
