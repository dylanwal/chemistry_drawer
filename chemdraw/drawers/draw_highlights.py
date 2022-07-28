
import numpy as np
import plotly.graph_objs as go

from chemdraw.objects.atoms import Atom
from chemdraw.objects.bonds import Bond


class ConfigDrawerHighlights:
    def __init__(self, parent):
        self.parent = parent

        self.show_atoms = True
        self.show_bonds = True
        self.highlight_bonds_between_atoms = False
        self.highlight_atoms_on_bonds = False
        self.atom_color = "rgb(127,177,235)"
        self.bond_color = "rgb(127,177,235)"
        self.atom_size = 40
        self.bond_width = 20
        self.scatter_kwargs = dict(hoverinfo="skip", cliponaxis=False)

    def __repr__(self):
        return f"show atoms: {self.show_atoms}, show bonds: {self.show_bonds}"


def draw_highlights(fig: go.Figure, config: ConfigDrawerHighlights, atoms: list[Atom], bonds: list[Bond])\
     -> go.Figure:
    if not atoms[0].parent.has_highlights:
        return fig

    if config.show_bonds:
        fig = _add_highlight_to_bonds(fig, config, bonds)

    if config.show_atoms:
        fig = _add_highlight_to_atoms(fig, config, atoms)

    return fig


def _add_highlight_to_atoms(fig: go.Figure, config: ConfigDrawerHighlights, atoms: list[Atom]) -> go.Figure:
    for atom in atoms:
        if atom.highlight or config.highlight_atoms_on_bonds and any([bond.highlight for bond in atom.bonds]):
            color = config.atom_color if atom.highlight_color is None else atom.highlight_color
            size = config.atom_size if atom.highlight_size is None else atom.highlight_size
            fig.add_trace(go.Scatter(x=[atom.coordinates[0]], y=[atom.coordinates[1]], mode="markers",
                                     marker=dict(color=color, size=size), **config.scatter_kwargs))

    return fig


def _add_highlight_to_bonds(fig: go.Figure, config: ConfigDrawerHighlights, bonds: list[Bond]) -> go.Figure:
    for bond in bonds:
        if bond.highlight or config.highlight_bonds_between_atoms and all([atom.highlight for atom in bond.atoms]):
            color = config.bond_color if bond.highlight_color is None else bond.highlight_color
            width = config.bond_width if bond.highlight_width is None else bond.highlight_width
            fig.add_trace(go.Scatter(x=bond.x, y=bond.y, mode="lines",
                                     line=dict(color=color, width=width), **config.scatter_kwargs))

    return fig
