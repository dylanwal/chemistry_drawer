import numpy as np


def map_data(
        old_values: int | float | tuple[int | float] | list[int | float] | np.ndarray,
        new_range: tuple[int | float, int | float] | list[int | float, int | float] | np.ndarray,
        old_range: tuple[int | float, int | float] | list[int | float, int | float] | np.ndarray = None,
) -> int | float | np.ndarray:

    if old_range is None:
        if not isinstance(old_values, (float, int)):
            old_range = (min(old_values), max(old_values))
        else:
            raise ValueError("Provide an 'old_range' if 'old_values' are int or float.")

    return (new_range[1]-new_range[0]) / (old_range[1]-old_range[0]) * old_values + new_range[0]


def get_offset_points(xy: list[int | float, int | float] | tuple[int | float, int | float] | np.ndarray,
                      perpendicular: np.ndarray,
                      offset: float | int) \
        -> np.ndarray:
    x_left = xy[0] + perpendicular[0] * offset
    x_right = xy[0] - perpendicular[0] * offset
    y_left = xy[1] + perpendicular[1] * offset
    y_right = xy[1] - perpendicular[1] * offset

    return np.array([[x_left, y_left], [x_right, y_right]])


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
    y_out = (pt2[1]-pt1[1])/(pt2[0]-pt1[0]) * (x_out - pt1[0]) + pt1[1]

    return np.array([x_out, y_out]).T

