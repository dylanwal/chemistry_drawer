import pathlib
import warnings

import yaml


class StyleTemplate:
    """ For styling the molecule's look (no parameters that are plotting package dependent). """
    def __init__(self):
        self.auto_rotate = True # rotates molecule longest axis to [1,0]  or [1,0,0]
        self.auto_center = True # move bound box center to [0, 0]

        # self.show_hydrogens = False
        # self.methyl = None # or "Me"
        ### drawing
        # self.draw_order = ["ring_highlights", "highlights", "parenthesis",
        #                    "atom_numbers", "bond_numbers", "ring_numbers",
        #                    "label"]
        self.draw_order = ["bonds", "atoms", "debug"]
        # first in list is drawn at the bottom
        background_color = "rgba(0,0,0,0)"

        ## bond
        self.bond_length = 1 # global scaling
        self.bond_color = "black"
        self.bond_width = 1
        self.bond_offset = 0.37
        self.bond_double_offset = 0.35  # of double bond perpendicular
        self.bond_double_center_length = 1.1  # [1 - 1.5] 1 = full length; >1 = longer
        self.bond_double_offset_length = 0.7  # [0 - 1] 1 = full length; <1 = shorter
        self.bond_triple_offset = 0.23   # of triple bond perpendicular
        self.bond_triple_length = 0.5
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
        self.atom_font_size = 70
        self.atom_font_color = "black"  # color or "element"
        self.atom_color_scheme = {
            "C": "black",
            "O": "red",
            "N": "green",
            "S": "yellow"
        }
        # self.margin = 0.1  # space around atom label (how much to shorten bond)


        ## debug
        self.debug = True
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

        for k, v in data.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                warnings.warn(f"{k} is not a valid style label. Skipping.")

    def save_style(self, filename: str | pathlib.Path):
        with open(filename, 'w') as f:
            yaml.dump(self.__dict__, f)

    def make_subscript(self, text: str) -> str:
        return f"<sub>{text}</sub>"

    def make_superscript(self, text: str) -> str:
        return f"<sup>{text}</sup>"

    def get_atom_color(self, atom_symbol: str) -> str:
        if self.atom_font_color == "element":
            return self.atom_color_scheme.get(atom_symbol, "black")
        return self.atom_font_color

    @classmethod
    def from_file(cls, filename: str | pathlib.Path):
        style = cls()
        style.set_style(filename)
        return style


current_folder = pathlib.Path(__file__).absolute().parent
STYLE_TEMPLATE = StyleTemplate.from_file(current_folder / "style_templates" / "acs_1996.yaml")


