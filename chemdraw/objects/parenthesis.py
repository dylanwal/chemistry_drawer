
import numpy as np

from chemdraw.data_types import PointType
from chemdraw.drawers.general_classes import Font, Line
from chemdraw.objects.atoms import Atom
from chemdraw.objects.bonds import Bond
import chemdraw.utils.vector_math as vector_math

def _add_parenthesis(self, s_block: dict) -> list[Parenthesis]:
    counter = 0
    parenthesis_list = []
    for k, v in s_block.items():
        if v["type_"] == Sgroup.SRU or v["type_"] == Sgroup.GEN:
            kwargs = dict(
                atoms=[self.atoms[i] for i in v['atoms']] if 'atoms' in v else None,
                contained_bonds=[self.atoms[i] for i in v['bonds']] if 'bonds' in v else None,
                parent=self
            )
            pos = np.array(v["position"])
            coordinate1 = np.array([np.mean([pos[0], pos[2]]), np.mean([pos[1], pos[3]])])
            coordinate2 = np.array([np.mean([pos[4], pos[6]]), np.mean([pos[5], pos[7]])])
            self._add_parenthesis_coordinates([coordinate1, coordinate2])
            vector = vector_math.normalize(np.array(coordinate1-coordinate2))

            par1 = Parenthesis(**kwargs,
                               id_=counter,
                               vector=-vector,
                               size=vector_math.pythagoras_theorem(pos[:2], pos[2:4])/2
                               )
            counter += 1
            par2 = Parenthesis(**kwargs,
                               id_=counter,
                               vector=vector,
                               sub_script=v["label"] if 'label' in v else None,
                               super_script=v["connectivity"].label if 'connectivity' in v else None,
                               size=vector_math.pythagoras_theorem(pos[4:6], pos[6:])/2
                               )
            counter += 1
            par1.partner = par2
            par2.partner = par1
            parenthesis_list += [par1, par2]

    return parenthesis_list

def add_parenthesis(self, bond_ids: list[int], sub_script: str = None, super_script: str = None):
    bonds = [self.bonds[id_] for id_ in bond_ids]
    if self.parenthesis_coordinates is None:
        self.parenthesis_coordinates = bonds[0].center.reshape((1, 2))
    else:
        self.parenthesis_coordinates = np.vstack((self.parenthesis_coordinates, bonds[0].center))
    self.parenthesis_coordinates = np.vstack((self.parenthesis_coordinates, bonds[1].center))

    vector = self.parenthesis_coordinates[-1] - self.parenthesis_coordinates[-2]

    self.parenthesis.append(
        Parenthesis(self,
                    id_=len(self.parenthesis_coordinates)-2,
                    vector=vector
                    )
    )
    self.parenthesis.append(
        Parenthesis(self,
                    id_=len(self.parenthesis_coordinates)-1,
                    vector=-vector,
                    sub_script=sub_script,
                    super_script=super_script
                    )
    )



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
        self.vector = vector_math.normalize(vector)
        self.size = size

        self.partner = None
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
        if self.partner is not None:
            text += f", partner: {self.partner.id_}"
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
