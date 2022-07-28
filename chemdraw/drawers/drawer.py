
import plotly.graph_objs as go

from chemdraw.objects.molecule import Molecule
import chemdraw.drawers.layout as layout
import chemdraw.drawers.draw_debug as draw_debug
import chemdraw.drawers.draw_title as draw_title
import chemdraw.drawers.draw_atoms as draw_atoms
import chemdraw.drawers.draw_bonds as draw_bonds
import chemdraw.drawers.draw_atom_numbers as draw_atom_numbers
import chemdraw.drawers.draw_bond_numbers as draw_bond_numbers
import chemdraw.drawers.draw_ring_numbers as draw_ring_numbers
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
            "kwargs": ["bonds", "atoms", "molecule"]  # fig is added by default
        },
        "atom_numbers": {
            "function": draw_atom_numbers.draw_atom_numbers,
            "kwargs": ["atoms"]  # fig is added by default
        },
        "bond_numbers": {
            "function": draw_bond_numbers.draw_bond_numbers,
            "kwargs": ["bonds"]  # fig is added by default
        },
        "ring_numbers": {
            "function": draw_ring_numbers.draw_ring_numbers,
            "kwargs": ["rings"]  # fig is added by default
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
        self.draw_order = ["ring_highlights", "highlights", "bonds", "atoms", "atom_numbers", "bond_numbers", "ring_numbers",
                           "debug", "title"]

        self.layout = layout.ConfigLayout(self)
        self.bonds = draw_bonds.ConfigDrawerBonds(self)
        self.atoms = draw_atoms.ConfigDrawerAtoms(self)
        self.atom_numbers = draw_atom_numbers.ConfigDrawerAtomNumber(self)
        self.bond_numbers = draw_bond_numbers.ConfigDrawerBondNumber(self)
        self.ring_numbers = draw_ring_numbers.ConfigDrawerRingNumber(self)
        self.title = draw_title.ConfigDrawerTitle(self)
        self.debug = draw_debug.ConfigDrawerDebug(self)
        self.highlights = draw_highlights.ConfigDrawerHighlights(self)
        self.ring_highlights = draw_ring_highlights.ConfigDrawerRingHighlights(self)

    def __repr__(self) -> str:
        return f"bonds: {self.bonds.show}, atoms: {self.atoms.show}, atom_numbers: {self.atom_numbers.show}, " \
               f"title: {self.title.show}, debug: {self.debug.debug}"

    @property
    def _scaling(self) -> float:
        return self.layout.scaling


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
        fig = self.config.layout.apply_layout(fig)

        if auto_open:
            fig.show()

        return fig

    def _draw(self, fig: go.Figure) -> go.Figure:
        self.config.layout.get_scaling(self.molecule, self.title)

        for key in self.config.draw_order:
            func = self.config.drawers[key]["function"]
            kwargs = self._get_kwargs(key, self.config.drawers[key]["kwargs"])
            fig = func(fig, **kwargs)

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

    def draw_img(self, file_location: str = "molecule.svg", transparent_background: bool = True) -> str:
        if transparent_background:
            self.config.layout.background_color = "rgba(0,0,0,0)"

        fig = self.draw()
        fig.write_image(file_location)
        return file_location

    def draw_html(self, file_location: str = "molecule.html", auto_open: str = False) -> str:
        fig = self.draw()
        fig.write_html(file_location, auto_open=auto_open)
        return file_location
