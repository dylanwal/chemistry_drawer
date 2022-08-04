import numpy as np
import plotly.graph_objs as go

from chemdraw.drawers.general_classes import Font, Line
from chemdraw.objects.parenthesis import Parenthesis
from chemdraw.utils import vector_math


def parabola(x: np.ndarray, prefactor: float = 0.4) -> np.ndarray:
    return prefactor * x ** 2


class ConfigDrawerParenthesis:
    def __init__(self, parent):
        self.parent = parent

        self.func = parabola
        self.points = 10
        self.size = 0.8  # distance from to bottom of parenthesis
        self.offset = 0.04
        self.line_format = Line(parent, width=6, color="black")
        self.sub_script_font = Font(parent, family="Arial", size=28, bold=True, color="black", offset=0)
        self.super_script_font = Font(parent, family="Arial", size=15, bold=True, color="black", offset=0)
        self.scatter_kwargs = dict(hoverinfo="skip", cliponaxis=False)

        self._show = None
        self.show = True
        self.super_script_font.show = False

    def __repr__(self):
        return f"show: {self.show}"

    @property
    def show(self):
        return self._show

    @show.setter
    def show(self, show: bool):
        self._show = show
        self.sub_script_font.show = show
        self.super_script_font.show = show
        self.line_format.show = show

    def get_size(self):
        return self.size / self.parent._scaling

    def get_offset(self):
        return self.offset / self.parent._scaling


def draw_parenthesis(fig: go.Figure, config: ConfigDrawerParenthesis, parenthesis: list[Parenthesis]) -> go.Figure:
    if not config.show:
        return fig

    for parenthesis_ in parenthesis:
        xy = _get_parenthesis_points(config, parenthesis_)

        fig.add_trace(
            go.Scatter(
                x=xy[:, 0], y=xy[:, 1],
                mode="lines",
                line=dict(
                    color=config.line_format.get_attr("color", parenthesis_.line_format),
                    width=config.line_format.get_attr("width", parenthesis_.line_format),
                    ),
                **config.scatter_kwargs
            ))

        # add sub_script
        if config.sub_script_font.get_attr("show", parenthesis_.sub_script_font):
            if parenthesis_.sub_script is None:
                continue

            xy = _get_sub_script_coordinates(config, parenthesis_)
            fig.add_trace(
                go.Scatter(
                    x=[xy[0]], y=[xy[1]],
                    mode="text",
                    text=parenthesis_.sub_script,
                    textfont=dict(
                        family=config.sub_script_font.get_attr("family", parenthesis_.sub_script_font),
                        color=config.sub_script_font.get_attr("color", parenthesis_.sub_script_font),
                        size=config.sub_script_font.get_attr("size", parenthesis_.sub_script_font),
                        ),
                    **config.scatter_kwargs
                ))

        # add super_script
        if config.super_script_font.get_attr("show", parenthesis_.super_script_font):
            if parenthesis_.super_script is None:
                continue

            xy = _get_super_script_coordinates(config, parenthesis_)
            fig.add_trace(
                go.Scatter(
                    x=[xy[0]], y=[xy[1]],
                    mode="text",
                    text=parenthesis_.super_script,
                    textfont=dict(
                        family=config.super_script_font.get_attr("family", parenthesis_.super_script_font),
                        color=config.super_script_font.get_attr("color", parenthesis_.super_script_font),
                        size=config.super_script_font.get_attr("size", parenthesis_.super_script_font),
                        ),
                    **config.scatter_kwargs
                ))

    return fig


def _get_parenthesis_points(config: ConfigDrawerParenthesis, parenthesis: Parenthesis) -> np.ndarray:
    # create parenthesis points
    if parenthesis.size is None:
        size = config.get_size()
    else:
        size = parenthesis.size

    x = np.linspace(-size, size, config.points)
    y = config.func(x)

    # move and rotate into position
    xy = np.array((x, y)).T
    rot_matrix = vector_math.rotation_matrix(np.array([0, 1]), parenthesis.vector)
    xy = np.dot(xy, rot_matrix)
    xy += parenthesis.coordinates
    xy += config.get_offset() * parenthesis.vector

    return xy


def _get_sub_script_coordinates(config: ConfigDrawerParenthesis, parenthesis: Parenthesis) -> np.ndarray:
    # create parenthesis points
    if parenthesis.size is None:
        size = config.get_size()
    else:
        size = parenthesis.size

    perpendicular = vector_math.perpendicular(parenthesis.vector)
    xy = parenthesis.coordinates + perpendicular * size
    xy -= parenthesis.vector * config.sub_script_font.get_attr("offset", parenthesis.sub_script_font)

    return xy


def _get_super_script_coordinates(config: ConfigDrawerParenthesis, parenthesis: Parenthesis) -> np.ndarray:
    # create parenthesis points
    if parenthesis.size is None:
        size = config.get_size()
    else:
        size = parenthesis.size

    perpendicular = vector_math.perpendicular(parenthesis.vector)
    xy = parenthesis.coordinates - perpendicular * size
    xy -= parenthesis.vector * config.super_script_font.get_attr("offset", parenthesis.super_script_font)

    return xy
