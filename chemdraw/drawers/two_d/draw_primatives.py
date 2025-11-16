from __future__ import annotations
from typing import Sequence

import numpy as np


class Line:
    def __init__(self,
                 x: np.ndarray,
                 y: np.ndarray,
                 color: str | None = None,
                 width: float | None = None,
                 dash: str | None = None,
                 wave: bool = False
                 ) -> None:
        self.x = x
        self.y = y
        self.color = color
        self.width = width
        self.dash = dash
        self.wave = wave

class Lines:
    """Stores segments with shared style properties (color, width, dash, wave)."""

    def __init__(self, color: str, width: float, dash: str):
        self.x: np.ndarray = np.array([])
        self.y: np.ndarray = np.array([])
        self.color = color
        self.width = width
        self.dash = dash  # "solid", "dot", "dash", "longdash", "dashdot", or "longdashdot"

    def add_segment(self, x: np.ndarray, y: np.ndarray) -> None:
        """Add a line segment, inserting None to break between segments."""
        self.x = np.concatenate([self.x, x, [None]])
        self.y = np.concatenate([self.y, y, [None]])

    def matches(self, color: str, width: float, dash: str) -> bool:
        """Return True if style matches."""
        return (
            self.color == color
            and self.width == width
            and self.dash == dash
        )

class Fill:
    def __init__(self,
                 x: np.ndarray,
                 y: np.ndarray,
                 color: str
                 ) -> None:
        self.x = x
        self.y = y
        self.color = color


class Fills:
    """Stores filled polygon segments of the same color."""

    def __init__(self, color: str):
        self.x: np.ndarray = np.array([])
        self.y: np.ndarray = np.array([])
        self.color = color

    def add_segment(self, x: np.ndarray, y: np.ndarray) -> None:
        self.x = np.concatenate([self.x, x, [None]])
        self.y = np.concatenate([self.y, y, [None]])

    def matches(self, color: str) -> bool:
        return self.color == color

class Text:
    def __init__(self,
                 x: int | float,
                 y: int | float,
                 symbol: str,
                 color: str,
                 font: str,
                 size: float
                 ) -> None:
        self.x = x
        self.y = y
        self.symbol = symbol
        self.color = color
        self.font = font
        self.size = size


class Texts:
    """Stores text labels with shared font properties."""

    def __init__(self, color: str, font: str, size: float):
        self.x: np.ndarray = np.array([])
        self.y: np.ndarray = np.array([])
        self.symbols: list[str] = []
        self.color = color
        self.font = font
        self.size = size

    def add_segment(self, x: float, y: float, symbol: str) -> None:
        self.x = np.concatenate([self.x, x])
        self.y = np.concatenate([self.y, y])
        self.symbols.append(symbol)

    def matches(self, color: str, font: str, size: float) -> bool:
        return (
            self.color == color
            and self.font == font
            and self.size == size
        )


class DrawingContainer:
    """Unified container for lines, fills, and text, with Plotly export."""

    def __init__(self):
        self.lines = []
        self.fills = []
        self.texts = []

    def __str__(self):
        text = f"lines: {len(self.lines)} | fills: {len(self.fills)} | text: {len(self.texts)}"
        return text

    def add_line(self, line: Line):
        for l in self.lines:
            if l.matches(line.color, line.width, line.dash):
                l.add_segment(line.x, line.y)
                return

        new_line = Lines(line.color, line.width, line.dash)
        new_line.add_segment(line.x, line.y)
        self.lines.append(new_line)

    def add_fill(self, fill: Fill) -> None:
        for f in self.fills:
            if f.matches(fill.color):
                f.add_segment(fill.x, fill.y)
                return

        new_fill = Fills(fill.color)
        new_fill.add_segment(fill.x, fill.y)
        self.fills.append(new_fill)
        
    def add_text(self, text: Text) -> None:
        for f in self.texts:
            if f.matches(text.color, text.font, text.size):
                f.add_segment(text.x, text.y, text.symbol)
                return

        new_text = Texts(text.color, text.font, text.size)
        new_text.add_segment(text.x, text.y, text.symbol)
        self.texts.append(new_text)

    def add_objects(self, objs: Line | Fill | Text | Sequence[Line | Fill | Text]):
        if not isinstance(objs, Sequence):
            objs = [objs]

        for obj in objs:
            if isinstance(obj, Line):
                self.add_line(obj)
            elif isinstance(obj, Fill):
                self.add_fill(obj)
            elif isinstance(obj, Text):
                self.add_text(obj)
            else:
                raise RuntimeError(f"Unknown type {type(obj)}")
