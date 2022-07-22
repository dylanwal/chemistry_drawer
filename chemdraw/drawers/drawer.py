import plotly.graph_objs as go

from chemdraw.objects.molecule import Molecule
import chemdraw.drawers.draw_debug as draw_debug
import chemdraw.drawers.draw_title as draw_title
import chemdraw.drawers.draw_atoms as draw_atoms
import chemdraw.drawers.draw_bonds as draw_bonds
import chemdraw.drawers.draw_atom_numbers as draw_atom_numbers
import chemdraw.drawers.draw_bond_numbers as draw_bond_numbers
import chemdraw.drawers.draw_highlights as draw_highlights
import chemdraw.drawers.draw_ring_highlights as draw_ring_highlights


class DrawerConfig:
    drawers = {
        "bonds": {
            "function": draw_bonds.draw_bonds,
            "kwargs": ["bonds"]  # fig is added by default
        },
        "atoms": {
            "function": draw_atoms.draw_atoms,
            "kwargs": ["atoms"]  # fig is added by default
        },
        "title": {
            "function": draw_title.draw_title,
            "kwargs": ["title", "molecule"]  # fig is added by default
        },
        "debug": {
            "function": draw_debug.draw_debug,
            "kwargs": ["bonds", "atoms"]  # fig is added by default
        },
        "atom_numbers": {
            "function": draw_atom_numbers.draw_atom_numbers,
            "kwargs": ["atoms"]  # fig is added by default
        },
        "bond_numbers": {
            "function": draw_bond_numbers.draw_bond_numbers,
            "kwargs": ["bonds"]  # fig is added by default
        },
        "highlights": {
            "function": draw_highlights.draw_highlights,
            "kwargs": ["atoms", "bonds"]  # fig is added by default
        },
        "ring_highlights": {
            "function": draw_ring_highlights.draw_ring_highlight,
            "kwargs": ["rings"]  # fig is added by default
        }
    }

    def __init__(self):
        # general options
        self.draw_order = ["ring_highlights", "bonds", "atoms", "atom_numbers", "bond_numbers",
                           "debug", "title", "highlights"]
        self.options_fix_zoom = False

        # layout
        self.layout_background_color = "white"
        self.layout_auto_size = False
        self.layout_margin = dict(l=0, r=0, b=0, t=0, pad=0)
        self.layout_width = 600  # only used with layout_auto_scale is False
        self.layout_height = 600  # only used with layout_auto_scale is False
        self.layout_auto_scale = True  # only used with layout_auto_scale is False
        self.layout_range_x = [-5, 5]
        self.layout_range_y = [-5, 5]
        self.layout_show_axis = False
        self.layout_dragmode = "pan"

        # drawers
        self.bonds = draw_bonds.ConfigDrawerBonds()
        self.atoms = draw_atoms.ConfigDrawerAtoms()
        self.atom_numbers = draw_atom_numbers.ConfigDrawerAtomNumber()
        self.bond_numbers = draw_bond_numbers.ConfigDrawerBondNumber()
        self.title = draw_title.ConfigDrawerTitle()
        self.debug = draw_debug.ConfigDrawerDebug()
        self.highlights = draw_highlights.ConfigDrawerHighlights()
        self.ring_highlights = draw_ring_highlights.ConfigDrawerRingHighlights()

    def __repr__(self) -> str:
        return f"bonds: {self.bonds.show}, atoms: {self.atoms.show}, atom_numbers: {self.atom_numbers.show}, " \
               f"title: {self.title.show}, debug: {self.debug.debug}"


class Drawer:
    def __init__(self, molecule: str | Molecule, title: str = None, config: DrawerConfig = None):
        if isinstance(molecule, str):
            molecule = Molecule(molecule, name=molecule)
        self.molecule = molecule

        self.title = title
        self.config = config if config is not None else DrawerConfig()

    def __repr__(self) -> str:
        text = "Drawer for: "
        if self.title:
            text += str(self.title)
        else:
            text += str(self.molecule)

        return text

    def draw(self, fig: go.Figure = None, auto_open: bool = False) -> go.Figure:
        if fig is None:
            fig = go.Figure()

        fig = self._draw(fig)
        fig = self._layout(fig)

        if auto_open:
            fig.show()

        return fig

    def _draw(self, fig: go.Figure) -> go.Figure:
        import time
        for key in self.config.draw_order:
            start = time.time()
            func = self.config.drawers[key]["function"]
            kwargs = self._get_kwargs(key, self.config.drawers[key]["kwargs"])
            fig = func(fig, **kwargs)
            stop = time.time()
            print(key, stop-start)

        return fig

    def _get_kwargs(self, key: str, kwargs: list[str]) -> dict:
        kwargs_out = {"config": getattr(self.config, key)}
        if "title" in kwargs:
            kwargs_out["title"] = getattr(self, "title")
        if "molecule" in kwargs:
            kwargs_out["molecule"] = getattr(self, "molecule")
        if "bonds" in kwargs:
            kwargs_out["bonds"] = getattr(self.molecule, "bonds")
        if "atoms" in kwargs:
            kwargs_out["atoms"] = getattr(self.molecule, "atoms")
        if "rings" in kwargs:
            kwargs_out["rings"] = getattr(self.molecule, "rings")

        return kwargs_out

    def _layout(self, fig: go.Figure) -> go.Figure:
        layout_kwargs = {
            "showlegend": False,
            "plot_bgcolor": self.config.layout_background_color,
            "dragmode": self.config.layout_dragmode,
            "margin": self.config.layout_margin
        }
        if not self.config.layout_auto_size:
            layout_kwargs["width"] = self.config.layout_width
            layout_kwargs["height"] = self.config.layout_height

        xaxes_kwargs = {
            "visible": self.config.layout_show_axis,
            "range": self.config.layout_range_x,
            "fixedrange": self.config.options_fix_zoom,
            "layer": "below traces",
        }

        yaxes_kwargs = {
            "visible": self.config.layout_show_axis,
            "layer": "below traces"
        }
        if self.config.layout_auto_size:
            yaxes_kwargs["scaleanchor"] = "x"
            yaxes_kwargs["scaleratio"] = 1
        else:
            yaxes_kwargs["range"] = self.config.layout_range_y

        fig.update_layout(**layout_kwargs)
        fig.update_xaxes(**xaxes_kwargs)
        fig.update_yaxes(**yaxes_kwargs)
        return fig

    def draw_img(self, file_location: str = "molecule.svg") -> str:
        fig = self.draw()
        fig.write_image(file_location)
        return file_location

    def draw_html(self, file_location: str = "molecule.html", auto_open: str = False) -> str:
        fig = self.draw()
        fig.write_html(file_location, auto_open=auto_open)
        return file_location
