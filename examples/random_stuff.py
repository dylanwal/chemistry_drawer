import plotly.graph_objs as go
from rdkit import Chem
import numpy as np

import chemdraw


def points_along_line(
        pt1: list[int | float, int | float] | tuple[int | float, int | float] | np.ndarray,
        pt2: list[int | float, int | float] | tuple[int | float, int | float] | np.ndarray,
        n: int) -> np.ndarray:

    if pt2[1]-pt1[1] == 0:  # horizontal line
        x = np.linspace(pt1[0], pt2[0], n)
        return np.array([x, np.zeros_like(x)]).T
    if pt2[0]-pt1[0] == 0:  # vertical line
        y = np.linspace(pt1[1], pt2[1], n)
        return np.array([np.zeros_like(y), y]).T

    x_out = np.linspace(pt1[0], pt2[0], n)
    y_out = (pt2[1]-pt1[1])/(pt2[0]-pt1[0]) * x_out + pt1[1]

    return np.array([x_out, y_out]).T


def main():
    x = np.linspace(0, 9, 10, dtype="float64")
    print(points_along_line([0, 0], [-1, 10], 11))

    print("hi")


if __name__ == "__main__":
    main()
