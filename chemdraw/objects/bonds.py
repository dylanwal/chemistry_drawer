import enum

import numpy as np

from chemdraw.objects.style_objects import StyleLine, StyleHighlight
import chemdraw.utils.math_vectors as math_vectors


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

BOND_COUNT = {
    BondType.single: 1,
    BondType.double: 2,
    BondType.triple: 3,
    BondType.wave: 1,
    BondType.hash: 1
}


class BondAlignment(enum.Enum):
    center = 0
    perpendicular = 1
    opposite = 2


class BondStereoChem(enum.Enum):
    default = 0
    up = 1
    down = 6 # from rdkit

    @classmethod
    def _missing_(cls, value):
        return cls.default


class Bond:
    def __init__(self, atom1_id: int, atom2_id: int, bond_type: int, stereo_chem: int, id_: int | str, parent):
        self.atom1_id = atom1_id
        self.atom2_id = atom2_id
        self.type_ = BondType(bond_type)
        self.id_ = id_
        self.stereo_chem = BondStereoChem(stereo_chem)
        self.parent = parent

        # drawing stuff
        self._show = True
        self.alignment = None
        self.style = StyleLine()
        self.highlight = StyleHighlight()
        self.label = id_

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
        self.style.show = show

    @property
    def coordinates(self) -> np.ndarray:
        return np.array(
            [self.parent.coordinates[i, (self.atom1_id, self.atom2_id)] for i in range(self.parent.coordinates.shape[0])]
        )

    @property
    def vector(self) -> np.ndarray:
        x, y = self.coordinates
        return math_vectors.normalize(np.array([x[1]-x[0], y[1]-y[0]]))

    @property
    def perpendicular(self) -> np.ndarray:
        return np.array([-self.vector[1], self.vector[0]])

    @property
    def center(self) -> np.ndarray:
        return np.mean(self.coordinates, axis=1)

    def in_rings(self) -> list[int]:
        return self.parent.bond_in_ring(self)
