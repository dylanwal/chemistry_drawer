
import numpy as np
import plotly.graph_objs as go

from chemdraw.objects.atoms import Atom
from chemdraw.objects.bonds import Bond


class ConfigDrawerHighlights:
    show_atoms = True
    show_bonds = True
    highlight_bonds_between_atoms = True
    highlight_atoms_on_bonds = True
    atom_color = "rgba(255,0,0,0.5)"
    bond_color = "rgba(255,0,0,0.5)"
    atom_width = 30
    bond_width = 30
    scatter_kwargs = dict(hoverinfo="skip", cliponaxis=False)

    def __repr__(self):
        return f"show atoms: {self.show_atoms}, show bonds: {self.show_bonds}"


def draw_highlights(fig: go.Figure, config: ConfigDrawerHighlights, atoms: list[Atom], bonds: list[Bond])\
     -> go.Figure:
    if not atoms[0].parent.has_highlights:
        return fig

    if config.show_atoms:
        fig = _add_highlight_to_atoms(fig, config, atoms)

    if config.show_bonds:
        fig = _add_highlight_to_bonds(fig, config, bonds)

    return fig


def _add_highlight_to_atoms(fig: go.Figure, config: ConfigDrawerHighlights, atoms: list[Atom]) -> go.Figure:
    for atom in atoms:
        if atom.highlight or config.highlight_atoms_on_bonds and any([bond.highlight for bond in atom.bonds]):
            x, y = _get_atom_line_length(atom)

            fig.add_trace(go.Scatter(x=x, y=y, mode="lines",
                                     line=dict(color=config.atom_color, width=config.bond_width)))

    return fig


def _get_atom_line_length(atom: Atom) -> tuple[np.ndarray, np.ndarray]:
    return np.array([atom.position[0], atom.position[0]+0.1]), np.array([atom.position[1], atom.position[1]])


def _add_highlight_to_bonds(fig: go.Figure, config: ConfigDrawerHighlights, bonds: list[Bond]) -> go.Figure:
    for bond in bonds:
        if bond.highlight or config.highlight_bonds_between_atoms and all([atom.highlight for atom in bond.atoms]):
            fig.add_trace(go.Scatter(x=bond.x, y=bond.y, mode="lines",
                                     line=dict(color=config.atom_color, width=config.bond_width, shape="spline")))

    return fig
