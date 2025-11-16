import pathlib
import warnings

import yaml


class StyleTemplate:
    """ For styling the molecule's look (no parameters that are plotting package dependent). """
    def __init__(self):
        self.auto_rotate = True
        # rotates molecule longest axis to [1,0]  or [1,0,0]
        # self.show_hydrogens = False
        #

        ### drawing
        # self.draw_order = ["ring_highlights", "highlights", "bonds", "atoms", "parenthesis",
        #                    "atom_numbers", "bond_numbers", "ring_numbers",
        #                    "debug", "label"]
        self.draw_order = ["bonds"]
        # first in list is drawn at the bottom

        background_color = "rgba(0,0,0,0)"

        # # font
        # self.font = 'Arial'
        # self.font_size = 1
        # self.atom_color = "black"  # or "element"
        # self.bold = False
        #
        # self.bond_length = 1
        # self.spacing = 0.18 # of double bond perpendicular
        # self.bond_color = 'black'
        # self.bond_width = 1
        # self.margin = 0.1  # space around atom label (how much to shorten bond)
        #
        # self.methyl = None # or "Me"
        #
        # # bond
        self.bond_length = 1 # global scaling
        self.bond_color = "black"
        self.bond_width = 1
        self.bond_offset = 0.37
        self.bond_double_offset = 0.35  # width
        self.bond_double_center_length = 1.1  # [1 - 1.5] 1 = full length; >1 = longer
        self.bond_double_offset_length = 0.7  # [0 - 1] 1 = full length; <1 = shorter
        self.bond_triple_offset = 0.23   # width
        self.bond_triple_length = 0.5
        self.bond_stereo_offset = 0.23  # how wide is the triangle
        self.bond_stereo_wedge_number_lines = 6
        # self.bond_stereo_wedge_line_width = 6

    def set_style(self, filename: str | pathlib.Path):
        with open(filename, 'r') as f:
            text = f.read()

        data = yaml.safe_load(text)

        for k, v in data.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                warnings.warn(f"{k} is not a valid style label. Skipping.")

    @classmethod
    def from_file(cls, filename: str | pathlib.Path):
        style = cls()
        style.set_style(filename)
        return style


current_folder = pathlib.Path(__file__).absolute().parent
STYLE_TEMPLATE = StyleTemplate.from_file(current_folder / "style_templates" / "acs_1996.yaml")
