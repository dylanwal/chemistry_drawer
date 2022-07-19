from rdkit import Chem
import plotly.graph_objs as go

from chemdraw.mole_file import MoleFile, BondType, Bond, Atom
from chemdraw.utils import shorten_line


class DrawerConfig:
    def __init__(self):
        # atom options
        self.atom_font = "Arial"
        self.atom_font_bold = True
        self.atom_font_size = 50
        self.atom_colors_add = False
        self.atom_font_color_default = "black"
        self.atom_colors = {
            "C": "black",
            "O": "red",
            "N": "green",
            "S": "yellow"
        }
        self.atom_show_carbons = False
        self.atom_background_shape = "octagon"  # tight, circle, square, hexagon, octagon, diamond
        self.atom_marker_size = 50  # used when atom_background_shape != tight
        self.atom_bgcolor = "white"  # set to None to remove bgcolor
        self.atom_borderpad = 0  # used when atom_background_shape != tight
        self.atom_align_offset = 0.4

        # bond options
        self.bond_width = 8
        self.bond_color = "black"
        self.bond_triple_offset = 0.23
        self.bond_double_offset = 0.4
        self.bond_double_offset_length = 0.7  # [0 - 1] 1 = full length; <1 = shorter
        self.bond_double_center_length = 1.1  # [1 - 1.5] 1 = full length; >1 = longer

        # title
        self.title_show = True
        self.title_location = "bottom"  # options = ["top", "bottom"]
        self.title_font = "Arial"
        self.title_font_color = "black"
        self.title_font_size = 32
        self.title_font_bold = True
        self.title_auto_wrap = True
        self.title_auto_wrap_length = 30
        self.title_pad_structure = 1
        self.title_line_height = 0.3

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

        # general options
        self.fix_zoom = False

        # debug options (can significantly increase render times 1 seconds -> 10 seconds)
        self.center_point = False
        self.bond_vector = False
        self.bond_perpendicular = False
        self.atom_vector = False


class Drawer:
    def __init__(self, molecule: str | MoleFile, title: str = None, config: DrawerConfig = None):
        if isinstance(molecule, str):
            mol = Chem.MolFromSmiles(molecule)
            molecule = MoleFile(Chem.MolToMolBlock(mol), name=molecule)

        self.molecule = molecule
        self.title = title
        self.config = config if config is not None else DrawerConfig()

    def draw(self, fig: go.Figure = None, auto_open: bool = False) -> go.Figure:
        if fig is None:
            fig = go.Figure()

        fig = self._draw(fig)
        fig = self._layout(fig)

        if auto_open:
            fig.show()

        return fig

    def _draw(self, fig: go.Figure) -> go.Figure:
        fig = self._draw_bonds(fig)
        if self.config.atom_background_shape != "tight":
            fig = self._add_atom_background_with_markers(fig)
        fig = self._draw_atoms(fig)
        fig = self._add_title(fig)

        # debug plotting
        if self.config.center_point:
            fig.add_trace(go.Scatter(x=[0], y=[0], mode="markers", marker=dict(color="red", size=5)))
        if self.config.bond_vector:
            fig = self._add_bond_vectors(fig)
        if self.config.bond_perpendicular:
            fig = self._add_bond_perpendicular(fig)
        if self.config.atom_vector:
            fig = self._add_atom_vector(fig)

        return fig

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
            "fixedrange": self.config.fix_zoom,
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

    ###### title ###########################################################################################################
    def _add_title(self, fig: go.Figure) -> go.Figure:
        if not self.config.title_show or self.title is None:
            return fig

        title = self._get_title_text()
        x, y = self._get_title_position(title)
        fig.add_annotation(
            x=x,
            y=y,
            text=title,
            showarrow=False,
            align="center",
            font=dict(
                family=self.config.title_font,
                size=self.config.title_font_size,
                color=self.config.title_font_color
            )
        )

        return fig

    def _get_title_text(self) -> str:
        title = self.title
        if self.config.title_auto_wrap:
            number_of_lines = int(len(title) / self.config.title_auto_wrap_length) + 1
            list_title = [title[i::number_of_lines] for i in range(number_of_lines)]
            title = "<br>".join(list_title)

        if self.config.title_font_bold:
            title = "<b>" + title + "</b>"

        return title

    def _get_title_position(self, title: str):
        lines_of_text = title.count("<br>")

        # get y
        if self.config.title_location == "top":
            y = self.molecule.get_top_atom().y
            y += self.config.title_pad_structure
            y += self.config.title_line_height * lines_of_text
        elif self.config.title_location == "bottom":
            y = self.molecule.get_bottom_atom().y
            y -= self.config.title_pad_structure
            y -= self.config.title_line_height * lines_of_text
        else:
            raise KeyError(f"Invalid title location. {self.config.title_location}")

        # get x
        x = self.molecule.position[0]

        return x, y

    ###### atoms ###########################################################################################################
    def _draw_atoms(self, fig: go.Figure) -> go.Figure:
        for atom in self.molecule.atoms:
            if not self.config.atom_show_carbons and atom.symbol == "C":
                continue  # skip drawing carbons

            symbol_text, align = self._get_atom_text(atom)
            x, y = self._atom_text_alignment(atom.x, atom.y, align)

            fig.add_annotation(
                x=x,
                y=y,
                text=symbol_text,
                showarrow=False,
                font=dict(
                    family=self.config.atom_font,
                    size=self.config.atom_font_size,
                    color=self._get_atom_color(atom.symbol)
                ),
                bgcolor=self.config.atom_bgcolor if self.config.atom_background_shape == "tight" else None,
                # borderwidth=self.config.atom_borderwidth,
                borderpad=self.config.atom_borderpad,
                # opacity=0.8
            )

        return fig

    def _get_atom_text(self, atom: Atom) -> tuple[str, str]:
        # add hydrogen
        symbol, align = self._add_hydrogen_text(atom)

        if self.config.atom_font_bold:
            symbol = "<b>" + symbol + "</b>"

        return symbol, align

    @staticmethod
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

    def _get_atom_color(self, atom: str) -> str:
        if self.config.atom_colors_add:
            if atom in self.config.atom_colors:
                return self.config.atom_colors[atom]

        return self.config.atom_font_color_default

    def _atom_text_alignment(self, x, y, align) -> tuple[float, float]:
        if align == "center":
            return x, y
        elif align == "left":
            return x - self.config.atom_align_offset, y
        elif align == "right":
            return x + self.config.atom_align_offset, y

    def _add_atom_background_with_markers(self, fig: go.Figure) -> go.Figure:
        x_data = []
        y_data = []
        for atom in self.molecule.atoms:
            if not self.config.atom_show_carbons and atom.symbol == "C":
                continue  # skip drawing carbons

            x_data.append(atom.x)
            y_data.append(atom.y)

        fig.add_trace(
            go.Scatter(x=x_data, y=y_data, mode="markers",
                       marker=dict(
                           color=self.config.atom_bgcolor,
                           size=self.config.atom_marker_size,
                           symbol=self.config.atom_background_shape
                       )
                       )
        )

        return fig

    ###### Bonds ###########################################################################################################
    def _draw_bonds(self, fig: go.Figure) -> go.Figure:
        for bond in self.molecule.bonds:
            if bond.type_ == BondType.single:
                fig = self._bond_single(fig, bond)
            elif bond.type_ == BondType.double:
                if bond.alignment == 0:
                    fig = self._bond_double_center(fig, bond)
                else:
                    fig = self._bond_double_offset(fig, bond)
            else:
                fig = self._bond_triple(fig, bond)

        return fig

    @staticmethod
    def _draw_bond_on_fig(fig, x, y, color, width) -> go.Figure:
        return fig.add_trace(
            go.Scatter(x=x, y=y, mode="lines",
                       line=dict(color=color, width=width), cliponaxis=False)
        )

    def _bond_single(self, fig: go.Figure, bond: Bond) -> go.Figure:
        return self._draw_bond_on_fig(
            fig, x=bond.x, y=bond.y,
            color=self.config.bond_color,
            width=self.config.bond_width
        )

    def _bond_double_center(self, fig: go.Figure, bond: Bond) -> go.Figure:
        x_left = bond.x + bond.perpendicular[0] * self.config.bond_double_offset/2
        x_right = bond.x - bond.perpendicular[0] * self.config.bond_double_offset/2
        y_left = bond.y + bond.perpendicular[1] * self.config.bond_double_offset/2
        y_right = bond.y - bond.perpendicular[1] * self.config.bond_double_offset/2
        if self.config.bond_double_center_length != 1:
            x0, x1, y0, y1 = shorten_line(x_left[0], x_left[1], y_left[0], y_left[1],
                                          self.config.bond_double_center_length)
            x_left = [x0, x1]
            y_left = [y0, y1]
            x0, x1, y0, y1 = shorten_line(x_right[0], x_right[1], y_right[0], y_right[1],
                                          self.config.bond_double_center_length)
            x_right = [x0, x1]
            y_right = [y0, y1]

        # left
        fig = self._draw_bond_on_fig(fig, x=x_left, y=y_left,
                                     color=self.config.bond_color, width=self.config.bond_width)
        # right
        fig = self._draw_bond_on_fig(fig, x=x_right, y=y_right,
                                     color=self.config.bond_color, width=self.config.bond_width)
        return fig

    def _bond_double_offset(self, fig: go.Figure, bond: Bond) -> go.Figure:
        if bond.alignment == 1:  # same side as perpendicular
            x_off = bond.x + bond.perpendicular[0] * self.config.bond_double_offset
            y_off = bond.y + bond.perpendicular[1] * self.config.bond_double_offset
        else:  # opposite side perpendicular
            x_off = bond.x - bond.perpendicular[0] * self.config.bond_double_offset
            y_off = bond.y - bond.perpendicular[1] * self.config.bond_double_offset

        # center
        fig = self._draw_bond_on_fig(fig, x=bond.x, y=bond.y,
                                     color=self.config.bond_color, width=self.config.bond_width)
        # right/left
        if self.config.bond_double_offset_length != 1:
            x0, x1, y0, y1 = shorten_line(x_off[0], x_off[1], y_off[0], y_off[1],
                                          self.config.bond_double_offset_length)
            x_off = [x0, x1]
            y_off = [y0, y1]

        fig = self._draw_bond_on_fig(fig, x=x_off, y=y_off,
                                     color=self.config.bond_color, width=self.config.bond_width)
        return fig

    def _bond_triple(self, fig: go.Figure, bond: Bond) -> go.Figure:
        x_left = bond.x + bond.perpendicular[0] * self.config.bond_triple_offset
        x_right = bond.x - bond.perpendicular[0] * self.config.bond_triple_offset
        y_left = bond.y + bond.perpendicular[1] * self.config.bond_triple_offset
        y_right = bond.y - bond.perpendicular[1] * self.config.bond_triple_offset

        # center
        fig = self._draw_bond_on_fig(fig, x=bond.x, y=bond.y,
                                     color=self.config.bond_color, width=self.config.bond_width)
        # left
        fig = self._draw_bond_on_fig(fig, x=x_left, y=y_left,
                                     color=self.config.bond_color, width=self.config.bond_width)
        # right
        fig = self._draw_bond_on_fig(fig, x=x_right, y=y_right,
                                     color=self.config.bond_color, width=self.config.bond_width)
        return fig

    ###### saving #########################################################################################################
    def draw_img(self, file_location: str = "molecule.svg") -> str:
        fig = self.draw()
        fig.write_image(file_location)
        return file_location

    def draw_html(self, file_location: str = "molecule.html", auto_open: str = False) -> str:
        fig = self.draw()
        fig.write_html(file_location, auto_open=auto_open)
        return file_location

    ###### debug #######################################################################################################
    def _add_bond_vectors(self, fig: go.Figure) -> go.Figure:
        for bond in self.molecule.bonds:
            fig.add_annotation(
                x=bond.center[0] + bond.vector[0],
                y=bond.center[1] + bond.vector[1],
                ax=bond.center[0],
                ay=bond.center[1],
                xref='x',
                yref='y',
                axref='x',
                ayref='y',
                showarrow=True,
                arrowhead=3,
                arrowsize=1,
                arrowwidth=1,
                arrowcolor="green"
            )

        return fig

    def _add_bond_perpendicular(self, fig: go.Figure) -> go.Figure:
        for bond in self.molecule.bonds:
            fig.add_annotation(
                x=bond.center[0] + bond.perpendicular[0],
                y=bond.center[1] + bond.perpendicular[1],
                ax=bond.center[0],
                ay=bond.center[1],
                xref='x',
                yref='y',
                axref='x',
                ayref='y',
                showarrow=True,
                arrowhead=3,
                arrowsize=1,
                arrowwidth=1,
                arrowcolor="blue"
            )

        return fig

    def _add_atom_vector(self, fig: go.Figure) -> go.Figure:
        for atom in self.molecule.atoms:
            fig.add_annotation(
                x=atom.x + atom.vector[0],
                y=atom.y + atom.vector[1],
                ax=atom.x,
                ay=atom.y,
                xref='x',
                yref='y',
                axref='x',
                ayref='y',
                showarrow=True,
                arrowhead=3,
                arrowsize=1,
                arrowwidth=1,
                arrowcolor="red"
            )

        return fig

