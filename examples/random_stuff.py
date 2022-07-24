import plotly.graph_objs as go
from rdkit import Chem
import numpy as np

import chemdraw


class Atom:
    def __init__(self, x):
        self.x =x

class Mol:
    def __init__(self, x):
        self.x = x
        self.atom = Atom(x[0, :])


    def modify(self):
        for x in self.x:
            x[0] = np.sin(x[0])
            x[1] = 2


def main():
    mol = Mol(x=np.array([[1,2],[3,4],[5,6]], dtype="float64"))



    print("hi")


if __name__ == "__main__":
    main()
