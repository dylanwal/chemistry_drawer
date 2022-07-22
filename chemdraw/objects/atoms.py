
import numpy as np

import chemdraw.utils.vector_math as vector_math

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
    def __init__(self, symbol: str, position: np.ndarray, id_: int):
        self.symbol = symbol
        self._position = position
        self.id_ = id_

        self.number_hydrogens = ATOM_VALENCY[self.symbol]
        self.bonds = []
        self.rings = []

        self._vector = None
        self._number_of_bonds = None

        self.parent = None

        # drawing stuff
        self.font = None
        self.size = None
        self.highlight = None
        self.number = self.id_

    def __repr__(self) -> str:
        return f"{self.symbol} (id: {self.id_}): [{self.position[0]}, {self.position[1]}] with {len(self.bonds)} bonds"

    @property
    def position(self) -> np.ndarray:
        if self.parent is not None:
            return self._position + self.parent.offset

        return self._position

    @position.setter
    def position(self, position: np.ndarray):
        self._position = position - self.parent.offset
        for bond in self.bonds:
            bond.update_position()

    @property
    def vector(self) -> np.ndarray:
        if self._vector is None:
            vector = np.zeros(2, dtype="float64")
            if len(self.bonds) == 1:
                self._vector = -1 * vector_math.normalize(self.bonds[0].center - self.position)
                # TODO: fix and atom 'H'

            elif len(self.bonds) == 2:
                for bond in self.bonds:
                    vector += vector_math.normalize(bond.center - self.position)
                self._vector = -1 * vector
            elif len(self.bonds) == 3:
                for bond in self.bonds:
                    from chemdraw.objects.bonds import BondType
                    if bond.type_ == BondType.double:
                        self._vector = -1 * (bond.center - self.position)
                        break
                else:
                    for bond in self.bonds:
                        vector += vector_math.normalize(bond.center - self.parent.position)
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
            return self.position[0] + offset, self.position[1]
        elif alignment == "right":
            return self.position[0] - offset, self.position[1]
        elif alignment == "top":
            return self.position[0], self.position[1] + offset
        elif alignment == "bottom":
            return self.position[0], self.position[1] - offset

        # best
        return self.position[0] + self.vector[0] * offset, self.position[1] + self.vector[1] * offset
