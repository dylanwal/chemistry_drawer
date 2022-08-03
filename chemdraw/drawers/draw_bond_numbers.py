
import numpy as np
import plotly.graph_objs as go

from chemdraw.drawers.general_classes import Font
from chemdraw.objects.bonds import Bond


class ConfigDrawerBondNumber:
    def __init__(self, parent):
        self.parent = parent

        self.show = False
        self.method = True  # True uses go.Scatter; very fast less options  || False uses add_annotations; slower
        self.font = Font(family="Arial", size=20, bold=True, color="gray", offset=0.4, alignment="best")
        # ["best", "left", "right", "top", "bottom"] alignment
        self.scatter_kwargs = dict(hoverinfo="skip", cliponaxis=False)

    def __repr__(self):
        return f"show: {self.show}"


def draw_bond_numbers(fig: go.Figure, config: ConfigDrawerBondNumber, bonds: list[Bond]) -> go.Figure:
    if not config.show:
        return fig

    if config.method:
        return _add_bond_numbers_with_scatter(fig, config, bonds)
    else:
        return _add_bond_numbers_with_annotation(fig, config, bonds)


def _add_bond_numbers_with_annotation(fig: go.Figure, config: ConfigDrawerBondNumber, bonds: list[Bond]) -> go.Figure:
    for bond in bonds:
        x, y = bond.get_bond_number_position(config.font.alignment, config.font.offset)

        fig.add_annotation(
            x=x,
            y=y,
            text=_get_bond_number_text(config, bond),
            showarrow=False,
            font=dict(
                family=config.font.family,
                size=config.font.size,
                color=config.font.color
            ),
            # bgcolor=self.config.bond_bgcolor if self.config.bond_background_shape == "tight" else None,
            # borderwidth=self.config.bond_borderwidth,
            # borderpad=self.config.bond_borderpad,
            # opacity=0.8
        )

    return fig


def _add_bond_numbers_with_scatter(fig: go.Figure, config: ConfigDrawerBondNumber, bonds: list[Bond]) -> go.Figure:
    symbols = [_get_bond_number_text(config, bond) for bond in bonds]
    xy = np.array([bond.get_bond_number_position(config.font.alignment, config.font.offset) for bond in bonds])

    fig.add_trace(go.Scatter(x=xy[:, 0], y=xy[:, 1], mode="text", text=symbols,
                             textfont=dict(family=config.font.family, color=config.font.color, size=config.font.size),
                             **config.scatter_kwargs))

    return fig


def _get_bond_number_text(config: ConfigDrawerBondNumber, bond: Bond) -> str:
    symbol = str(bond.number)

    if config.font.bold:
        symbol = "<b>" + symbol + "</b>"

    return symbol
