

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


