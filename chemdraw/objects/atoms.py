
import numpy as np

import chemdraw.utils.vector_math as vector_math
from chemdraw.drawers.general_classes import Font, Highlight

ATOM_VALENCY = {
    "H": 1,
    "B": 3,
    "C": 4,
    "N": 3,
    "O": 2,
    "F": 1,
    "Si": 4,
    "P": 3,
    "S": 2,
    "Cl": 1,
    "Br": 1,
    "I": 1,
}


class Atom:
    def __init__(self, symbol: str, id_: int, parent):
        self.symbol = symbol
        self.id_ = id_
        self.parent = parent

        self.number_hydrogens = ATOM_VALENCY[self.symbol]
        self.bonds = []
        self.rings = []

        self._vector = None
        self._number_of_bonds = None

        # drawing stuff
        self._show = None
        self.font = Font()
        self.highlight = Highlight()
        self.number = self.id_

    def __repr__(self) -> str:
        return f"{self.symbol} (id: {self.id_}): [{self.coordinates[0]}, {self.coordinates[1]}] with {len(self.bonds)} bonds"

    @property
    def show(self):
        return self._show

    @show.setter
    def show(self, show: bool):
        self._show = show
        self.font.show = show

    @property
    def coordinates(self) -> np.ndarray:
        return self.parent.atom_coordinates[self.id_, :]

    @coordinates.setter
    def coordinates(self, coordinates: np.ndarray):
        self.parent.atom_coordinates[self.id_, :] = coordinates

    @property
    def vector(self) -> np.ndarray:
        if self._vector is None:
            vector = np.zeros(2, dtype="float64")
            if len(self.bonds) == 1:
                self._vector = -1 * vector_math.normalize(self.bonds[0].center - self.coordinates)
                # TODO: fix and atom 'H'

            elif len(self.bonds) == 2:
                for bond in self.bonds:
                    vector += vector_math.normalize(bond.center - self.coordinates)
                self._vector = -1 * vector
            elif len(self.bonds) == 3:
                for bond in self.bonds:
                    from chemdraw.objects.bonds import BondType
                    if bond.type_ == BondType.double:
                        self._vector = -1 * (bond.center - self.coordinates)
                        break
                else:
                    for bond in self.bonds:
                        vector += vector_math.normalize(bond.center - self.parent.coordinates)
                        self._vector = vector_math.normalize(vector)

            else:
                # dots = {}
                # for bond in self.bonds:
                #     for bond_ in self.bonds:
                #         dots[f"{np.max([bond.id_, bond_.id_])}_{np.min([bond.id_, bond_.id_])}"] = \
                #         np.dot(bond.center-self.position, bond_.center-self.position)
                #
                # keys = []
                # values = []
                # for k, v in dots.items():
                #     keys.append(k)
                #     values.append(v)
                self._vector = (0, 0)

        return self._vector

    @property
    def number_of_bonds(self) -> int:
        if self._number_of_bonds is None:
            self._number_of_bonds = np.sum([bond.type_.value for bond in self.bonds])

        return self._number_of_bonds

    @property
    def in_ring(self) -> bool:
        return bool(self.rings)

    def add_bond(self, bond):
        self.bonds.append(bond)
        self.number_hydrogens -= bond.type_.value

    def get_atom_number_position(self, alignment: str, offset: float) -> tuple[float, float]:
        if alignment == "left":
            return self.coordinates[0] + offset, self.coordinates[1]
        elif alignment == "right":
            return self.coordinates[0] - offset, self.coordinates[1]
        elif alignment == "top":
            return self.coordinates[0], self.coordinates[1] + offset
        elif alignment == "bottom":
            return self.coordinates[0], self.coordinates[1] - offset

        # best
        return self.coordinates[0] + self.vector[0] * offset, self.coordinates[1] + self.vector[1] * offset
