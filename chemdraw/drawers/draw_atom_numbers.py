
import numpy as np
import plotly.graph_objs as go

from chemdraw.drawers.general_classes import Font
from chemdraw.objects.atoms import Atom


class ConfigDrawerAtomNumber:
    def __init__(self, parent):
        self.parent = parent

        self.show = False
        self.method = True  # True uses go.Scatter; very fast but less options  || False uses add_annotations; slower
        self.font = Font(parent, family="Arial", size=12, bold=True, color="black", offset=0.4, alignment="best")
        # ["best", "left", "right", "top", "bottom"] alignment
        self.scatter_kwargs = dict(hoverinfo="skip", cliponaxis=False)

    def __repr__(self):
        return f"show: {self.show}"


def draw_atom_numbers(fig: go.Figure, config: ConfigDrawerAtomNumber, atoms: list[Atom]) -> go.Figure:
    if not config.show:
        return fig

    if config.method:
        return _add_atom_numbers_with_scatter(fig, config, atoms)
    else:
        return _add_atom_numbers_with_annotation(fig, config, atoms)


def _add_atom_numbers_with_annotation(fig: go.Figure, config: ConfigDrawerAtomNumber, atoms: list[Atom]) -> go.Figure:
    for atom in atoms:
        x, y = atom.get_atom_number_position(config.font.alignment, config.font.offset)

        fig.add_annotation(
            x=x,
            y=y,
            text=_get_atom_number_text(config, atom),
            showarrow=False,
            font=dict(
                family=config.font.family,
                size=config.font.size,
                color=config.font.color
            ),
            # bgcolor=self.config.atom_bgcolor if self.config.atom_background_shape == "tight" else None,
            # borderwidth=self.config.atom_borderwidth,
            # borderpad=self.config.atom_borderpad,
            # opacity=0.8
        )

    return fig


def _add_atom_numbers_with_scatter(fig: go.Figure, config: ConfigDrawerAtomNumber, atoms: list[Atom]) -> go.Figure:
    symbols = [_get_atom_number_text(config, atom) for atom in atoms]
    xy = np.array([atom.get_atom_number_position(config.font.alignment, config.font.offset) for atom in atoms])

    fig.add_trace(go.Scatter(x=xy[:, 0], y=xy[:, 1], mode="text", text=symbols,
                             textfont=dict(family=config.font.family, color=config.font.color, size=config.font.size),
                             **config.scatter_kwargs))

    return fig


def _get_atom_number_text(config: ConfigDrawerAtomNumber, atom: Atom) -> str:
    symbol = str(atom.number)

    if config.font.bold:
        symbol = "<b>" + symbol + "</b>"

    return symbol
