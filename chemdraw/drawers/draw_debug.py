
import plotly.graph_objs as go

from chemdraw.objects.bonds import Bond
from chemdraw.objects.atoms import Atom


class ConfigDrawerDebug:
    _debug = False
    show_center_point = False
    show_bond_vector = False
    show_bond_perpendicular = False
    show_atom_vector = False

    @property
    def debug(self) -> bool:
        """ Turn on all debugging."""
        return self._debug

    @debug.setter
    def debug(self, option: bool):
        self._debug = option
        self.show_center_point = option
        self.show_bond_vector = option
        self.show_bond_perpendicular = option
        self.show_atom_vector = option


def draw_debug(fig: go.Figure, config: ConfigDrawerDebug, atoms: list[Atom], bonds: list[Bond]) -> go.Figure:
    if config.show_center_point:
        fig.add_trace(go.Scatter(x=[0], y=[0], mode="markers", marker=dict(color="red", size=5)))
    if config.show_bond_vector:
        fig = _add_bond_vectors(fig, bonds)
    if config.show_bond_perpendicular:
        fig = _add_bond_perpendicular(fig, bonds)
    if config.show_atom_vector:
        fig = _add_atom_vector(fig, atoms)

    return fig


def _add_bond_vectors(fig: go.Figure, bonds: list[Bond]) -> go.Figure:
    for bond in bonds:
        fig.add_annotation(
            x=bond.center[0] + bond.vector[0],
            y=bond.center[1] + bond.vector[1],
            ax=bond.center[0],
            ay=bond.center[1],
            xref='x',
            yref='y',
            axref='x',
            ayref='y',
            showarrow=True,
            arrowhead=3,
            arrowsize=1,
            arrowwidth=1,
            arrowcolor="green"
        )

    return fig


def _add_bond_perpendicular(fig: go.Figure, bonds: list[Bond]) -> go.Figure:
    for bond in bonds:
        fig.add_annotation(
            x=bond.center[0] + bond.perpendicular[0],
            y=bond.center[1] + bond.perpendicular[1],
            ax=bond.center[0],
            ay=bond.center[1],
            xref='x',
            yref='y',
            axref='x',
            ayref='y',
            showarrow=True,
            arrowhead=3,
            arrowsize=1,
            arrowwidth=1,
            arrowcolor="blue"
        )

    return fig


def _add_atom_vector(fig: go.Figure, atoms: list[Atom]) -> go.Figure:
    for atom in atoms:
        fig.add_annotation(
            x=atom.position[0] + atom.vector[0],
            y=atom.position[1] + atom.vector[1],
            ax=atom.position[0],
            ay=atom.position[1],
            xref='x',
            yref='y',
            axref='x',
            ayref='y',
            showarrow=True,
            arrowhead=3,
            arrowsize=1,
            arrowwidth=1,
            arrowcolor="red"
        )

    return fig
