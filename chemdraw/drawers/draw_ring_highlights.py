
import numpy as np
import plotly.graph_objs as go

from chemdraw.objects.atoms import Atom
from chemdraw.objects.bonds import Bond
from chemdraw.objects.rings import Ring
import chemdraw.utils.vector_math as vector_math


class ConfigDrawerRingHighlights:
    show = False
    offset = 1
    color = "rgba(69, 127, 222, 0.5)"

    def __repr__(self):
        return f"show ring highlights: {self.show}"


def draw_ring_highlight(fig: go.Figure, config: ConfigDrawerRingHighlights, rings: list[Ring]) -> go.Figure:
    if not config.show:
        return fig

    for ring in rings:
        if ring.highlight:
            xy = _get_coordinates(config, ring)
            color = config.color if ring.highlight_color is None else ring.highlight_color

            fig.add_trace(go.Scatter(x=xy[:, 0], y=xy[:, 1], mode="lines", fill='toself', fillcolor=color,
                                     line=dict(color='rgba(0, 0, 0, 0)')))

    return fig


def _get_coordinates(config: ConfigDrawerRingHighlights, ring: Ring) -> np.ndarray:
    xy = ring.coordinates
    xy = sort_circle_points(xy)
    if config.offset == 1:
        return xy

    for i, point in enumerate(xy):
        vector = point - ring.center
        vector = config.offset * vector
        xy[i] = ring.center + vector

    return xy


def sort_circle_points(xy: np.ndarray) -> np.ndarray:
    # normalize data  [-1, 1]
    xy_sort = np.empty_like(xy)
    xy_sort[:, 0] = 2 * (xy[:, 0] - np.min(xy[:, 0]))/(np.max(xy[:, 0] - np.min(xy[:, 0]))) - 1
    xy_sort[:, 1] = 2 * (xy[:, 1] - np.min(xy[:, 1])) / (np.max(xy[:, 1] - np.min(xy[:, 1]))) - 1

    # get sort result
    sort_array = np.arctan2(xy_sort[:, 0], xy_sort[:, 1])
    sort_result = np.argsort(sort_array)

    # apply sort result
    return xy[sort_result]
