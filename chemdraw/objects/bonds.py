import enum

import numpy as np

from chemdraw.drawers.general_classes import Line, Highlight


class BondType(enum.Enum):
    single = 1
    double = 2
    triple = 3
    wave = 4
    hash = 5


BOND_SYMBOLS = {
    BondType.single: "-",
    BondType.double: "=",
    BondType.triple: "𝄘",
    BondType.wave: "~",
    BondType.hash: "--"
}


class BondAlignment(enum.Enum):
    center = 0
    LT = 1
    RB = 2


class BondStereoChem(enum.Enum):
    default = 0
    up = 1
    down = 2

    @classmethod
    def _missing_(cls, value):
        return cls.default


class Bond:
    def __init__(self, atom1_id: int, atom2_id: int, bond_type: int, stereo_chem: int, _id: int, parent):
        self.atom1_id = atom1_id
        self.atom2_id = atom2_id
        self.type_ = BondType(bond_type)
        self._id = _id
        self.stereo_chem = BondStereoChem(stereo_chem)
        self.parent = parent

        # drawing stuff
        self._show = None
        self._alignment = None
        self.line_format = Line()
        self.highlight = Highlight()
        self.number = _id

    def __repr__(self) -> str:
        text = f"{self.parent.atoms[self.atom1_id].symbol} ({self.atom1_id})"
        text += f" {BOND_SYMBOLS[self.type_]} "
        if self.stereo_chem is not BondStereoChem.default:
            text += f" ({self.stereo_chem.name})"
        text += f"{self.parent.atoms[self.atom2_id].symbol} ({self.atom2_id})"

        return text

    @property
    def show(self):
        return self._show

    @show.setter
    def show(self, show: bool):
        self._show = show
        self.line_format.show = show

    @property
    def coordinates(self) -> np.ndarray:
        return np.array(
            [self.parent.coordinates[i, (self.atom1_id, self.atom2_id)] for i in range(self.parent.atom_coordiants.shape[0])]
        )

    # @coordinates.setter
    # def coordinates(self, coordinates: np.ndarray):
    #     """set coordinates of bond"""
    #     if coordinates.ndim != 1:
    #         if len(coordinates) != self.parent.atom_coordinates.shape[0]:
    #             raise ValueError(
    #                 f"Wrong dimension of coordinates. "
    #                 f"\n\tGiven: {len(coordinates)}"
    #                 f"\n\tExpected: {self.parent.atom_coordinates.shape[0]}"
    #             )
    #         coordinates = coordinates.reshape((1, self.parent.atom_coordinates.shape[0]))
    #
    #     else:
    #         if coordinates.shape[0] != self.parent.atom_coordinates.shape[0]:
    #             raise ValueError(
    #                 f"Wrong dimension of coordinates. "
    #                 f"\n\tGiven: {coordinates.shape[0]}"
    #                 f"\n\tExpected: {self.parent.atom_coordinates.shape[0]}"
    #             )
    #
    #     self.parent.atom_coordinates[:, self._id] = coordinates

    # @property
    # def vector(self) -> np.ndarray:
    #     return vector_math.normalize(np.array([self.x[1] - self.x[0], self.y[1] - self.y[0]]))
    #
    # @property
    # def perpendicular(self) -> np.ndarray:
    #     return np.array([-self.vector[1], self.vector[0]])
    #
    # @property
    # def center(self) -> np.ndarray:
    #     return np.array([np.mean(self.x), np.mean(self.y)])
