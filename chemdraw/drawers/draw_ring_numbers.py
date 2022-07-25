
import numpy as np
import plotly.graph_objs as go

from chemdraw.objects.rings import Ring


class ConfigDrawerRingNumber:
    def __init__(self, parent):
        self.parent = parent

        self.show = False
        self.method = True  # True uses go.Scatter; very fast less options  || False uses add_annotations; slower
        self.font = "Arial"
        self.font_bold = True
        self.font_size = 20
        self.font_color = "maroon"
        self.scatter_kwargs = dict(hoverinfo="skip", cliponaxis=False)

    def __repr__(self):
        return f"show: {self.show}"


def draw_ring_numbers(fig: go.Figure, config: ConfigDrawerRingNumber, rings: list[Ring]) -> go.Figure:
    if not config.show:
        return fig

    if config.method:
        return _add_ring_numbers_with_scatter(fig, config, rings)
    else:
        return _add_ring_numbers_with_annotation(fig, config, rings)


def _add_ring_numbers_with_annotation(fig: go.Figure, config: ConfigDrawerRingNumber, rings: list[Ring]) -> go.Figure:
    for ring in rings:
        xy = ring.center

        fig.add_annotation(
            x=xy[0],
            y=xy[1],
            text=_get_ring_number_text(config, ring),
            showarrow=False,
            font=dict(
                family=config.font,
                size=config.font_size,
                color=config.font_color
            ),
            # bgcolor=self.config.ring_bgcolor if self.config.ring_background_shape == "tight" else None,
            # borderwidth=self.config.ring_borderwidth,
            # borderpad=self.config.ring_borderpad,
            # opacity=0.8
        )

    return fig


def _add_ring_numbers_with_scatter(fig: go.Figure, config: ConfigDrawerRingNumber, rings: list[Ring]) -> go.Figure:
    symbols = [_get_ring_number_text(config, ring) for ring in rings]
    xy = np.array([ring.center for ring in rings])

    fig.add_trace(go.Scatter(x=xy[:, 0], y=xy[:, 1], mode="text", text=symbols,
                             textfont=dict(family=config.font, color=config.font_color, size=config.font_size),
                             **config.scatter_kwargs))

    return fig


def _get_ring_number_text(config: ConfigDrawerRingNumber, ring: Ring) -> str:
    symbol = str(ring.number)

    if config.font_bold:
        symbol = "<b>" + symbol + "</b>"

    return symbol
