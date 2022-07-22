import numpy as np
import plotly.graph_objs as go

from chemdraw.objects.atoms import Atom


class ConfigDrawerAtoms:
    show = True
    method = True  # True uses go.Scatter; very fast less options  || False uses add_annotations; slower
    font = "Arial"
    font_bold = True
    font_size = 50
    colors_add = False  # set 'method' to False
    font_color = "black"
    colors = {
        "C": "black",
        "O": "red",
        "N": "green",
        "S": "yellow"
    }
    show_carbons = False
    background_shape = "octagon"  # tight (set 'method' to False), circle, square, hexagon, octagon, diamond
    marker_size = 50  # used when background_shape != tight
    bgcolor = "white"  # set to None to remove bgcolor
    borderpad = 0  # used when background_shape != tight
    align_offset = 0.3
    scatter_kwargs = dict(hoverinfo="skip")

    def __repr__(self):
        return f"show: {self.show}"


def draw_atoms(fig: go.Figure, config: ConfigDrawerAtoms, atoms: list[Atom]) -> go.Figure:
    if not config.show:
        return fig

    if config.method:
        fig = _add_background_with_markers(fig, config, atoms)
        return _add_atoms_with_scatter(fig, config, atoms)
    else:
        if config.background_shape != "tight":
            fig = _add_background_with_markers(fig, config, atoms)
        return _add_atoms_with_annotations(fig, config, atoms)


def _add_atoms_with_annotations(fig: go.Figure, config: ConfigDrawerAtoms, atoms: list[Atom]) -> go.Figure:
    for atom in atoms:
        if not config.show_carbons and atom.symbol == "C":
            continue  # skip drawing carbons

        symbol, x, y = _get_symbol(config, atom)

        fig.add_annotation(
            x=x,
            y=y,
            text=symbol,
            showarrow=False,
            font=dict(
                family=config.font,
                size=config.font_size,
                color=_get_color(config, atom.symbol)
            ),
            bgcolor=config.bgcolor if config.background_shape == "tight" else None,
            # borderwidth=config.borderwidth,
            borderpad=config.borderpad,
            # opacity=0.8
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

    fig.add_trace(go.Scatter(x=xy[:counter, 0], y=xy[:counter, 1], mode="text", text=symbols,
                             textfont=dict(family=config.font, color=config.font_color, size=config.font_size),
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

    if atom.vector[0] > 0:
        # hydrogen on left side of atom
        return "H" + subscript + atom.symbol, "left"
    else:
        # hydrogens on right side of atom
        return atom.symbol + "H" + subscript, "right"


def _text_alignment(config: ConfigDrawerAtoms, atom: Atom, align: str) -> tuple[float, float]:
    if align == "center":
        return atom.position[0], atom.position[1]
    elif align == "left":
        return atom.position[0] - config.align_offset, atom.position[1]
    elif align == "right":
        return atom.position[0] + config.align_offset, atom.position[1]


def _get_color(config: ConfigDrawerAtoms, atom: str) -> str:
    if config.colors_add:
        if atom in config.colors:
            return config.colors[atom]

    return config.font_color


def _add_background_with_markers(fig: go.Figure, config: ConfigDrawerAtoms, atoms: list[Atom]) -> go.Figure:
    xy = np.empty((len(atoms), 2), dtype="float64")

    counter = 0
    for atom in atoms:
        if not config.show_carbons and atom.symbol == "C":
            continue  # skip drawing carbons

        xy[counter] = atom.position
        counter += 1

    xy = xy[:counter, :]

    fig.add_trace(
        go.Scatter(x=xy[:, 0], y=xy[:, 1], mode="markers",
                   marker=dict(color=config.bgcolor, size=config.marker_size, symbol=config.background_shape)
                   )
    )

    return fig
