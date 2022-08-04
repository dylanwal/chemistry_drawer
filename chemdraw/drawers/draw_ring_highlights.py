
import numpy as np
import plotly.graph_objs as go

from chemdraw.drawers.general_classes import Highlight
from chemdraw.objects.rings import Ring


class ConfigDrawerRingHighlights:
    def __init__(self, parent):
        self.parent = parent
        self.ring = Highlight(parent, show=True, color="rgba(69, 127, 222, 0.5)", offset=1)

    def __repr__(self):
        return f"show ring highlights: {self.ring.show}"


def draw_ring_highlight(fig: go.Figure, config: ConfigDrawerRingHighlights, rings: list[Ring]) -> go.Figure:
    if not config.ring.show or not rings or not rings[0].parent.ring_highlights:
        return fig

    for ring in rings:
        if ring.highlight.show:
            xy = _get_coordinates(config, ring)
            color = config.ring.get_attr("color", ring.highlight)

            fig.add_trace(go.Scatter(x=xy[:, 0], y=xy[:, 1], mode="lines", fill='toself', fillcolor=color,
                                     line=dict(color='rgba(0, 0, 0, 0)')))

    return fig


def _get_coordinates(config: ConfigDrawerRingHighlights, ring: Ring) -> np.ndarray:
    xy = ring.coordinates
    xy = sort_circle_points(xy)
    offset = config.ring.get_attr("offset", ring.highlight)
    if offset == 1:
        return xy

    for i, point in enumerate(xy):
        vector = point - ring.center
        vector = offset * vector
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
