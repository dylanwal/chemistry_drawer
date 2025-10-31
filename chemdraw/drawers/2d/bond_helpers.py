    @property
    def alignment(self) -> BondAlignment:
        """ 0: center, 1: with perpendicular, 2: opposite of perpendicular"""
        if self._alignment is None:
            self._alignment = self._get_alignment()

        return self._alignment

    @alignment.setter
    def alignment(self, value: int | str):
        if isinstance(value, int):
            self._alignment = BondAlignment(value)
            return
        else:
            values = set(item.label for item in BondAlignment)
            if value in values:
                self._alignment = BondAlignment[value]
                return

        raise ValueError("Invalid BondAlignment")


    def get_coordinates(self, show_carbons: bool, offset: float) -> tuple[np.ndarray, np.ndarray]:
        x = np.empty(2, dtype="float64")
        y = np.empty(2, dtype="float64")
        # point 1
        if self.atoms[0].symbol == "C" and not show_carbons:
            x[0] = self.x[0]
            y[0] = self.y[0]
        else:
            if len(self.atoms[0].symbol) > 1:
                offset_ = offset + (len(self.atoms[0].symbol)-1) * 0.5 * offset
            else:
                offset_ = offset
            x[0] = self.x[0] + self.vector[0] * offset_
            y[0] = self.y[0] + self.vector[1] * offset_
        # point 2
        if self.atoms[1].symbol == "C" and not show_carbons:
            x[1] = self.x[1]
            y[1] = self.y[1]
        else:
            if len(self.atoms[1].symbol) > 1:
                offset = offset + (len(self.atoms[1].symbol)-1) * 0.5 * offset
            x[1] = self.x[1] - self.vector[0] * offset
            y[1] = self.y[1] - self.vector[1] * offset

        return x, y

    def _get_alignment(self) -> BondAlignment:
        # only look at double bonds
        if self.type_ != BondType.double:
            return BondAlignment.center

        if self.in_ring:
            ring_ = self.rings[0]
            for ring in self.rings:
                if ring.aromatic:
                    ring_ = ring
                    break

            bond_ring_vector = ring_.center - self.center
            return alignment_decision(self.perpendicular, bond_ring_vector)

        # general
        if self.atoms[0].number_of_bonds == 2 and self.atoms[1].number_of_bonds == 2:
            return BondAlignment.center
        elif self.atoms[0].number_of_bonds == 3 and self.atoms[1].number_of_bonds == 2:
            return alignment_decision(self.perpendicular, self.atoms[0].vector)
        elif self.atoms[0].number_of_bonds == 2 and self.atoms[1].number_of_bonds == 3:
            return alignment_decision(self.perpendicular, self.atoms[1].vector)
        elif self.atoms[0].number_of_bonds == 3 and self.atoms[1].number_of_bonds == 3:
            return alignment_decision(self.perpendicular, self.atoms[1].vector)
            # non-ring
            # ring
        elif self.atoms[0].number_of_bonds == 4 and self.atoms[1].number_of_bonds == 2:
            return BondAlignment.center
        elif self.atoms[0].number_of_bonds == 2 and self.atoms[1].number_of_bonds == 4:
            return BondAlignment.center
        elif self.atoms[0].number_of_bonds == 4 and self.atoms[1].number_of_bonds == 4:
            return BondAlignment.center
            # non-ring
            # ring
        elif self.atoms[0].number_of_bonds == 4 and self.atoms[1].number_of_bonds == 3:
            return alignment_decision(self.perpendicular, self.atoms[1].vector)
        elif self.atoms[0].number_of_bonds == 3 and self.atoms[1].number_of_bonds == 4:
            return alignment_decision(self.perpendicular, self.atoms[0].vector)

    def get_bond_number_position(self, alignment: str, offset: float) -> tuple[float, float]:
        if alignment == "left":
            return self.center[0] + offset, self.center[1]
        elif alignment == "right":
            return self.center[0] - offset, self.center[1]
        elif alignment == "top":
            return self.center[0], self.center[1] + offset
        elif alignment == "bottom":
            return self.center[0], self.center[1] - offset

        # best
        if self.alignment == BondAlignment.center or self.alignment == BondAlignment.opposite:
            return self.center[0] + self.perpendicular[0] * offset, self.center[1] + self.perpendicular[1] * offset
        else:
            return self.center[0] - self.perpendicular[0] * offset, self.center[1] - self.perpendicular[1] * offset


def alignment_decision(vector: np.ndarray, bond_perpendicular: np.ndarray) -> BondAlignment:
    """ True: same side as perpendicular, False: opposite side of perpendicular """
    dot = np.dot(vector, bond_perpendicular)
    if dot >= 0:
        return BondAlignment.perpendicular
    return BondAlignment.opposite