import numpy as np

from chemdraw.config.style_template import STYLE_TEMPLATE
from chemdraw.objects.molecule import Molecule
from chemdraw.objects.atoms import Atom
from chemdraw.objects.bonds import Bond, BondType, BondAlignment, BondStereoChem
from chemdraw.drawers.two_d.draw_atoms import between_two_double_bonds
import chemdraw.utils.math_vectors as math_vectors
import chemdraw.utils.general_math as general_math

from chemdraw.drawers.two_d.primitives_for_drawing import DrawingContainer, Line, Fill


def draw_bonds(container: DrawingContainer, mol: Molecule) -> DrawingContainer:
    for bond in mol.bonds:
        if not bond._show:
            continue

        if bond.type_ == BondType.single:
            objs = draw_single_bond(bond)
        elif bond.type_ == BondType.double:
            objs = draw_double_bond(bond)
        # elif bond.type_ == BondType.wave:
        #     objs = draw_wave_bond(bond)
        # elif bond.type_ == BondType.hash:
        #     objs = draw_hash_bond(bond)
        elif bond.type_ == BondType.triple:
            objs = draw_triple_bond(bond)
        else:
            raise RuntimeError(f"Unknown bond type: {bond.type_}")

        # set style sheet values if not set locally.
        if not isinstance(objs, list):
            objs = [objs]
        for obj in objs:
            if isinstance(obj, Line):
                if obj.color is None:
                    obj.color = STYLE_TEMPLATE.bond_color
                if obj.width is None:
                    obj.width = STYLE_TEMPLATE.bond_width
            if isinstance(obj, Fill):
                if obj.color is None:
                    obj.color = STYLE_TEMPLATE.bond_color

        container.add_objects(objs)

    return container




def draw_single_bond(bond: Bond) -> Line | Fill | list[Line]:
    if bond.stereo_chem != BondStereoChem.default:
        return draw_stereo_bond(bond)

    x, y = shorten_bond_for_atom_label(bond)
    return Line(x, y, bond.style.color, bond.style.width)


def draw_stereo_bond(bond: Bond) -> Line | Fill | list[Line]:
    x, y = shorten_bond_for_atom_label(bond)
    # bond_vector = bond.vector
    # bond_center = bond.center
    perpendicular = bond.perpendicular

    stereo_offset = STYLE_TEMPLATE.bond_stereo_offset

    if bond.stereo_chem is BondStereoChem.up:  # wedge
        x_left = x[1] + perpendicular[0] * stereo_offset
        x_right = x[1] - perpendicular[0] * stereo_offset
        y_left = y[1] + perpendicular[1] * stereo_offset
        y_right = y[1] - perpendicular[1] * stereo_offset
        x_plot = np.array([x[0], x_left, x_right, x[0]])
        y_plot = np.array([y[0], y_left, y_right, y[0]])

        return Fill(x_plot, y_plot, color=bond.style.color)

    # hash
    num_lines = STYLE_TEMPLATE.bond_stereo_wedge_number_lines
    xy = general_math.points_along_line((x[0], y[0]), (x[1], y[1]), num_lines + 2)  # the +2  is for the ends
    xy = xy[1:-1, :]  # remove the ends
    hash_lengths = np.linspace(1 / num_lines, 1, num_lines) * stereo_offset

    lines = []
    for i in range(num_lines):
        points = general_math.get_offset_points(xy[i, :], bond.perpendicular, hash_lengths[i])
        lines.append(Line(points[:, 0], points[:, 1], color=bond.style.color, width=bond.style.width))

    return lines


def draw_double_bond(bond: Bond):
    x, y = shorten_bond_for_atom_label(bond)
    # bond_vector = bond.vector
    # bond_center = bond.center
    perpendicular = bond.perpendicular
    double_bond_offset = STYLE_TEMPLATE.bond_double_offset

    alignment = bond.alignment
    if alignment is None:
        alignment = determine_double_bond_alignment(bond)

    if alignment == BondAlignment.center:
        x_left = x + perpendicular[0] * double_bond_offset / 2
        x_right = x - perpendicular[0] * double_bond_offset / 2
        y_left = y + perpendicular[1] * double_bond_offset / 2
        y_right = y - perpendicular[1] * double_bond_offset / 2
        return [
            Line(x_left, y_left, bond.style.color, bond.style.width),  # left
            Line(x_right, y_right, bond.style.color, bond.style.width),  # right
        ]

    # offset double bond
    if bond.alignment == BondAlignment.perpendicular:  # same side as perpendicular
        x_off = x + perpendicular[0] * double_bond_offset
        y_off = y + perpendicular[1] * double_bond_offset
    else:  # opposite side perpendicular
        x_off = x - perpendicular[0] * double_bond_offset
        y_off = y - perpendicular[1] * double_bond_offset

    if STYLE_TEMPLATE.bond_double_offset_length != 1:
        x_off, y_off = math_vectors.shorten_line(x_off, y_off, STYLE_TEMPLATE.bond_double_offset_length)

    return [
        Line(x, y, bond.style.color, bond.style.width),  # center
        Line(x_off, y_off, bond.style.color, bond.style.width),
    ]


def determine_double_bond_alignment(bond: Bond):
    assert bond.type_ == BondType.double

    mol = bond.parent
    atom1 = mol.atoms[bond.atom1_id]
    atom2 = mol.atoms[bond.atom2_id]
    bond_center = bond.center
    perpendicular = bond.perpendicular

    # rings
    # in_ring = None
    # for ring in mol.rings:
    #     if bond in ring:
    #         if in_ring is None:
    #             in_ring = ring
    #         elif ring.aromatic:
    #             in_ring = ring
    #             break
    # if in_ring is not None:
    #     bond_ring_vector = in_ring.center - bond_center
    #     return alignment_decision(perpendicular, bond_ring_vector)

    # general
    num_bonds_atom1 = atom1.number_bonds()
    num_bonds_atom2 = atom2.number_bonds()

    if between_two_double_bonds(atom1) or between_two_double_bonds(atom2):
        # two doubles in a row
        return BondAlignment.center

    if num_bonds_atom1 == 2 and num_bonds_atom2 == 2:
        return BondAlignment.center
    elif num_bonds_atom1 == 3 and num_bonds_atom2 == 2:
        return alignment_decision(perpendicular, atom1.vector())
    elif num_bonds_atom1 == 2 and num_bonds_atom2 == 3:
        return alignment_decision(perpendicular, atom2.vector())
    elif num_bonds_atom1 == 3 and num_bonds_atom2 == 3:
        return alignment_decision(perpendicular, atom2.vector())
        # non-ring
        # ring
    elif num_bonds_atom1 == 4 and num_bonds_atom2 == 2:
        return BondAlignment.center
    elif num_bonds_atom1 == 2 and num_bonds_atom2 == 4:
        return BondAlignment.center
    elif num_bonds_atom1 == 4 and num_bonds_atom2 == 4:
        return BondAlignment.center
        # non-ring
        # ring
    elif num_bonds_atom1 == 4 and num_bonds_atom2 == 3:
        return alignment_decision(perpendicular, atom2.vector())
    elif num_bonds_atom1 == 3 and num_bonds_atom2 == 4:
        return alignment_decision(perpendicular, atom1.vector())
    else:
        return BondAlignment.center


def alignment_decision(vector: np.ndarray, bond_perpendicular: np.ndarray) -> BondAlignment:
    """ True: same side as perpendicular, False: opposite side of perpendicular """
    dot = np.dot(vector, bond_perpendicular)
    if dot >= 0:
        return BondAlignment.perpendicular
    return BondAlignment.opposite


def draw_triple_bond(bond: Bond) -> list[Line]:
    x, y = shorten_bond_for_atom_label(bond)
    perpendicular = bond.perpendicular
    triple_bond_offset = STYLE_TEMPLATE.bond_triple_offset
    triple_bond_length = STYLE_TEMPLATE.bond_triple_length

    x_left = x + perpendicular[0] * triple_bond_offset
    x_right = x - perpendicular[0] * triple_bond_offset
    y_left = y + perpendicular[1] * triple_bond_offset
    y_right = y - perpendicular[1] * triple_bond_offset

    if triple_bond_length != 1:
        x_left, y_left = _shorten_bond_triple(x_left, y_left, triple_bond_length)
        x_right, y_right = _shorten_bond_triple(x_right, y_right, triple_bond_length)

    return [
        Line(x, y, bond.style.color, bond.style.width),
        Line(x_left, y_left, bond.style.color, bond.style.width),
        Line(x_right, y_right, bond.style.color, bond.style.width),
    ]


def _shorten_bond_triple(x: np.ndarray, y: np.ndarray, triple_bond_length) \
        -> tuple[np.ndarray, np.ndarray]:
    x_new, y_new = math_vectors.shorten_line(x, y, triple_bond_length)

    # only shorten the terminal end
    # if bond.vector[0] == 0:  # vertical
    #     if bond.vector[1] > 0:
    #         if y0 > y1:
    #             x = np.array([x0, x[1]])
    #             y = np.array([y0, y[1]])
    #         else:
    #             x = np.array([x[0], x1])
    #             y = np.array([y[0], y1])
    #
    # elif bond.vector[0] > 0:
    #     if x0 > x1:
    #         x = np.array([x0, x[1]])
    #         y = np.array([y0, y[1]])
    #     else:
    #         x = np.array([x[0], x1])
    #         y = np.array([y[0], y1])
    # else:
    if x_new[0] < x_new[1]:
        x = np.array([x_new[0], x[1]])
        y = np.array([y_new[0], y[1]])
    else:
        x = np.array([x[0], x_new[1]])
        y = np.array([y[0], y_new[1]])

    return x, y


def shorten_bond_for_atom_label(bond: Bond) -> tuple[np.ndarray, np.ndarray]:
    x, y = bond.coordinates
    # if STYLE_TEMPLATE.plotter == "matplotlib":
    #     return matplotlib_shorten_bond_for_atom_label(bond)

    atom1 = bond.parent.atoms[bond.atom1_id]
    atom2 = bond.parent.atoms[bond.atom2_id]
    if (atom1.charge != 0 or atom1.radical) and atom1.coordinates[1] < atom2.coordinates[1]:
        multiplier1 = 0.5
        multiplier2 = 1
    elif (atom2.charge != 0 or atom2.radical) and atom2.coordinates[1] < atom1.coordinates[1]:
        multiplier2 = 0.5
        multiplier1 = 1
    else:
        multiplier1 = 1
        multiplier2 = 1

    if determine_if_show_atom_label(atom1) and determine_if_show_atom_label(atom2):
        x, y = math_vectors.shorten_line(x, y, STYLE_TEMPLATE.bond_offset**2*multiplier1*multiplier2, None)
    elif determine_if_show_atom_label(atom1):
        x, y = math_vectors.shorten_line(x, y, STYLE_TEMPLATE.bond_offset*multiplier1, 0)
    elif determine_if_show_atom_label(atom2):
        x, y = math_vectors.shorten_line(x, y, STYLE_TEMPLATE.bond_offset*multiplier2, 1)

    return x, y

# def matplotlib_shorten_bond_for_atom_label(bond: Bond) -> tuple[np.ndarray, np.ndarray]:
#     x, y = bond.coordinates
#
#     atom1 = bond.parent.atoms[bond.atom1_id]
#     atom2 = bond.parent.atoms[bond.atom2_id]
#     if determine_if_show_atom_label(atom1):
#         text_obj = draw_atom(atom1)
#         if text_obj.font is None:
#             text_obj.font = STYLE_TEMPLATE.atom_font_family
#         if text_obj.bold is None:
#             text_obj.bold = STYLE_TEMPLATE.atom_font_bold
#         if text_obj.color is None:
#             text_obj.color = STYLE_TEMPLATE.get_atom_color(text_obj)
#         if text_obj.size is None:
#             text_obj.size = STYLE_TEMPLATE.atom_font_size
#
#         if isinstance(text_obj.symbol, str):
#             text = text_obj.symbol
#         else:
#             text = text_obj.symbol[0]
#         label_width, label_height = STYLE_TEMPLATE.get_text_size(text, text_obj.font, text_obj.size)
#         try:
#             x_new, y_new = general_math.find_rectangle_intersection(
#                 np.array(
#                     [
#                         [text_obj.x-label_width/2, text_obj.x+label_width/2],
#                         [text_obj.y, text_obj.y+label_height],
#                     ]
#                 ),
#                 np.vstack((x,y))
#             )
#         except Exception:
#             return x, y
#         x[0] = x_new
#         y[0] = y_new
#
#     if determine_if_show_atom_label(atom2):
#         text_obj = draw_atom(atom2)
#         if text_obj.font is None:
#             text_obj.font = STYLE_TEMPLATE.atom_font_family
#         if text_obj.bold is None:
#             text_obj.bold = STYLE_TEMPLATE.atom_font_bold
#         if text_obj.color is None:
#             text_obj.color = STYLE_TEMPLATE.get_atom_color(text_obj)
#         if text_obj.size is None:
#             text_obj.size = STYLE_TEMPLATE.atom_font_size
#
#         if isinstance(text_obj.symbol, str):
#             text = text_obj.symbol
#         else:
#             text = text_obj.symbol[0]
#         label_width, label_height = STYLE_TEMPLATE.get_text_size(text, text_obj.font, text_obj.size)
#         try:
#             x_new, y_new = general_math.find_rectangle_intersection(
#                 np.array(
#                     [
#                         [text_obj.x-label_width/2, text_obj.x+label_width/2],
#                         [text_obj.y, text_obj.y+label_height],
#                     ]
#                 ),
#                 np.vstack((x,y))
#             )
#         except Exception:
#             return x, y
#         x[1] = x_new
#         y[1] = y_new
#
#     return x, y



def determine_if_show_atom_label(atom: Atom) -> bool:
    if atom._show is False:
        return False
    if not STYLE_TEMPLATE.atom_show_carbons and atom.symbol == "C" and atom.charge == 0 and not atom.radical and not between_two_double_bonds(atom):
        return False

    return True