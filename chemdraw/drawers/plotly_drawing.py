
import plotly.graph_objs as go

from chemdraw.drawers.two_d.draw_primatives import Fills, Lines, Texts, DrawingContainer

def container_to_figure(container: DrawingContainer) -> go.Figure:
    fig = go.Figure()

    draw_lines(fig, container.lines)
    draw_fills(fig, container.fills)
    draw_texts(fig, container.texts)

    return fig


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
        fig.add_scatter(
            x=t.x,
            y=t.y,
            text=t.symbols,
            mode="text",
            textfont=dict(color=t.color, family=t.font, size=t.size),
            hoverinfo="skip",
            showlegend=False,
        )



