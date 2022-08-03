
import numpy as np

from chemdraw.data_types import PointType
from chemdraw.drawers.general_classes import Font, Line
from chemdraw.objects.atoms import Atom
from chemdraw.objects.bonds import Bond
import chemdraw.utils.vector_math as vector_math


class Parenthesis:

    def __init__(self,
                 parent,
                 id_: int,
                 vector: PointType,
                 atoms: list[Atom] = None,
                 contained_bonds: list[Bond] = None,
                 sub_script: str = None,
                 super_script: str = None,
                 size: float = None
                 ):
        self.id_ = id_
        self.parent = parent
        self.sub_script = sub_script
        self.super_script = super_script
        self.vector = vector
        self.size = size

        self.parenthesis_partner = None
        self.atoms = atoms if atoms is not None else []
        self.contained_bonds = contained_bonds if contained_bonds is not None else []
        self.cross_bond = self._get_cross_bond() if self.contained_bonds is not [] else []

        # drawing stuff
        self._show = None
        self.sub_script_font = Font()
        self.super_script_font = Font()
        self.line_format = Line()
        self.bond_position = False
        self.number = id_

        self.__post_init__()

    def __repr__(self) -> str:
        text = f"id: {self.id_}"
        if self.parenthesis_partner is not None:
            text += f", partner: {self.parenthesis_partner.id_}"
        text += ", atoms: ["
        for atom in self.atoms:
            text += f"{atom.symbol}({atom.id_}), "
        else:
            text = text[:-2]
            text += "]"
        return text

    def __post_init__(self):
        if self.contained_bonds == [] and self.atoms:
            # find bonds if none provided but atoms were
            bonds = []
            for atom in self.atoms:
                for bond in atom.bonds:
                    if bond not in bonds:
                        bonds.append(bond)
                    else:
                        self.contained_bonds.append(bond)
                        bonds.remove(bond)
            self.cross_bond = self._find_cross_bond(bonds)

    @property
    def show(self):
        return self._show

    @show.setter
    def show(self, show: bool):
        self._show = show
        self.sub_script_font.show = show
        self.super_script_font.show = show
        self.line_format.show = show

    @property
    def coordinates(self) -> np.ndarray:
        if self.bond_position:
            return self.cross_bond.center

        return self.parent.parenthesis_coordinates[self.id_]

    def _get_cross_bond(self) -> Bond:
        # get all bonds in and exiting parenthesis
        bonds = []
        for atom in self.atoms:
            bonds += atom.bonds

        # remove non-edge bonds and duplicates
        edge_bonds = []
        for bond in bonds:
            if bond not in self.contained_bonds:
                if bond not in edge_bonds:
                    edge_bonds.append(bond)

        return self._find_cross_bond(edge_bonds)

    def _find_cross_bond(self, edge_bonds: list[Bond]) -> Bond:
        # select bond with closes coordinates
        closest_bond = None
        smallest_distance = 10000000
        for bond in edge_bonds:
            distance = vector_math.pythagoras_theorem(bond.center, self.parent.parenthesis_coordinates[self.id_])
            if distance < smallest_distance:
                closest_bond = bond
                smallest_distance = distance

        return closest_bond
