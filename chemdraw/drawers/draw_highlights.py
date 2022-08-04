
import numpy as np
import plotly.graph_objs as go

from chemdraw.drawers.general_classes import Highlight
from chemdraw.objects.atoms import Atom
from chemdraw.objects.bonds import Bond


class ConfigDrawerHighlights:
    def __init__(self, parent):
        self.parent = parent

        self.atoms = Highlight(parent, show=True, color="rgb(127,177,235)", size=40)
        self.bonds = Highlight(parent, show=True, color="rgb(127,177,235)", size=20)
        self.highlight_bonds_between_atoms = False
        self.highlight_atoms_on_bonds = False
        self.scatter_kwargs = dict(hoverinfo="skip", cliponaxis=False)

    def __repr__(self):
        return f"show atoms: {self.atoms.show}, show bonds: {self.bonds.show}"


def draw_highlights(fig: go.Figure, config: ConfigDrawerHighlights, atoms: list[Atom], bonds: list[Bond])\
     -> go.Figure:
    if not atoms[0].parent.has_highlights:
        return fig

    if config.bonds.show:
        fig = _add_highlight_to_bonds(fig, config, bonds)

    if config.atoms.show:
        fig = _add_highlight_to_atoms(fig, config, atoms)

    return fig


def _add_highlight_to_atoms(fig: go.Figure, config: ConfigDrawerHighlights, atoms: list[Atom]) -> go.Figure:
    for atom in atoms:
        if atom.highlight.show or config.highlight_atoms_on_bonds and any([bond.highlight.show for bond in atom.bonds]):
            color = config.atoms.color if atom.highlight.color is None else atom.highlight.color
            size = config.atoms.size if atom.highlight.size is None else atom.highlight.size
            fig.add_trace(go.Scatter(x=[atom.coordinates[0]], y=[atom.coordinates[1]], mode="markers",
                                     marker=dict(color=color, size=size), **config.scatter_kwargs))

    return fig


def _add_highlight_to_bonds(fig: go.Figure, config: ConfigDrawerHighlights, bonds: list[Bond]) -> go.Figure:
    for bond in bonds:
        if bond.highlight.show or \
                (config.highlight_bonds_between_atoms and all([atom.highlight.show for atom in bond.atoms])):
            color = config.bonds.color if bond.highlight.color is None else bond.highlight.color
            width = config.bonds.size if bond.highlight.size is None else bond.highlight.size
            fig.add_trace(go.Scatter(x=bond.x, y=bond.y, mode="lines",
                                     line=dict(color=color, width=width), **config.scatter_kwargs))

    return fig
