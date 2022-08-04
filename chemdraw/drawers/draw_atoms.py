import numpy as np
import plotly.graph_objs as go

from chemdraw.drawers.general_classes import Font
from chemdraw.objects.atoms import Atom


class ConfigDrawerAtoms:
    def __init__(self, parent):
        self.parent = parent

        self.show = True
        self.method = True  # True uses go.Scatter; very fast less options  || False uses add_annotations; slower
        self.font = Font(parent, family="Arial", size=40, bold=True, color="black", offset=0.3, top_offset=0.6)
        self.colors_add = False  # set 'method' to False
        self.font_color = "black"
        self.colors = {
            "C": "black",
            "O": "red",
            "N": "green",
            "S": "yellow"
        }
        self.show_carbons = False
        # self.align_offset = 0.3
        self.scatter_kwargs = dict(hoverinfo="skip")
        self.text_y_offset = 0.07

    def __repr__(self):
        return f"show: {self.show}"

    def get_text_y_offset(self):
        return self.text_y_offset


def draw_atoms(fig: go.Figure, config: ConfigDrawerAtoms, atoms: list[Atom]) -> go.Figure:
    if not config.show:
        return fig

    if config.method:
        return _add_atoms_with_scatter(fig, config, atoms)
    else:
        return _add_atoms_with_annotations(fig, config, atoms)


def _add_atoms_with_annotations(fig: go.Figure, config: ConfigDrawerAtoms, atoms: list[Atom]) -> go.Figure:
    for atom in atoms:
        if not config.show_carbons and atom.symbol == "C":
            continue  # skip drawing carbons

        symbol, x, y = _get_symbol(config, atom)
        font = config.font.get_attr("family", atom.font)
        font_size = config.font.get_attr("size", config.font.get_attr("size", atom.font))

        fig.add_annotation(
            x=x,
            y=y,
            text=symbol,
            showarrow=False,
            font=dict(
                family=font,
                size=font_size,
                color=_get_color(config, atom)
            ),
        )

    return fig


def _add_atoms_with_scatter(fig: go.Figure, config: ConfigDrawerAtoms, atoms: list[Atom]) -> go.Figure:
    xy = np.empty((int(len(atoms) * 1.5), 2), dtype="float64")
    counter = 0
    symbols = []
    for atom in atoms:
        if not config.show_carbons and atom.symbol == "C":
            continue  # skip drawing carbons
        symbol, x, y, direction = _get_symbol(config, atom)
        symbols.append(symbol)
        xy[counter, :] = [x, y - config.get_text_y_offset()]
        counter += 1

        # add hydrogens that are above or below atom
        if direction is not None:
            hydrogen_symbol = _get_hydrogen_symbol(atom)
            if config.font.get_attr("bold", atom.font):
                hydrogen_symbol = "<b>" + hydrogen_symbol + "</b>"
            symbols.append(hydrogen_symbol)
            top_offset = config.font.get_attr("top_offset", atom.font)
            if direction == "up":
                xy[counter, :] = [atom.coordinates[0], atom.coordinates[1] + top_offset - config.get_text_y_offset()]
            else:
                xy[counter, :] = [atom.coordinates[0], atom.coordinates[1] - top_offset - config.get_text_y_offset()]
            counter += 1

    fig.add_trace(
        go.Scatter(
            x=xy[:counter, 0], y=xy[:counter, 1],
            mode="text",
            text=symbols,
            textfont=dict(
                family=config.font.family,
                color=config.font.color,
                size=max([int(config.font.get_attr("size", atoms[0].font)), 1])
            ),
            **config.scatter_kwargs
        ))

    return fig


def _get_symbol(config: ConfigDrawerAtoms, atom: Atom) -> tuple[str, float, float, str | None]:
    # add hydrogen
    symbol, align, direction = _add_hydrogen_text(atom)

    if config.font.get_attr("bold", atom.font):
        symbol = "<b>" + symbol + "</b>"

    x, y = _text_alignment(config, atom, align)
    return symbol, x, y, direction


def _add_hydrogen_text(atom: Atom) -> tuple[str, str, str | None]:
    """ add hydrogen and subscript to atoms"""
    if atom.number_hydrogens < 1:
        return atom.symbol, "center", None

    if abs(atom.vector[0]) > abs(atom.vector[1]) or len(atom.bonds) != 2:
        if atom.vector[0] < 0:
            # hydrogen on left side of atom
            return _get_hydrogen_symbol(atom) + atom.symbol, "left", None
        else:
            # hydrogen on right side of atom
            return atom.symbol + _get_hydrogen_symbol(atom), "right", None
    else:
        if atom.vector[1] > 0:
            # hydrogen on top side of atom
            return atom.symbol, "center", "up"
        else:
            # hydrogen on right side of atom
            return atom.symbol, "center", "down"


def _get_hydrogen_symbol(atom: Atom) -> str:
    if atom.number_hydrogens < 1:
        return ""

    if atom.number_hydrogens == 1:
        subscript = ""
    else:
        subscript = "<sub>" + str(atom.number_hydrogens) + "</sub>"

    return "H" + subscript


def _text_alignment(config: ConfigDrawerAtoms, atom: Atom, align: str) -> tuple[float, float]:
    offset = config.font.get_attr("offset", atom.font)
    if align == "center":
        return atom.coordinates[0], atom.coordinates[1]
    elif align == "left":
        return atom.coordinates[0] - offset, atom.coordinates[1]
    elif align == "right":
        return atom.coordinates[0] + offset, atom.coordinates[1]

    raise ValueError("Coding error")


def _get_color(config: ConfigDrawerAtoms, atom: Atom) -> str:
    if config.colors_add:
        if atom.symbol in config.colors:
            return config.colors[atom.symbol]

    return config.font.get_attr("color", atom.font)
