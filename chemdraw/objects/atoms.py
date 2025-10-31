import numpy as np

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
    "*": 0
}


class Atom:
    # __slots__ = ("symbol", "_id", "parent", "_show", "font", "highlight", "number", "_atom_number_position")
    def __init__(self, symbol: str, _id: int, parent):
        self.symbol = symbol
        self._id = _id
        self.parent = parent

        # drawing stuff
        self._show = None
        self.font = Font()
        self.highlight = Highlight()
        self.number = self._id
        self._atom_number_position = None

    def __repr__(self) -> str:
        return f"{self.symbol} (id: {self._id}): [{','.join(self.coordinates)}]"

    @property
    def show(self):
        return self._show

    @show.setter
    def show(self, show: bool):
        self._show = show
        self.font.show = show

    @property
    def coordinates(self) -> np.ndarray:
        return self.parent.coordinates[:, self._id]

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

        self.parent.coordinates[self._id, :] = coordinates
