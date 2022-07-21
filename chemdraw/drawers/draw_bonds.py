import plotly.graph_objs as go

from chemdraw.objects.bonds import Bond, BondType
import chemdraw.utils.vector_math as vector_math


class ConfigDrawerBonds:
    show = True
    width = 8
    color = "black"
    triple_bond_offset = 0.23
    double_bond_offset = 0.4
    double_bond_offset_length = 0.7  # [0 - 1] 1 = full length; <1 = shorter
    double_bond_center_length = 1.1  # [1 - 1.5] 1 = full length; >1 = longer
    scatter_kwargs = dict(hoverinfo="skip", cliponaxis=False)


def draw_bonds(fig: go.Figure, config: ConfigDrawerBonds, bonds: list[Bond]) -> go.Figure:
    if not config.show:
        return fig

    for bond in bonds:
        if bond.type_ == BondType.single:
            fig = _draw_bond_on_fig(fig, config, x=bond.x, y=bond.y, color=config.color, width=config.width)
        elif bond.type_ == BondType.double:
            if bond.alignment == 0:
                fig = _bond_double_center(fig, config, bond)
            else:
                fig = _double_bond_offset(fig, config, bond)
        else:
            fig = _bond_triple(fig, config, bond)

    return fig


def _draw_bond_on_fig(fig: go.Figure, config: ConfigDrawerBonds, x, y, color, width) -> go.Figure:
    return fig.add_trace(go.Scatter(x=x, y=y, mode="lines", line=dict(color=color, width=width),
                                    **config.scatter_kwargs))


def _bond_double_center(fig: go.Figure, config: ConfigDrawerBonds, bond: Bond) -> go.Figure:
    x_left = bond.x + bond.perpendicular[0] * config.double_bond_offset / 2
    x_right = bond.x - bond.perpendicular[0] * config.double_bond_offset / 2
    y_left = bond.y + bond.perpendicular[1] * config.double_bond_offset / 2
    y_right = bond.y - bond.perpendicular[1] * config.double_bond_offset / 2
    if config.double_bond_center_length != 1:
        x0, x1, y0, y1 = vector_math.shorten_line(x_left[0], x_left[1], y_left[0], y_left[1],
                                                  config.double_bond_center_length)
        x_left = [x0, x1]
        y_left = [y0, y1]
        x0, x1, y0, y1 = vector_math.shorten_line(x_right[0], x_right[1], y_right[0], y_right[1],
                                                  config.double_bond_center_length)
        x_right = [x0, x1]
        y_right = [y0, y1]

    # left
    fig = _draw_bond_on_fig(fig, config, x=x_left, y=y_left, color=config.color, width=config.width)
    # right
    fig = _draw_bond_on_fig(fig, config, x=x_right, y=y_right, color=config.color, width=config.width)

    return fig


def _double_bond_offset(fig: go.Figure, config: ConfigDrawerBonds, bond: Bond) -> go.Figure:
    if bond.alignment == 1:  # same side as perpendicular
        x_off = bond.x + bond.perpendicular[0] * config.double_bond_offset
        y_off = bond.y + bond.perpendicular[1] * config.double_bond_offset
    else:  # opposite side perpendicular
        x_off = bond.x - bond.perpendicular[0] * config.double_bond_offset
        y_off = bond.y - bond.perpendicular[1] * config.double_bond_offset

    # center
    fig = _draw_bond_on_fig(fig, config, x=bond.x, y=bond.y, color=config.color, width=config.width)
    # right/left
    if config.double_bond_offset_length != 1:
        x0, x1, y0, y1 = vector_math.shorten_line(x_off[0], x_off[1], y_off[0], y_off[1],
                                                  config.double_bond_offset_length)
        x_off = [x0, x1]
        y_off = [y0, y1]

    fig = _draw_bond_on_fig(fig, config, x=x_off, y=y_off, color=config.color, width=config.width)

    return fig


def _bond_triple(fig: go.Figure, config: ConfigDrawerBonds, bond: Bond) -> go.Figure:
    x_left = bond.x + bond.perpendicular[0] * config.triple_bond_offset
    x_right = bond.x - bond.perpendicular[0] * config.triple_bond_offset
    y_left = bond.y + bond.perpendicular[1] * config.triple_bond_offset
    y_right = bond.y - bond.perpendicular[1] * config.triple_bond_offset

    # center
    fig = _draw_bond_on_fig(fig, config, x=bond.x, y=bond.y, color=config.color, width=config.width)
    # left
    fig = _draw_bond_on_fig(fig, config, x=x_left, y=y_left, color=config.color, width=config.width)
    # right
    fig = _draw_bond_on_fig(fig, config, x=x_right, y=y_right, color=config.color, width=config.width)

    return fig
