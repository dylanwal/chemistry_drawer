from __future__ import annotations
from typing import Optional

import plotly.graph_objects as go


class Lines:
    """Stores segments with shared style properties (color, width, dash, wave)."""

    def __init__(self, color: str, width: float, dash: str, wave: bool):
        self.x: list[Optional[float]] = []
        self.y: list[Optional[float]] = []
        self.color = color
        self.width = width
        self.dash = dash  # "solid", "dot", "dash", "longdash", "dashdot", or "longdashdot"
        self.wave = wave

    def add_segment(self, x: list[float], y: list[float]) -> None:
        """Add a line segment, inserting None to break between segments."""
        self.x.extend(x + [None])
        self.y.extend(y + [None])

    def matches(self, color: str, width: float, dash: str, wave: bool) -> bool:
        """Return True if style matches."""
        return (
            self.color == color
            and self.width == width
            and self.dash == dash
            and self.wave == wave
        )

    def to_trace(self) -> go.Scatter:
        """Convert this line collection to a Plotly trace."""
        # Optionally, "wave" can be represented as smoothed or dashed lines
        if self.wave:
            raise NotImplementedError("")  #TODO
        return go.Scatter(
            x=self.x,
            y=self.y,
            mode="lines",
            line=dict(color=self.color, width=self.width, dash=self.dash),
            hoverinfo="skip",
        )


class DrawLines:
    """Manages multiple Lines groups."""

    def __init__(self):
        self.lines: list[Lines] = []

    def add_segment(
        self,
        x: list[float],
        y: list[float],
        color: str,
        width: float,
        dash: str,
        wave: bool,
    ) -> None:
        """Add a segment to an existing style or create a new one."""
        for line in self.lines:
            if line.matches(color, width, dash, wave):
                line.add_segment(x, y)
                return  

        
        new_line = Lines(color, width, dash, wave)
        new_line.add_segment(x, y)
        self.lines.append(new_line)

    def to_traces(self) -> list[go.Scatter]:
        """Convert all stored lines to Plotly Scatter traces."""
        return [line.to_trace() for line in self.lines]


class Fills:
    """Stores filled polygon segments of the same color."""

    def __init__(self, color: str):
        self.x: list[Optional[float]] = []
        self.y: list[Optional[float]] = []
        self.color = color

    def add_segment(self, x: list[float], y: list[float]) -> None:
        self.x.extend(x + [None])
        self.y.extend(y + [None])

    def matches(self, color: str) -> bool:
        return self.color == color

    def to_trace(self) -> go.Scatter:
        """Convert this fill collection to a Plotly filled trace."""
        return go.Scatter(
            x=self.x,
            y=self.y,
            mode="lines",
            fill="toself",
            fillcolor=self.color,
            line=dict(width=0),
            hoverinfo="skip",
        )

class DrawFills:
    """Manages multiple Fills groups."""

    def __init__(self):
        self.fills: list[Fills] = []

    def add_segment(self, x: list[float], y: list[float], color: str) -> None:
        for fill in self.fills:
            if fill.matches(color):
                fill.add_segment(x, y)
                return

        new_fill = Fills(color)
        new_fill.add_segment(x, y)
        self.fills.append(new_fill)

    def to_traces(self) -> list[go.Scatter]:
        """Convert all stored fills to Plotly filled area traces."""
        return [fill.to_trace() for fill in self.fills]


class Text:
    """Stores text labels with shared font properties."""

    def __init__(self, color: str, font: str, size: float):
        self.x: list[float] = []
        self.y: list[float] = []
        self.symbols: list[str] = []
        self.color = color
        self.font = font
        self.size = size

    def add_segment(self, x: float, y: float, symbol: str) -> None:
        self.x.append(x)
        self.y.append(y)
        self.symbols.append(symbol)

    def matches(self, color: str, font: str, size: float) -> bool:
        return (
            self.color == color
            and self.font == font
            and self.size == size
        )

    def to_trace(self) -> go.Scatter:
        """Convert this text collection to a Plotly text trace."""
        return go.Scatter(
            x=self.x,
            y=self.y,
            text=self.symbols,
            mode="text",
            textfont=dict(color=self.color, family=self.font, size=self.size),
            hoverinfo="skip",
        )

class DrawText:
    """Manages multiple Text groups."""

    def __init__(self):
        self.texts: list[Text] = []

    def add_segment(
        self,
        x: float,
        y: float,
        symbol: str,
        color: str,
        font: str,
        size: float,
    ) -> None:
        for text in self.texts:
            if text.matches(color, font, size):
                text.add_segment(x, y, symbol)
                return

        new_text = Text(color, font, size)
        new_text.add_segment(x, y, symbol)
        self.texts.append(new_text)

    def to_traces(self) -> list[go.Scatter]:
        """Convert all stored text labels to Plotly text traces."""
        return [txt.to_trace() for txt in self.texts]


class Drawing:
    """Unified container for lines, fills, and text, with Plotly export."""

    def __init__(self):
        self.lines = DrawLines()
        self.fills = DrawFills()
        self.text = DrawText()

    def to_figure(self) -> go.Figure:
        """Combine all traces into a single Plotly figure."""
        traces = (
            self.fills.to_traces()
            + self.lines.to_traces()
            + self.text.to_traces()
        )
        fig = go.Figure(traces)
        fig.update_layout(
            xaxis=dict(scaleanchor="y", showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False),
            plot_bgcolor="white",
        )
        return fig