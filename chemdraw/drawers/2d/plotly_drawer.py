import plotly.graph_objs as go
import numpy as np


def draw_all():



def draw_lines(
        fig: go.Figure,
        xy: np.ndarray,
        color: str,
        width: int,
        plotly_kwargs: dict = None
):
    return fig.add_scatter(
            x=xy[:, 0], y=xy[:, 1],
            mode="lines",
            line=dict(
                color=color,
                width=width,
            ),
            **plotly_kwargs
        )


def draw_fill(
        fig: go.Figure,
        xy: np.ndarray,
        color: str,
        width: int,
        plotly_kwargs: dict = None
):
    return fig.add_scatter(
            x=xy[:, 0], y=xy[:, 1],
            mode="lines",
            line=dict(
                color=color,
                width=width,
            ),
            fill="toself",
            fillcolor=color,
            **plotly_kwargs
        )


def draw_text(
        fig: go.Figure,
        xy: np.ndarray,
        text: list[str],
        font_family: str,
        font_size: str,
        font_color: str,
        plotly_kwargs: dict = None
):
    fig.add_scatter(
        x=xy[:, 0], y=xy[:, 1],
        mode="text",
        text=text,
        textfont=dict(family=font_family, color=font_color, size=font_size),
        **plotly_kwargs
    )
