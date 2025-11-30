from __future__ import annotations

import warnings
from typing import Sequence
import copy
from itertools import chain

import numpy as np

import chemdraw.utils.math_vectors as math_vectors
import chemdraw.utils.math_points as math_points
import chemdraw.utils.text_size as text_size
from chemdraw.config.style_template import STYLE_TEMPLATE


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

    def box_coordinates(self) -> np.ndarray:
        pts = np.vstack((self.x, self.y))
        min_vals = np.min(pts, axis=1)
        max_vals = np.max(pts, axis=1)
        if STYLE_TEMPLATE.plotter == "matplotlib":
            radius = (self.size/3.145)**0.5 * STYLE_TEMPLATE.dot_scaler  # area related
        else:
            radius = self.size * STYLE_TEMPLATE.dot_scaler # diameter related

        corners = np.array(
            [
                [min_vals[0]-radius, min_vals[0]-radius, max_vals[0]+radius, max_vals[0]+radius],
                [min_vals[1]-radius, max_vals[1]-radius, max_vals[1]+radius, min_vals[1]+radius],
            ]
        )

        return corners

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
        self.symbols: list[str | list[str] | tuple[str]] = []  # list[str] will be converted to page returns
        self.color = color
        self.font = font
        self.size = size
        self.bold = bold

        self._up_to_date = False
        self.text_dim: tuple[float] = ()

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

    def box_coordinates(self):
        # if len(self.symbols) > 10:
        #     # get the outermost points
        #     top_index = np.argmax(self.y)
        #     bottom_index = np.argmin(self.y)
        #     left_index = np.argmin(self.x)
        #     right_index = np.argmax(self.x)
        #     indexes = [top_index, bottom_index, left_index, right_index]
        #
        #     # get any large strings
        #     for i, s in enumerate(self.symbols):
        #         if len(self.symbols) > 10 or isinstance(self.symbols[i], list) and len(self.symbols[0]) > 10:
        #             indexes.append(i)
        # else:
        indexes = range(len(self.symbols))

        xs, ys = [], []
        for i in indexes:
            width, height = text_size.get_text_dimensions(self.symbols[i], self.font, self.size)
            xs.append((self.x[i]-width/2, self.x[i]-width/2, self.x[i]+width/2, self.x[i]+width/2))
            ys.append((self.y[i]-height/2, self.y[i]+height/2, self.y[i]+height/2, self.y[i]-height/2))

        points = np.vstack((np.concatenate(xs), np.concatenate(ys)))
        return math_points.get_bounding_box(points)


    def prepare_for_drawing(self, new_line: str):
        symbols = []
        for i in self.symbols:
            if isinstance(i, list) or isinstance(i, tuple):
                symbols.append(f"{new_line}".join(i))
            else:
                symbols.append(i)
        self.symbols = symbols


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

    def join(self, other: Arrows) -> None:
        self.arrows.extend(other.arrows)

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

    def __init__(self, layer_type: str | None = None):
        self.dots: list[Dots] = []
        self.lines: list[Lines] = []
        self.fills: list[Fills] = []
        self.texts: list[Texts] = []
        self.arrows: list[Arrows] = []
        # the location of None is when to draw itself (this allows layering)
        self.containers: list[DrawingContainer | None] = [None]  # limit to one layer deep
        self.layer_type = layer_type

        self._box_coordinates = None

    def __str__(self):
        text = ""
        if self.layer_type is not None:
            text += f"layer_type: {self.layer_type} |"
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

    def is_empty(self) -> bool:
        return (len(self.dots) == 0 and len(self.lines) == 0 and len(self.fills) == 0 and len(self.texts) == 0 and
                len(self.arrows) == 0 and len(self.containers) == 1)

    def bounding_box(self) -> np.ndarray:
        if self._box_coordinates is not None:
            return self._box_coordinates

        if self.is_empty():
            return np.array([])

        if len(self.containers) > 1:
            container = self.prepare_for_drawing()
        else:
            container = self

        xs = []
        ys = []

        # 1. Group standard objects together to reduce code repetition
        for obj in (container.lines + container.fills):
            xs.append(obj.x)
            ys.append(obj.y)

        # 2. Handle arrows separately (since they use _x and _y)
        for arrow in container.arrows:
            c = arrow._coordinates()
            xs.append(c[0, :])
            ys.append(c[1, :])

        for text in (container.texts + container.dots):
            c = text.box_coordinates()
            xs.append(c[0, :])
            ys.append(c[1, :])

        # 3. Handle containers separately
        for c in self.containers:
            if c is None or c.is_empty():
                continue
            cc = c.bounding_box()
            xs.append(cc[0])
            ys.append(cc[1])

        # 4. Concatenate and Stack
        # np.vstack creates a (2, N) array.
        x = np.concatenate(xs)
        y = np.concatenate(ys)
        x = x[x != None]
        y = y[y != None]
        coords = np.vstack((x, y))

        coords = np.asarray(coords, dtype=float)

        return math_points.get_bounding_box(coords)

    def center(self) -> np.ndarray:
        """ center of bounding box of molecule """
        return np.mean(self.bounding_box(), axis=1)

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

    def add_arrows(self, arrows: Arrows):
        for a in self.arrows:
            if a.matches(arrows.color, arrows.line_width, arrows.dash, arrows.style):
                a.join(arrows)
                return

        self.arrows.append(copy.deepcopy(arrows))

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
        for c in self_obj.containers:
            if c is None:
                continue
            c.prepare_for_drawing()

        return self_obj

    def move(self, x: float, y: float):
        if len(self.arrows) > 0:
            raise RuntimeError("Call prepare_for_drawing() first.")

        for obj in chain(self.dots, self.lines, self.fills, self.texts):
            mask_none = (obj.x != None)
            obj.x[mask_none] += x
            obj.y[mask_none] += y

        for c in self.containers:
            if c is None:
                continue
            c.move(x, y)


    def join(self, container: DrawingContainer) -> None:
        # join current layer
        for obj in container.dots:
            self.add_dots(obj)
        for obj in container.lines:
            self.add_lines(obj)
        for obj in container.fills:
            self.add_fills(obj)
        for obj in container.texts:
            self.add_texts(obj)
        for obj in container.arrows:
            self.add_arrows(obj)
        for c in container.containers:
            if c is None:
                continue
            for cc in self.containers:  # only join containers from same layer
                if cc is None:
                    continue
                if c.layer_type == cc.layer_type:
                    cc.join(c)
                    break
            else:
                self.containers.append(c)


class DrawingContainerGrid:
    def __init__(self, shape: Sequence[int] | None = None):
        self.containers: list[DrawingContainer] = []
        self.shape: Sequence[int] | None = shape

    def add(self, container: DrawingContainer):
        self.containers.append(container)

    def _get_shape(self) -> Sequence[int]:
        if self.shape is not None and len(self.shape) == 2:
            if self.shape[0] * self.shape[1] > len(self.containers):
                return [self.shape[1]] * self.shape[0]
            warnings.warn(
                f"`shape` for grid drawing does not match number of molecules. "
                f"Reverting to default shape."
            )
        elif self.shape is not None:
            total_grid_spots = sum(self.shape)
            if total_grid_spots > len(self.containers):
                return self.shape
            warnings.warn(
                f"`shape` for grid drawing does not match number of molecules. "
                f"Reverting to default shape."
            )

        # auto determine shape
        num_cols = int(np.sqrt(len(self.containers)))
        num_rows = len(self.containers) // num_cols + (1 if len(self.containers) % num_cols else 0)
        return [num_cols] * num_rows

    def prepare_for_drawing(self) -> DrawingContainer:
        new_obj = DrawingContainer()

        prep_containers = [container.prepare_for_drawing() for container in self.containers]

        bounding_box = [c.bounding_box() for c in prep_containers]
        cell_width = max(np.max(b[0]) - np.min(b[0]) for b in bounding_box)
        cell_height = max(np.max(b[1]) - np.min(b[1]) for b in bounding_box)
        grid_shape = self._get_shape()

        # loop through containers and move them
        count = 0
        DONE = False
        for i, len_row in enumerate(grid_shape):
            if DONE:
                break
            for j in range(len_row):
                prep_containers[count].move(cell_width*j, cell_height*i)
                count += 1
                if count == len(prep_containers):
                    DONE = True
                    break

        # join similar layers
        for c in prep_containers:
            new_obj.join(c)

        return new_obj
