import numpy as np

from chemdraw.objects.style_objects import StyleHighlight


class Ring:
    def __init__(self, atom_ids: np.ndarray, id_: int, parent, aromatic: bool = None):
        self.id_ = id_
        self.atom_ids = atom_ids
        self.aromatic = aromatic
        self.parent = parent

        self._center = None

        # for drawing
        self.highlight = StyleHighlight()
        self.label = id_

    def __repr__(self) -> str:
        return f"Atoms: {self.atom_ids}"

    @property
    def ring_size(self) -> int:
        return len(self.atom_ids)

    @property
    def center(self) -> np.ndarray:
        return np.mean(self.parent.coordinates[:, self.atom_ids], axis=1)

    # @property
    # def coordinates(self) -> np.ndarray:
    #     coordinates = np.empty((self.ring_size, 2))
    #     for i, atom in enumerate(self.atoms):
    #         coordinates[i] = atom.coordinates
    #
    #     return coordinates
    #
    # def add_atoms(self, atoms: list[Atom]):
    #     for atom in atoms:
    #         if atom not in self.atoms:
    #             self.atoms.append(atom)
