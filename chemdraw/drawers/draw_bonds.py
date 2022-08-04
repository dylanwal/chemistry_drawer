import numpy as np
import plotly.graph_objs as go

from chemdraw.drawers.general_classes import Line
from chemdraw.objects.bonds import Bond, BondType, BondAlignment, BondStereoChem
import chemdraw.utils.vector_math as vector_math
import chemdraw.utils.general_math as general_math


class ConfigDrawerBonds:
    def __init__(self, parent):
        self.parent = parent

        self.show = True
        self.line_format = Line(parent, width=6, color="black")
        self.offset = 0.37
        self.double_bond_offset = 0.35  # width
        self.double_bond_offset_length = 0.7  # [0 - 1] 1 = full length; <1 = shorter
        self.double_bond_center_length = 1.1  # [1 - 1.5] 1 = full length; >1 = longer
        self.triple_bond_offset = 0.23   # width
        self.triple_bond_length = 0.5
        self.stereo_offset = 0.23  # how wide is the triangle
        self.stereo_wedge_number_lines = 6
        self.stereo_wedge_line_width = 6
        self.scatter_kwargs = dict(hoverinfo="skip", cliponaxis=False)

    def __repr__(self):
        return f"show: {self.show}"


def draw_bonds(fig: go.Figure, config: ConfigDrawerBonds, bonds: list[Bond]) -> go.Figure:
    if not config.show:
        return fig

    for bond in bonds:
        x, y = bond.get_coordinates(config.parent.atoms.show_carbons, config.offset)
        if bond.type_ == BondType.single:
            if bond.stereo_chem != BondStereoChem.default:
                fig = _draw_stereo_bond(fig, config, x, y, bond)
            else:
                fig = _draw_bond_on_fig(fig, config, x, y, bond)
        elif bond.type_ == BondType.double:
            if bond.alignment == BondAlignment.center:
                fig = _bond_double_center(fig, config, x, y, bond)
            else:
                fig = _double_bond_offset(fig, config, x, y, bond)
        else:
            fig = _bond_triple(fig, config, x, y, bond)

    return fig


def _draw_bond_on_fig(fig: go.Figure, config: ConfigDrawerBonds, x, y, bond) -> go.Figure:
    return fig.add_trace(
        go.Scatter(
            x=x, y=y,
            mode="lines",
            line=dict(
                color=config.line_format.get_attr("color", bond.line_format),
                width=config.line_format.get_attr("width", bond.line_format),
            ),
            **config.scatter_kwargs
        ))


def _bond_double_center(fig: go.Figure, config: ConfigDrawerBonds, x, y, bond: Bond) -> go.Figure:
    x_left = x + bond.perpendicular[0] * config.double_bond_offset / 2
    x_right = x - bond.perpendicular[0] * config.double_bond_offset / 2
    y_left = y + bond.perpendicular[1] * config.double_bond_offset / 2
    y_right = y - bond.perpendicular[1] * config.double_bond_offset / 2
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
    fig = _draw_bond_on_fig(fig, config, x_left, y_left, bond)
    # right
    fig = _draw_bond_on_fig(fig, config, x_right, y_right, bond)

    return fig


def _double_bond_offset(fig: go.Figure, config: ConfigDrawerBonds, x, y, bond: Bond) -> go.Figure:
    if bond.alignment == BondAlignment.perpendicular:  # same side as perpendicular
        x_off = x + bond.perpendicular[0] * config.double_bond_offset
        y_off = y + bond.perpendicular[1] * config.double_bond_offset
    else:  # opposite side perpendicular
        x_off = x - bond.perpendicular[0] * config.double_bond_offset
        y_off = y - bond.perpendicular[1] * config.double_bond_offset

    # center
    fig = _draw_bond_on_fig(fig, config, x, y, bond)
    # right/left
    if config.double_bond_offset_length != 1:
        x0, x1, y0, y1 = vector_math.shorten_line(x_off[0], x_off[1], y_off[0], y_off[1],
                                                  config.double_bond_offset_length)
        x_off = [x0, x1]
        y_off = [y0, y1]

    fig = _draw_bond_on_fig(fig, config, x_off, y_off, bond)

    return fig


def _bond_triple(fig: go.Figure, config: ConfigDrawerBonds, x, y, bond: Bond) -> go.Figure:
    x_left = x + bond.perpendicular[0] * config.triple_bond_offset
    x_right = x - bond.perpendicular[0] * config.triple_bond_offset
    y_left = y + bond.perpendicular[1] * config.triple_bond_offset
    y_right = y - bond.perpendicular[1] * config.triple_bond_offset

    if config.triple_bond_length != 1:
        x_left, y_left = _shorten_bond_triple(config, bond, x_left, y_left)
        x_right, y_right = _shorten_bond_triple(config, bond, x_right, y_right)

    # center
    fig = _draw_bond_on_fig(fig, config, x, y, bond)
    # left
    fig = _draw_bond_on_fig(fig, config, x_left, y_left, bond)
    # right
    fig = _draw_bond_on_fig(fig, config, x_right, y_right, bond)

    return fig


def _shorten_bond_triple(config: ConfigDrawerBonds, bond: Bond, x: np.ndarray, y: np.ndarray) \
        -> tuple[np.ndarray, np.ndarray]:
    x0, x1, y0, y1 = vector_math.shorten_line(x[0], x[1], y[0], y[1], config.triple_bond_length)

    # only shorten the terminal end
    if bond.vector[0] == 0:  # vertical
        if bond.vector[1] > 0:
            if y0 > y1:
                x = np.array([x0, x[1]])
                y = np.array([y0, y[1]])
            else:
                x = np.array([x[0], x1])
                y = np.array([y[0], y1])

    elif bond.vector[0] > 0:
        if x0 > x1:
            x = np.array([x0, x[1]])
            y = np.array([y0, y[1]])
        else:
            x = np.array([x[0], x1])
            y = np.array([y[0], y1])
    else:
        if x0 < x1:
            x = np.array([x0, x[1]])
            y = np.array([y0, y[1]])
        else:
            x = np.array([x[0], x1])
            y = np.array([y[0], y1])

    return x, y


def _draw_stereo_bond(fig: go.Figure, config: ConfigDrawerBonds, x: np.ndarray, y: np.ndarray, bond: Bond) -> go.Figure:
    color = config.line_format.get_attr("color", bond.line_format)

    if bond.stereo_chem == BondStereoChem.up:
        x_left = x[1] + bond.perpendicular[0] * config.stereo_offset
        x_right = x[1] - bond.perpendicular[0] * config.stereo_offset
        y_left = y[1] + bond.perpendicular[1] * config.stereo_offset
        y_right = y[1] - bond.perpendicular[1] * config.stereo_offset
        x_plot = np.array([x[0], x_left, x_right, x[0]])
        y_plot = np.array([y[0], y_left, y_right, y[0]])

        fig.add_trace(
            go.Scatter(x=x_plot, y=y_plot, mode="lines", fill="toself", fillcolor=color,
                       line=dict(color=color))
        )

        return fig

    # down
    num_lines = config.stereo_wedge_number_lines
    xy = general_math.points_along_line((x[0], y[0]), (x[1], y[1]), num_lines + 2)
    # the +2  is for the ends
    # remove the ends
    xy = xy[1:-1, :]

    points = np.empty((3 * num_lines, 2), dtype="float64")
    offset = np.linspace(1 / num_lines, 1, num_lines) * config.stereo_offset
    for i in range(num_lines):
        i_ = i * 3
        points[i_:i_ + 2, :] = general_math.get_offset_points(xy[i, :], bond.perpendicular, offset[i])
        points[i_ + 2, :] = [None, None]

    fig.add_trace(
        go.Scatter(x=points[:, 0], y=points[:, 1], mode="lines",
                   line=dict(color=color, width=config.stereo_wedge_line_width))
    )

    return fig
