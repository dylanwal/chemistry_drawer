    @property
    def vector(self) -> np.ndarray:
        if self._vector is None:
            vector = np.zeros(2, dtype="float64")
            if len(self.bonds) == 1:
                self._vector = -1 * vector_math.normalize(self.bonds[0].center - self.coordinates)

            elif len(self.bonds) == 2:
                for bond in self.bonds:
                    vector += vector_math.normalize(bond.center - self.coordinates)
                self._vector = -1 * vector

            elif len(self.bonds) == 3:
                for bond in self.bonds:
                    from chemdraw.objects.bonds import BondType
                    if bond.type_ == BondType.double:
                        self._vector = -1 * (bond.center - self.coordinates)
                        break
                else:
                    for bond in self.bonds:
                        vector += vector_math.normalize(bond.center - self.parent.coordinates)
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
                self._vector = (1, 0)

        return self._vector


        def get_atom_number_position(self, alignment: str, offset: float) -> tuple[float, float]:
        if alignment == "left":
            return self.coordinates[0] + offset, self.coordinates[1]
        elif alignment == "right":
            return self.coordinates[0] - offset, self.coordinates[1]
        elif alignment == "top":
            return self.coordinates[0], self.coordinates[1] + offset
        elif alignment == "bottom":
            return self.coordinates[0], self.coordinates[1] - offset

        # best
        return self.coordinates[0] + self.vector[0] * offset, self.coordinates[1] + self.vector[1] * offset