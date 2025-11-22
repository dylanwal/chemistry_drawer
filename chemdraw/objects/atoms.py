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
        self._vector = None

    def __repr__(self) -> str:
        return f"{self.symbol} (id: {self.id_}): [{','.join(str(i) for i in self.coordinates)}]"

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
        if len(self._bonds) == 0:
            for bond in self.parent.bonds:
                if self.id_ == bond.atom1_id or self.id_ == bond.atom2_id:
                    self._bonds.append(bond)

    def number_bonds(self) -> int:
        self._get_bonds()
        return sum(BOND_COUNT[bond.type_] for bond in self._bonds)

    def _number_connections(self) -> int:
        self._get_bonds()
        return len(self._bonds)

    def number_hydrogens(self) -> int:
        return ATOM_VALENCY.get(self.symbol, 0)

    def vector(self) -> np.ndarray:
        if self._vector is None:
            self._get_bonds()

            if self._number_connections() == 1:
                self._vector = -1 * math_vectors.normalize(self._bonds[0].center - self.coordinates)

            elif self._number_connections() == 2 or self._number_connections() == 3:
                bond_vectors = []
                for bond in self._bonds:
                    # flip vector direction depending on atom - bond center locations
                    b = np.array([bond.center[0]-self.coordinates[0], bond.center[1] - self.coordinates[1]])
                    bond_vectors.append(math_vectors.normalize(b))
                self._vector = math_vectors.get_furthest_direction(bond_vectors)

            else:
                self._vector = (1, 0)

        return self._vector
