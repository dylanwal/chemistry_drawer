import math

import numpy as np


def normalize(vector: np.ndarray) -> np.ndarray:
    """
    Object is guaranteed to be a unit quaternion after calling this
    operation UNLESS the object is equivalent to Quaternion(0)
    """
    n = np.sqrt(np.dot(vector, vector))
    if n > 0:
        return vector / n
    else:
        return vector


def shorten_line(x0: float, x1: float, y0: float, y1: float, short_percent: float) -> (float, float, float, float):
    if short_percent == 1 or short_percent < 0:
        return x0, x1, y0, y1

    if (x1 - x0) == 0:
        # vertical line
        length = y0 - y1
        cut_distance = (1 - short_percent) / 2 * length
        return x0, x1, y0 + cut_distance, y1 - cut_distance

    if (y1 - y0) == 0:
        # horizontal line
        length = x0 - x1
        cut_distance = (1 - short_percent) / 2 * length
        return x0 - cut_distance, x1 + cut_distance, y0, y1

    # line with slope
    slope = (y1 - y0) / (x1 - x0)
    intercept = y0 - slope * x0
    length = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** (1 / 2)
    cut_distance = (1 - short_percent) / 2 * length

    # quadratic formula
    a = 1 + slope ** 2
    b = 2 * intercept * slope - 2 * y0 * slope - 2 * x0
    c = x0 ** 2 + intercept ** 2 - 2 * y0 * intercept + y0 ** 2 - cut_distance ** 2
    x0_new = (-b + (b ** 2 - 4 * a * c) ** (1 / 2)) / (2 * a)
    if short_percent < 1:
        if not (x0 < x0_new < x1):
            # use second solution to quadratic formula
            x0_new = (-b - (b ** 2 - 4 * a * c) ** (1 / 2)) / (2 * a)
    else:  # if short_percent > 1
        if x0 < x0_new < x1:
            # use second solution to quadratic formula
            x0_new = (-b - (b ** 2 - 4 * a * c) ** (1 / 2)) / (2 * a)

    y0_new = slope * x0_new + intercept
    x1_new = x1 - (x0_new - x0)
    y1_new = slope * x1_new + intercept

    return x0_new, x1_new, y0_new, y1_new


def offset_point_vector(x0: float, y0: float, vector: tuple[float, float] | list[float, float] | np.ndarray,
         offset: float) -> tuple[float, float]:
    if vector[0] == 0:
        if vector[1] == 0:
            return x0, y0
        else:
            # vertical vector
            return x0, y0 + offset * math.copysign(1, vector[1])
    if vector[1] == 0:
        # horizontal vector
        return x0 + offset * math.copysign(1, vector[0]), y0

    # diagonal vector
    vector = normalize(vector)
    vector = vector * offset
    return x0 + vector[0], y0 + vector[1]


def rotation_matrix(current_vector: np.ndarray, new_vector: np.ndarray) -> np.ndarray:
    if np.all(current_vector == new_vector):
        return np.array([[1, 0], [0, 1]], dtype="float64")
    dot = current_vector[0]*new_vector[0] + current_vector[1]*new_vector[1]     # dot product
    det = current_vector[0]*new_vector[1] - current_vector[1]*new_vector[0]     # determinant
    theta = np.arctan2(det, dot)
    cos_, sin_ = np.cos(theta), np.sin(theta)
    return np.array(((cos_, sin_), (-sin_, cos_)))


def local_run():
    import plotly.graph_objs as go

    a = (1.3, 2.1)
    vector = (-1, -1)
    offset = 0.5

    b = offset_point_vector(a[0], a[1], vector, offset)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[a[0]], y=[a[1]], mode="markers"))
    fig.add_trace(go.Scatter(x=[a[0], a[0]+vector[0]], y=[a[1], a[1]+vector[1]], mode="lines"))
    fig.add_trace(go.Scatter(x=[b[0]], y=[b[1]], mode="markers", marker=dict(color="red")))
    fig.show()


if __name__ == "__main__":
    local_run()
