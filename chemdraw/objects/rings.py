import numpy as np

from chemdraw.objects.atoms import Atom
from chemdraw.objects.bonds import Bond


class Ring:
    def __init__(self, atom_ids: list[int], id_: int, aromatic: bool = None):
        self.id_ = id_
        self.atom_ids = atom_ids
        self.aromatic = aromatic
        self.atoms: list[Atom] = []
        self.bonds: list[Bond] = []
        self.parent = None

        self._center = None

        # for drawing
        self.color = None
        self.highlight = False

    def __repr__(self) -> str:
        return f"Atoms: {self.atom_ids}"

    @property
    def ring_size(self) -> int:
        return len(self.atom_ids)

    @property
    def center(self) -> np.ndarray:
        if self.parent is not None:
            return self._center + self.parent.offset

        return self._center

    @property
    def coordinates(self) -> np.ndarray:
        coordinates = np.empty((self.ring_size, 2))
        for i, atom in enumerate(self.atoms):
            coordinates[i] = atom.position

        return coordinates

    def add_atoms(self, atoms: list[Atom]):
        for atom in atoms:
            if atom not in self.atoms:
                self.atoms.append(atom)
