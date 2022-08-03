import numpy as np
import plotly.graph_objs as go

from chemdraw.objects.atoms import Atom


class ConfigDrawerAtoms:
    def __init__(self, parent):
        self.parent = parent

        self.show = True
        self.method = True  # True uses go.Scatter; very fast less options  || False uses add_annotations; slower
        self.font = "Arial"
        self.font_bold = True
        self.font_size = 40
        self.colors_add = False  # set 'method' to False
        self.font_color = "black"
        self.colors = {
            "C": "black",
            "O": "red",
            "N": "green",
            "S": "yellow"
        }
        self.show_carbons = False
        self.align_offset = 0.3
        self.scatter_kwargs = dict(hoverinfo="skip")
        self.text_y_offset = 0.07

    def __repr__(self):
        return f"show: {self.show}"

    def get_font_size(self) -> float:
        font_size = self.font_size / self.parent._scaling
        return font_size


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
        font = config.font if atom.font is None else atom.font
        font_size = config.font_size if atom.font_size is None else atom.font_size

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
    xy = np.empty((len(atoms), 2), dtype="float64")
    counter = 0
    symbols = []
    for atom in atoms:
        if not config.show_carbons and atom.symbol == "C":
            continue  # skip drawing carbons
        symbol, x, y = _get_symbol(config, atom)
        symbols.append(symbol)
        xy[counter, :] = [x, y]
        counter += 1

    fig.add_trace(go.Scatter(x=xy[:counter, 0], y=xy[:counter, 1] - config.text_y_offset, mode="text", text=symbols,
                             textfont=dict(family=config.font, color=config.font_color, size=config.get_font_size()),
                             **config.scatter_kwargs))

    return fig


def _get_symbol(config: ConfigDrawerAtoms, atom: Atom) -> tuple[str, float, float]:
    # add hydrogen
    symbol, align = _add_hydrogen_text(atom)

    if config.font_bold:
        symbol = "<b>" + symbol + "</b>"

    x, y = _text_alignment(config, atom, align)
    return symbol, x, y


def _add_hydrogen_text(atom: Atom) -> tuple[str, str]:
    """ add hydrogen and subscript to atoms"""
    if atom.number_hydrogens < 1:
        return atom.symbol, "center"

    if atom.number_hydrogens == 1:
        subscript = ""
    else:
        subscript = "<sub>" + str(atom.number_hydrogens) + "</sub>"

    if atom.vector[0] < 0:
        # hydrogen on left side of atom
        return "H" + subscript + atom.symbol, "left"
    else:
        # hydrogen on right side of atom
        return atom.symbol + "H" + subscript, "right"


def _text_alignment(config: ConfigDrawerAtoms, atom: Atom, align: str) -> tuple[float, float]:
    if align == "center":
        return atom.coordinates[0], atom.coordinates[1]
    elif align == "left":
        return atom.coordinates[0] - config.align_offset, atom.coordinates[1]
    elif align == "right":
        return atom.coordinates[0] + config.align_offset, atom.coordinates[1]


def _get_color(config: ConfigDrawerAtoms, atom: Atom) -> str:
    if atom.font_color is not None:
        return atom.font_color

    if config.colors_add:
        if atom.symbol in config.colors:
            return config.colors[atom.symbol]

    return config.font_color
