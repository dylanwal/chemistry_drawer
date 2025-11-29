import pathlib
import warnings

import yaml


class StyleTemplate:
    """ For styling the molecule's look (no parameters that are plotting package dependent). """

    def __init__(self):
        self.plotter = "matplotlib"  # "plotly"
        self.sub_plotter = None  # None or {"matplotlib": ("paths",)}
        self.auto_rotate = False # rotates molecule longest axis to [1,0]  or [1,0,0]
        self.auto_center = True  # move bound box center to [0, 0]

        # self.show_hydrogens = False
        # self.methyl = None # or "Me"


        ## plotting
        self.plot_width = 700
        self.plot_height = 560
        self.plot_background_color = "white"  # "rgba(0,0,0,0)"
        self.plot_buffer = 0  # in percent
        self.plot_buffer_abs = 0.2 # in absolute

        ## bond
        self.bond_color = "black"
        self.bond_width = 2
        self.bond_offset = 0.67
        self.bond_double_offset = 0.25  # of double bond perpendicular
        self.bond_double_center_length = 0.65  # [1 - 1.5] 1 = full length; >1 = longer
        self.bond_double_center_length_double = 0.4
        self.bond_double_offset_length = 0.75  # [0 - 1] 1 = full length; <1 = shorter
        self.bond_triple_offset = 0.125  # of triple bond perpendicular
        self.bond_triple_length = 1
        self.bond_stereo_offset = 0.23  # how wide is the triangle
        self.bond_stereo_wedge_number_distance = 0.2
        # self.bond_stereo_wedge_line_width = 6

        ## atom
        self.atom_show_carbons = False  # show carbon atoms
        # self.atom_prefix = ""  # useful for invisible text modifiers
        # self.atom_suffix = "" # useful for invisible text modifiers
        self.atom_text_x_offset = 0.1
        self.atom_text_y_offset = 0.07
        self.atom_font_family = 'Arial'
        self.atom_font_bold = False
        self.atom_font_size = 40
        self.atom_font_color = "black"  # color or "element"
        self.atom_color_scheme = {
            "C": "black",
            "O": "red",
            "N": "green",
            "S": "yellow"
        }
        self.atom_global_offset_x = 0
        self.atom_global_offset_y = -0.1
        self.atom_charge_offset = .2
        self.atom_H_offset_x = 0.3
        self.atom_H_offset_y = 0
        # self.margin = 0.1  # space around atom label (how much to shorten bond)

        ## atom, bond, and ring numbers
        self.bond_numbers_show = False
        self.bond_numbers_offset = 0.2
        self.bond_alignment = "best"  # ["best", "left", "right", "top", "bottom"]
        self.bond_numbers_font_family = 'Arial'
        self.bond_numbers_font_bold = False
        self.bond_numbers_font_size = 0.5
        self.bond_numbers_font_color = "gray"
        self.bond_numbers_box_type = "bottom_center"  # "bottom_center" or None
        self.bond_numbers_box_x = 0.3
        self.bond_numbers_box_y = 0.3

        self.atom_numbers_show = False
        self.atom_numbers_offset = 0.3
        self.atom_alignment = "best"  # ["best", "left", "right", "top", "bottom"]
        self.atom_numbers_font_family = 'Arial'
        self.atom_numbers_font_bold = False
        self.atom_numbers_font_size = 0.5
        self.atom_numbers_font_color = "tan"
        self.atom_numbers_box_type = "bottom_center"  # "bottom_center" or None
        self.atom_numbers_box_x = 0.4
        self.atom_numbers_box_y = 0.4

        self.ring_numbers_show = False
        self.ring_numbers_offset_x = 0
        self.ring_numbers_offset_y = 0
        self.ring_numbers_font_family = 'Arial'
        self.ring_numbers_font_bold = False
        self.ring_numbers_font_size = 0.5
        self.ring_numbers_font_color = "darkgreen"

        ## label
        self.label_show = True
        self.label_location = "bottom"  # options = ["top", "bottom"]
        self.label_font_family = 'Arial'
        self.label_font_bold = False
        self.label_font_size = 20
        self.label_font_color = "black"
        self.label_auto_wrap = True
        self.label_auto_wrap_length = 20
        self.label_pad = 0.75  # distance between molecule and text


        ##
        self.highlight_atom_color = (1,0,0,0.25) # RGBA
        self.highlight_atom_size = 60
        self.highlight_bond_color = "rgba(0,1,0,0.25)"
        self.highlight_bond_size = 30
        # self.highlight_bonds_between_atoms = False
        # self.highlight_atoms_on_bonds = False


        ## debug
        self.debug = False
        self.debug_molecule_show = True
        self.debug_molecule_color = 'gray'
        self.debug_molecule_size = 15
        self.debug_molecule_line_width = 3
        self.debug_molecule_dash = "dash"  # None or "dash"

        self.debug_bond_vector_show = True
        self.debug_bond_perpendicular_show = True
        self.debug_bond_vector_length = 0.3
        self.debug_bond_vector_color = "green"
        self.debug_bond_vector_perp_color = "blue"
        self.debug_bond_vector_line_width = 2
        self.debug_bond_vector_head_width = 0.1
        self.debug_bond_vector_head_height = 0.1
        self.debug_bond_vector_dash = None
        self.debug_bond_vector_style = 0

        self.debug_atom_vector_show = True
        self.debug_atom_vector_length = 0.3
        self.debug_atom_vector_color = "red"
        self.debug_atom_vector_line_width = 2
        self.debug_atom_vector_head_width = 0.1
        self.debug_atom_vector_head_height = 0.1
        self.debug_atom_vector_dash = None
        self.debug_atom_vector_style = 0

        self.debug_ring_center_show = True
        self.debug_ring_center_size = 10
        self.debug_ring_center_color = "black"

        # self.debug_show_parenthesis = False

        # these are to estimate size of these things for clearance
        self.text_calculator = "manual"  # "auto" or "manual"  manual can be way faster but less robust
        self.text_width = 6.8  # at 10 pt font
        self.text_height = 7.84 # at 10 pt font
        self.dot_scaler = 0.1

        ## matplotlib
        self.matplotlib_dpi = 100

    def set_style(self, filename: str | pathlib.Path):
        with open(filename, 'r') as f:
            text = f.read()

        data = yaml.safe_load(text)

        if data is None:  # no data found
            warnings.warn(f"No style properties found from {filename}. Skipping.")
            return

        for k, v in data.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                warnings.warn(f"{k} is not a valid style label. Skipping.")

    def save_style(self, filename: str | pathlib.Path):
        with open(filename, 'w') as f:
            yaml.dump(self.__dict__, f)

    def make_subscript(self, text: str) -> str:
        if self.plotter == "plotly":
            return f"<sub>{text}</sub>"
        if self.plotter == "matplotlib":
            return "$_{" + f"{text}" + "}$"

        return text

    def make_superscript(self, text: str) -> str:
        if self.plotter == "plotly":
            return f"<sup>{text}</sup>"
        if self.plotter == "matplotlib":
            return "$^{" + f"{text}" + "}$"

        return text

    def get_text_break(self) -> str:
        if self.plotter == "plotly":
            return f"<br>"

        return "\n"

    def get_atom_color(self, atom_symbol: str) -> str:
        if self.atom_font_color == "element":
            return self.atom_color_scheme.get(atom_symbol, "black")
        return self.atom_font_color

    def get_plotter(self):
        if self.plotter == "plotly":
            from chemdraw.drawers.plotters.plotly_2d import draw_single_2d
            return draw_single_2d
        elif self.plotter == "matplotlib":
            from chemdraw.drawers.plotters.matplotlib_2d import draw_single_2d
            return draw_single_2d

        raise ValueError("Invalid plotter")

    @classmethod
    def from_file(cls, filename: str | pathlib.Path):
        style = cls()
        style.set_style(filename)
        return style

    # def get_text_size(self, text: str, font_family: str, size: int | float) -> float:
    #     if self.plotter != "matplotlib":
    #         raise ValueError("Only support matplotlib plotter.")
    #
    #     from matplotlib.text import TextPath
    #     from matplotlib.font_manager import FontProperties
    #
    #     fp = FontProperties(family=font_family)
    #     # Create the path (position doesn't matter for size)
    #     tp = TextPath((0, 0), text, size=size, prop=fp)
    #
    #     # Get the bounding box
    #     bbox = tp.get_extents()
    #     return bbox.width, bbox.height


def determine_which_plotting_lib_installed() -> list[str]:
    libs = []
    try:
        libs.append("matplotlib")
    except ImportError:
        pass
    try:
        import plotly
        libs.append("plotly")
    except ImportError:
        pass

    if len(libs) == 0:
        raise ImportError(
            'Please install a plotting library: '
            '\n\t`pip install matplotlib`'
            '\n\t`pip install plotly`'
        )

    return libs

plotting_libs = determine_which_plotting_lib_installed()
current_folder = pathlib.Path(__file__).absolute().parent
STYLE_TEMPLATE = StyleTemplate.from_file(current_folder / "style_templates" / f"acs_1996_{plotting_libs[0]}.yaml")
