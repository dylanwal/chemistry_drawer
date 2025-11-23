from __future__ import annotations
from typing import Sequence
import copy

import numpy as np

import chemdraw.utils.math_vectors as math_vectors
import chemdraw.utils.math_points as math_points


class Dot:
    def __init__(self,
                 x: float | int,
                 y: float | int,
                 color: str | None = None,
                 size: float | None = None,

                 ) -> None:
        self.x = x
        self.y = y
        self.color = color
        self.size = size


class Dots:
    """Stores dots with shared style properties (color, size)."""

    def __init__(self, color: str, size: float):
        self.x: np.ndarray = np.array([])
        self.y: np.ndarray = np.array([])
        self.color = color
        self.size = size

    def add_segment(self, x: float | int, y: float | int) -> None:
        """Add a line segment, inserting None to break between segments."""
        self.x = np.append(self.x, x)
        self.y = np.append(self.y, y)

    def join(self, other: Dots) -> None:
        self.x = np.append(self.x, other.x)
        self.y = np.append(self.y, other.y)

    def matches(self, color: str, size: float | int) -> bool:
        """Return True if style matches."""
        return (
                self.color == color
                and self.size == size
        )


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
        self.x = np.concatenate((self.x, x, [None]))
        self.y = np.concatenate((self.y, y, [None]))

    def join(self, other: Lines) -> None:
        self.x = np.append(self.x, other.x)
        self.y = np.append(self.y, other.y)

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
        self.x = np.concatenate((self.x, x, [None]))
        self.y = np.concatenate((self.y, y, [None]))

    def join(self, other: Fills) -> None:
        self.x = np.append(self.x, other.x)
        self.y = np.append(self.y, other.y)

    def matches(self, color: str) -> bool:
        return self.color == color


class Text:
    def __init__(self,
                 x: int | float,
                 y: int | float,
                 symbol: str | list[str] | tuple[str],
                 color: str,
                 font: str,
                 size: float,
                 bold: bool
                 ):
        self.x = x
        self.y = y
        self.symbol = symbol  # if in list/tuple; convert to page returns upon drawing
        self.color = color
        self.font = font
        self.size = size
        self.bold = bold


class Texts:
    """Stores text labels with shared font properties."""

    def __init__(self, color: str, font: str, size: float, bold: bool):
        self.x: np.ndarray = np.array([])
        self.y: np.ndarray = np.array([])
        self.symbols: list[str | list[str] | tuple[str]] = []
        self.color = color
        self.font = font
        self.size = size
        self.bold = bold

    def add_segment(self, x: float, y: float, symbol: str):
        self.x = np.concatenate((self.x, np.array([x])))
        self.y = np.concatenate((self.y, np.array([y])))
        self.symbols.append(symbol)

    def join(self, other: Texts) -> None:
        self.x = np.append(self.x, other.x)
        self.y = np.append(self.y, other.y)
        self.symbols.extend(other.symbols)

    def matches(self, color: str, font: str, size: float) -> bool:
        return (
                self.color == color
                and self.font == font
                and self.size == size
        )


class Arrow:
    def __init__(self,
                 x: np.ndarray,
                 y: np.ndarray,
                 color: str | None = None,
                 line_width: float | None = None,
                 head_width: float | None = None,
                 head_height: float | None = None,
                 dash: str | None = None,
                 style: int | None = None
                 ) -> None:
        self.x = x  # first point is tail, last point is head
        self.y = y
        self.color = color
        self.line_width = line_width
        self.head_width = head_width
        self.head_height = head_height
        self.dash = dash
        self.style = style


class Arrows:
    """Stores segments with shared style properties (color, width, dash, style)."""

    def __init__(self):
        self.arrows: list[Arrow] = []

    @property
    def color(self):
        if len(self.arrows) == 0:
            return None
        return self.arrows[0].color

    @property
    def line_width(self):
        if len(self.arrows) == 0:
            return None
        return self.arrows[0].line_width

    @property
    def dash(self):
        if len(self.arrows) == 0:
            return None
        return self.arrows[0].dash

    @property
    def style(self):
        if len(self.arrows) == 0:
            return None
        return self.arrows[0].style

    @property
    def head_width(self):
        if len(self.arrows) == 0:
            return None
        return self.arrows[0].head_width

    @property
    def head_height(self):
        if len(self.arrows) == 0:
            return None
        return self.arrows[0].head_height

    def _num_points(self) -> int:
        return sum(a.x.size for a in self.arrows)

    def _coordinates(self) -> np.ndarray:
        xs = []
        ys = []
        for a in self.arrows:
            xs.append(a.x)
            ys.append(a.y)

        return np.vstack((np.concatenate(xs), np.concatenate(ys)))

    def add(self, a: Arrow) -> None:
        self.arrows.append(a)

    def matches(self, color: str, line_width: float, dash: str, style: int) -> bool:
        """Return True if style matches."""
        return (
                self.color == color
                and self.line_width == line_width
                and self.dash == dash
                and self.style == style
        )

    def to_lines_fills(self) -> tuple[Lines, Fills]:

        lines = Lines(color=self.color, width=self.line_width, dash=self.dash)
        fills = Fills(color=self.color)
        for arrow in self.arrows:
            lines.add_segment(arrow.x, arrow.y)

            if self.style == 0:
                # plain trangle head
                points = math_vectors.get_triangle_vertices(
                    base_center=np.array([arrow.x[-1], arrow.y[-1]]),
                    height=arrow.head_height,
                    vector_to_tip=np.array([arrow.x[1] - arrow.x[0], arrow.y[1] - arrow.y[0]]),
                    base_width=arrow.head_width
                )
                fills.add_segment(points[:, 0], points[:, 1])

                # TODO more arrow styles
            else:
                raise RuntimeError("Not supported arrow head style.")

        return lines, fills


class DrawingContainer:
    """Unified container for lines, fills, and text, with Plotly export."""

    def __init__(self):
        self.dots: list[Dots] = []
        self.lines: list[Lines] = []
        self.fills: list[Fills] = []
        self.texts: list[Texts] = []
        self.arrows: list[Arrows] = []
        # the location of None is when to draw itself (this allows layering)
        self.containers: list[DrawingContainer | None] = [None]

        self._coordinates = None

    def __str__(self):
        text = ""
        if self.dots:
            text += f"dots: {len(self.dots)} |"
        if self.lines:
            text += f"lines: {len(self.lines)} |"
        if self.fills:
            text += f"fills: {len(self.fills)} |"
        if self.texts:
            text += f"text: {len(self.texts)} |"
        if self.arrows:
            text += f"arrows: {len(self.arrows)} |"
        if self.containers:
            text += f"containers: {len(self.containers)} |"
        return text

    def coordinates(self) -> np.ndarray:
        if self._coordinates:
            return self._coordinates

        xs = []
        ys = []

        # 1. Group standard objects together to reduce code repetition
        standard_objects = self.dots + self.lines + self.fills + self.texts

        for obj in standard_objects:
            xs.append(obj.x)
            ys.append(obj.y)

        # 2. Handle arrows separately (since they use _x and _y)
        for arrow in self.arrows:
            c = arrow._coordinates()
            xs.append(c[0, :])
            ys.append(c[1, :])

        # 4. Concatenate and Stack
        # np.vstack creates a (2, N) array.
        x = np.concatenate(xs)
        y = np.concatenate(ys)
        x = x[x != None]
        y = y[y != None]
        coords = np.vstack((x, y))

        self._coordinates = coords
        return self._coordinates

    def center(self) -> np.ndarray:
        """ center of bounding box of molecule """
        return math_points.get_bounding_box_center(self.coordinates())

    def bounding_box(self) -> np.ndarray:
        return math_points.get_bounding_box(self.coordinates())

    def add_dot(self, dot: Dot):
        for d in self.dots:
            if d.matches(dot.color, dot.size):
                d.add_segment(dot.x, dot.y)
                return

        new_dot = Dots(dot.color, dot.size)
        new_dot.add_segment(dot.x, dot.y)
        self.dots.append(new_dot)

    def add_dots(self, dots: Dots):
        for d in self.dots:
            if d.matches(dots.color, dots.size):
                d.join(dots)
                return
        self.dots.append(copy.deepcopy(dots))

    def add_line(self, line: Line):
        for l in self.lines:
            if l.matches(line.color, line.width, line.dash):
                l.add_segment(line.x, line.y)
                return

        new_line = Lines(line.color, line.width, line.dash)
        new_line.add_segment(line.x, line.y)
        self.lines.append(new_line)

    def add_lines(self, lines: Lines):
        for d in self.lines:
            if d.matches(lines.color, lines.width, lines.dash):
                d.join(lines)
                return

        self.lines.append(copy.deepcopy(lines))

    def add_fill(self, fill: Fill) -> None:
        for f in self.fills:
            if f.matches(fill.color):
                f.add_segment(fill.x, fill.y)
                return

        new_fill = Fills(fill.color)
        new_fill.add_segment(fill.x, fill.y)
        self.fills.append(new_fill)

    def add_fills(self, fills: Fills):
        for d in self.fills:
            if d.matches(fills.color):
                d.join(fills)
                return

        self.fills.append(copy.deepcopy(fills))

    def add_text(self, text: Text) -> None:
        for f in self.texts:
            if f.matches(text.color, text.font, text.size):
                f.add_segment(text.x, text.y, text.symbol)
                return

        new_text = Texts(text.color, text.font, text.size, text.bold)
        new_text.add_segment(text.x, text.y, text.symbol)
        self.texts.append(new_text)

    def add_texts(self, texts: Texts):
        for d in self.texts:
            if d.matches(texts.color, texts.font, texts.size):
                d.join(texts)
                return

        self.texts.append(copy.deepcopy(texts))

    def add_arrow(self, arrow: Arrow) -> None:
        for a in self.arrows:
            if a.matches(arrow.color, arrow.line_width, arrow.dash, arrow.style):
                a.add(arrow)
                return

        new_arrow = Arrows()
        new_arrow.add(arrow)
        self.arrows.append(new_arrow)

    # Do not add add_arrows; it should not be needed as they are converted to lines/fills

    def add_objects(self, objs: Dot | Line | Fill | Text | Arrow | Sequence[Dot | Line | Fill | Text | Arrow]):
        if not isinstance(objs, Sequence):
            objs = [objs]

        for obj in objs:
            if isinstance(obj, Line):
                self.add_line(obj)
            elif isinstance(obj, Fill):
                self.add_fill(obj)
            elif isinstance(obj, Text):
                self.add_text(obj)
            elif isinstance(obj, Arrow):
                self.add_arrow(obj)
            elif isinstance(obj, Dot):
                self.add_dot(obj)
            else:
                raise RuntimeError(f"Unknown type {type(obj)}")

    def prepare_for_drawing(self):
        # call prior to plotting - some objects need to be converted into lines and fills
        self_obj = copy.copy(self)
        for a in self.arrows:
            a_line, a_fill = a.to_lines_fills()
            self_obj.lines.append(a_line)
            self_obj.fills.append(a_fill)

        # resolve containers and merge into a new one
        new_obj = self.__class__()
        for container in self.containers:
            if container is None:
                container = self_obj
            else:
                container = container.prepare_for_drawing()

            for obj in container.dots:
                new_obj.add_dots(obj)
            for obj in container.lines:
                new_obj.add_lines(obj)
            for obj in container.fills:
                new_obj.add_fills(obj)
            for obj in container.texts:
                new_obj.add_texts(obj)
            # arrows should be converted to text/fills already

        return new_obj
