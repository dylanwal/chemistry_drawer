import numpy as np

from chemdraw.objects.style_objects import StyleFont, StyleHighlight

from chemdraw.objects.bonds import BOND_COUNT
import chemdraw.utils.math_vectors as math_vectors


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
    "*": 0
}


class Atom:
    # __slots__ = ("symbol", "_id", "parent", "_show", "font", "highlight", "number",
    # "_atom_number_position", "radical", "charge")
    def __init__(self, symbol: str, id_: int, parent, charge: int = 0, radical: bool = False):
        self.symbol = symbol
        self.charge = charge
        self.radical = radical
        self.id_ = id_
        self.parent = parent

        # drawing stuff
        self._show = None
        self.style = StyleFont()
        self.highlight = StyleHighlight()
        self.number = self.id_
        self._atom_number_position = None

        # computed data
        self._bonds = []
        self._number_bonds = None
        self._vector = None

    def __repr__(self) -> str:
        return f"{self.symbol} (id: {self.id_}): [{','.join(self.coordinates)}]"

    @property
    def show(self):
        return self._show

    @show.setter
    def show(self, show: bool):
        self._show = show
        self.style.show = show

    @property
    def coordinates(self) -> np.ndarray:
        return self.parent.coordinates[:, self.id_]

    @coordinates.setter
    def coordinates(self, coordinates: np.ndarray):
        """set coordinates of atom"""
        if coordinates.ndim != 1:
            if len(coordinates) != self.parent.coordinates.shape[0]:
                raise ValueError(
                    f"Wrong dimension of coordinates. "
                    f"\n\tGiven: {len(coordinates)}"
                    f"\n\tExpected: {self.parent.coordinates.shape[0]}"
                )
            coordinates = coordinates.reshape((1, self.parent.coordinates.shape[0]))

        else:
            if coordinates.shape[0] != self.parent.coordinates.shape[0]:
                raise ValueError(
                    f"Wrong dimension of coordinates. "
                    f"\n\tGiven: {coordinates.shape[0]}"
                    f"\n\tExpected: {self.parent.coordinates.shape[0]}"
                )

        self.parent.coordinates[self.id_, :] = coordinates

    def _get_bonds(self):
        if self.parent.bonds is not None:
            for bond in self.parent.bonds:
                if self.id_ == bond.atom1_id or self.id_ == bond.atom2_id:
                    self._bonds.append(bond)

    def number_bonds(self) -> int:
        if self._number_bonds is None:
            self._get_bonds()
            self._number_bonds = sum(BOND_COUNT[bond.type_] for bond in self._bonds)

        return self._number_bonds

    def vector(self) -> np.ndarray:
        if self._vector is None:
            self._get_bonds()

            vector = np.zeros(2, dtype="float64")
            if len(self._bonds) == 1:
                self._vector = -1 * math_vectors.normalize(self._bonds[0].center - self.coordinates)

            elif len(self._bonds) == 2:
                for bond in self._bonds:
                    vector += math_vectors.normalize(bond.center - self.coordinates)
                self._vector = -1 * vector

            elif len(self._bonds) == 3:
                for bond in self._bonds:
                    from chemdraw.objects.bonds import BondType
                    if bond.type_ == BondType.double:
                        self._vector = -1 * (bond.center - self.coordinates)
                        break
                else:
                    for bond in self._bonds:
                        vector += math_vectors.normalize(bond.center - self.parent.coordinates)
                        self._vector = math_vectors.normalize(vector)

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
                self._vector = (1, 0)

        return self._vector
