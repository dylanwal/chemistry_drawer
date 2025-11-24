import pathlib
import warnings

import yaml


class StyleTemplate:
    """ For styling the molecule's look (no parameters that are plotting package dependent). """
    def __init__(self):
        self.plotter = "matplotlib" # "plotly"
        self.auto_rotate = False # rotates molecule longest axis to [1,0]  or [1,0,0]
        self.auto_center = True # move bound box center to [0, 0]

        # self.show_hydrogens = False
        # self.methyl = None # or "Me"


        ### drawing (first in list is drawn at the bottom)
        # 'label' should be last as it needs the molecule built to know where it should be.
        # self.draw_order = ["ring_highlights", "highlights", "parenthesis", "ring_numbers"]
        self.draw_order = ["bonds", "atoms", "debug", "bond_numbers", "atom_numbers", "label"]

        ## plotting
        self.plot_width = 700
        self.plot_height = 560
        self.plot_background_color = "white" #"rgba(0,0,0,0)"
        self.plot_buffer = 0.1  # in percent


        ## bond
        self.bond_length = 1 # global scaling
        self.bond_color = "black"
        self.bond_width = 2
        self.bond_offset = 0.67
        self.bond_double_offset = 0.25  # of double bond perpendicular
        self.bond_double_center_length = 0.65  # [1 - 1.5] 1 = full length; >1 = longer
        self.bond_double_center_length_double = 0.4
        self.bond_double_offset_length = 0.75  # [0 - 1] 1 = full length; <1 = shorter
        self.bond_triple_offset = 0.23   # of triple bond perpendicular
        self.bond_triple_length = 1
        self.bond_stereo_offset = 0.23  # how wide is the triangle
        self.bond_stereo_wedge_number_lines = 6
        # self.bond_stereo_wedge_line_width = 6

        ## atom
        self.atom_show_carbons = False  # show carbon atoms
        # self.atom_prefix = ""  # useful for invisible text modifiers
        # self.atom_suffix = "" # useful for invisible text modifiers
        self.atom_text_x_offset = 0.1  # TODO make font size dependent
        self.atom_text_y_offset = 0.07  # TODO make font size dependent
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


        ## atom and bond numbers
        self.bond_numbers_show = False
        self.bond_numbers_offset = 0.3
        self.bond_alignment = "best" # ["best", "left", "right", "top", "bottom"]
        self.bond_numbers_font_family = 'Arial'
        self.bond_numbers_font_bold = False
        self.bond_numbers_font_size = 20
        self.bond_numbers_font_color = "gray"

        self.atom_numbers_show = False
        self.atom_numbers_offset = 0.3
        self.atom_alignment = "best" # ["best", "left", "right", "top", "bottom"]
        self.atom_numbers_font_family = 'Arial'
        self.atom_numbers_font_bold = False
        self.atom_numbers_font_size = 20
        self.atom_numbers_font_color = "tan"


        ## label
        self.label_show = True
        self.label_location = "bottom"  # options = ["top", "bottom"]
        self.label_font_family = 'Arial'
        self.label_font_bold = False
        self.label_font_size = 20
        self.label_font_color = "black"
        self.label_auto_wrap = True
        self.label_auto_wrap_length = 20
        self.label_pad = 0.75 # distance between molecule and text


        ## debug
        self.debug = False
        self.debug_show_molecule = True
        self.debug_molecule_color = 'gray'
        self.debug_molecule_size = 15
        self.debug_molecule_line_width = 3
        self.debug_molecule_dash = "dash" # None or "dash"

        self.debug_show_bond_vector = True
        self.debug_show_bond_perpendicular = True
        self.debug_bond_vector_length = 0.3
        self.debug_bond_vector_color = "green"
        self.debug_bond_vector_perp_color = "blue"
        self.debug_bond_vector_line_width = 2
        self.debug_bond_vector_head_width = 0.1
        self.debug_bond_vector_head_height = 0.1
        self.debug_bond_vector_dash = None
        self.debug_bond_vector_style = 0

        self.debug_show_atom_vector = True
        self.debug_atom_vector_length = 0.3
        self.debug_atom_vector_color = "red"
        self.debug_atom_vector_line_width = 2
        self.debug_atom_vector_head_width = 0.1
        self.debug_atom_vector_head_height = 0.1
        self.debug_atom_vector_dash = None
        self.debug_atom_vector_style = 0

        # self.debug_show_parenthesis = False

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
            from chemdraw.drawers.plotters.plotly_drawing import draw_single_2d
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


current_folder = pathlib.Path(__file__).absolute().parent
STYLE_TEMPLATE = StyleTemplate.from_file(current_folder / "style_templates" / "acs_1996.yaml")
