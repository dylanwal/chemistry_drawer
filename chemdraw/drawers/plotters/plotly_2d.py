import numpy as np

from chemdraw.config.style_template import STYLE_TEMPLATE
from chemdraw.drawers.two_d.primitives_for_drawing import Dots, Fills, Lines, Texts, DrawingContainer

try:
    import plotly.graph_objs as go
except ImportError:
    raise ImportError(
        "Please install matplotlib with `pip install plotly` and `pip install kaleido==0.1.0post1` "
        "(for image generation) or use another plotting package."
    )


def draw_single_2d(container: DrawingContainer) -> go.Figure:
    fig = go.Figure()
    draw_containers(fig, container)
    apply_layout(fig, container)

    return fig


def apply_layout(fig: go.Figure, container: DrawingContainer):
    kwargs = {
        "showlegend": False,
        "hovermode": False,
        "plot_bgcolor": STYLE_TEMPLATE.plot_background_color,
        "paper_bgcolor": STYLE_TEMPLATE.plot_background_color,
        "margin": dict(l=0, r=0, b=0, t=0, pad=0),
    }

    xaxes_kwargs = {
        "visible": False,
        # "fixedrange": True,
        "layer": "below traces",
    }

    yaxes_kwargs = {
        "visible": False,
        # "fixedrange": True,
        "layer": "below traces"
    }

    # zooming
    kwargs["width"] = STYLE_TEMPLATE.plot_width
    kwargs["height"] = STYLE_TEMPLATE.plot_height

    points = container.bounding_box()
    x_span = np.array([np.min(points[0]), np.max(points[0])])
    y_span = np.array([np.min(points[1]), np.max(points[1])])
    dx = x_span[1] - x_span[0]
    dy = y_span[1] - y_span[0]
    scale = STYLE_TEMPLATE.plot_buffer  # add a buffer for text
    xaxes_kwargs["range"] = x_span[0] - dx * scale, x_span[1] + dx * scale
    yaxes_kwargs["range"] = y_span[0] - dy * scale, y_span[1] + dy * scale

    fig.update_layout(**kwargs)
    fig.update_xaxes(**xaxes_kwargs)
    fig.update_yaxes(**yaxes_kwargs)

def draw_containers(fig: go.Figure, container: DrawingContainer):
    for c in container.containers:
        draw_one_layer_of_container(fig, c)
        if len(c.containers) != 0:
            draw_containers(fig, c) # recursive call
    draw_one_layer_of_container(fig, container)


def draw_one_layer_of_container(fig: go.Figure, container: DrawingContainer):
    draw_dots(fig, container.dots)
    draw_lines(fig, container.lines)
    draw_fills(fig, container.fills)
    draw_texts(fig, container.texts)


def draw_dots(fig: go.Figure, dots: list[Dots]):
    for d in dots:
        fig.add_scatter(
            x=d.x,
            y=d.y,
            mode="markers",
            marker=dict(color=d.color, size=d.size),
            hoverinfo="skip",
            showlegend=False,
        )


def draw_lines(fig: go.Figure, lines: list[Lines]):
    for l in lines:
        fig.add_scatter(
            x=l.x,
            y=l.y,
            mode="lines",
            line=dict(color=l.color, width=l.width, dash=l.dash),
            hoverinfo="skip",
            showlegend=False,
        )


def draw_fills(fig: go.Figure, fills: list[Fills]):
    for f in fills:
        fig.add_scatter(
            x=f.x,
            y=f.y,
            mode="lines",
            fill="toself",
            fillcolor=f.color,
            line=dict(width=0),
            hoverinfo="skip",
            showlegend=False,
        )


def draw_texts(fig: go.Figure, text: list[Texts]):
    for t in text:
        t.prepare_for_drawing("\n")
        fig.add_scatter(
            x=t.x,
            y=t.y,
            text=t.symbols,
            mode="text",
            textfont=dict(color=t.color, family=t.font, size=t.size),
            hoverinfo="skip",
            showlegend=False,
        )
