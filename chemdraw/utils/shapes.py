
import numpy as np

import chemdraw.utils.vector_math as vector_math


def slot_shape(x: np.array, y: np.array, width: float, points_on_ends: int = 10) -> np.ndarray:
    half_width = width/2
    xy = np.empty((points_on_ends*2, 2), dtype="float64")
    vector = vector_math.normalize(np.array((x[1] - x[0], y[1] - y[0])))
    perpendicular = np.array([-vector[1], vector[0]])

    xy[0, :] = (x[0] + perpendicular[0] * half_width, y[0] + perpendicular[1] * half_width)

    return xy
