import math

import numpy as np


def normalize(vector: np.ndarray) -> np.ndarray:
    """
    vector = np.array([x,y])
    Object is guaranteed to be a unit quaternion after calling this
    operation UNLESS the object is equivalent to Quaternion(0)
    """
    n = np.sqrt(np.dot(vector, vector))
    if n > 0:
        return vector / n
    else:
        return vector


def pythagoras_theorem(point1: np.ndarray, point2: np.ndarray) -> float:
    return ((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2) ** (1 / 2)


def perpendicular(vector: np.ndarray) -> np.ndarray:
    """
    vector = np.array([x,y])
    """
    return np.array([-vector[1], vector[0]])


def shorten_line(x: np.ndarray, y: np.ndarray, percent: float, direction: int | None = None) -> tuple[np.ndarray, np.ndarray]:
    """

    Parameters
    ----------
    x: np.ndarray
    y: np.ndarray
    percent: float
        0<x<1
    direction: int | None
        None: shorten from both sides
        0 shorten from the x[0], y[0] side
        1 shorten from the x[1], y[1] side

    Returns
    -------

    """
    if percent == 1:
        return x, y
    if not (0 <= percent < 1):
        raise ValueError("Short percent must be between 0 and 1.")
    if direction not in [None, 0, 1]:
        raise ValueError("direction must be None, 0, or 1.")

    dx = x[1] - x[0]
    dy = y[1] - y[0]
    percent = 1 - percent

    # Direction None: Shorten from both sides equally
    if direction is None:
        p = percent / 2
        new_x = np.array([x[0] + dx * p, x[1] - dx * p])
        new_y = np.array([y[0] + dy * p, y[1] - dy * p])
        return new_x, new_y

    # Direction 0: Shorten from the start (x[0], y[0])
    # We add the vector fraction to move the start point "forward"
    if direction == 0:
        new_x = np.array([x[0] + dx * percent, x[1]])
        new_y = np.array([y[0] + dy * percent, y[1]])
        return new_x, new_y

    # Direction 1: Shorten from the end (x[1], y[1])
    # We subtract the vector fraction to move the end point "backward"
    # (Implicit else for direction == 1)
    new_x = np.array([x[0], x[1] - dx * percent])
    new_y = np.array([y[0], y[1] - dy * percent])
    return new_x, new_y


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
    dot = current_vector[0] * new_vector[0] + current_vector[1] * new_vector[1]  # dot product
    det = current_vector[0] * new_vector[1] - current_vector[1] * new_vector[0]  # determinant
    theta = np.arctan2(det, dot)
    cos_, sin_ = np.cos(theta), np.sin(theta)
    return np.array(((cos_, sin_), (-sin_, cos_)))


def get_triangle_vertices(
        base_center: np.ndarray,
        height: int | float,
        vector_to_tip: np.ndarray,
        base_width: int | float = None
):
    """
    Calculates the 3 vertices of a triangle given a base center, height,
    and a direction vector pointing to the tip.

    Args:
        base_center (list or np.array): The [x, y] or [x, y, z] coordinates of the base center.
        height (float): The distance from the base center to the tip.
        vector_to_tip (list or np.array): A vector indicating the direction from base to tip.
                                          (Does not need to be normalized).
        base_width (float, optional): The width of the base. If None, calculates width
                                      for an Equilateral triangle.

    Returns:
        np.array: A 3xN array containing the 3 points of the triangle.
                  [Tip_Point, Base_Point_Left, Base_Point_Right]
    """

    # 1. Convert inputs to numpy arrays for vector math
    center = np.array(base_center, dtype=float)
    direction = np.array(vector_to_tip, dtype=float)

    # 2. Validate dimensions (2D or 3D)
    dim = len(center)
    if len(direction) != dim:
        raise ValueError("Base center and direction vector must have the same dimensions.")

    # 3. Normalize the direction vector (Tip Direction)
    # This ensures we just get the direction, and scale it by 'height' manually
    norm = np.linalg.norm(direction)
    if norm == 0:
        raise ValueError("Vector to tip cannot be zero.")
    unit_up = direction / norm

    # 4. Calculate the Tip Point
    # Tip = Center + (UnitDirection * Height)
    tip_point = center + (unit_up * height)

    # 5. Determine Base Width
    if base_width is None: # assume an Equilateral Triangle
        base_width = (2 * height) / np.sqrt(3)
    half_width = base_width / 2.0

    # 6. Calculate the Base Vector (Perpendicular to Up)
    unit_right = np.array([-unit_up[1], unit_up[0]])

    # 7. Calculate Base Points
    # Move left and right from the center along the perpendicular vector
    p2 = center - (unit_right * half_width)
    p3 = center + (unit_right * half_width)

    # 8. Return the 3 points
    # Format: [Tip, Left_Base, Right_Base]
    return np.array([tip_point, p2, p3, tip_point])


def get_furthest_direction(vectors: list[np.ndarray]) -> np.ndarray:
    """
    Finds the unit vector direction that maximizes the angular distance
    from a list of 3 input 2D unit vectors.

    Args:
        vectors (list or np.array): A list of 3 vectors, e.g., [[1,0], [0,1], [-1,0]]

    Returns:
        np.array: The unit vector representing the furthest direction.
    """
    # 1. Convert vectors to angles (radians) in range (-pi, pi]
    # np.arctan2 handles the quadrants correctly regardless of magnitude
    angles = [np.arctan2(v[1], v[0]) for v in vectors]

    # 2. Sort the angles to find adjacent differences
    angles.sort()

    # 3. Calculate the gaps (arc lengths) between adjacent vectors
    # We have 3 vectors, so we have 3 gaps.
    # Gap 1: Between Angle 2 and Angle 1
    # Gap 2: Between Angle 3 and Angle 2
    # Gap 3: The wrap-around gap between Angle 1 and Angle 3

    gaps = []
    # Normal adjacent gaps
    for i in range(len(angles) - 1):
        gaps.append(angles[i+1] - angles[i])

    # Wrap-around gap (crossing the 180/-180 degree cut)
    # Formula: (2*pi - last_angle) + first_angle
    wrap_gap = (2 * np.pi - angles[-1]) + angles[0]
    gaps.append(wrap_gap)

    # 4. Find the index of the largest gap
    max_gap_index = np.argmax(gaps)
    max_gap = gaps[max_gap_index]

    # 5. Calculate the angle exactly in the middle of that largest gap
    if max_gap_index < len(angles) - 1:
        # Normal case: Average the two angles defining the gap
        # OR: Start angle + half the gap
        optimal_angle = angles[max_gap_index] + (max_gap / 2.0)
    else:
        # Wrap-around case: Start at the last angle, add half the gap,
        # and normalize if it exceeds pi (though sin/cos handle overflow fine)
        optimal_angle = angles[-1] + (max_gap / 2.0)

    # 6. Convert the optimal angle back to a unit vector
    return normalize(np.array([np.cos(optimal_angle), np.sin(optimal_angle)]))


def local_run():
    import plotly.graph_objs as go

    a = (1.3, 2.1)
    vector = (-1, -1)
    offset = 0.5

    b = offset_point_vector(a[0], a[1], vector, offset)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[a[0]], y=[a[1]], mode="markers"))
    fig.add_trace(go.Scatter(x=[a[0], a[0] + vector[0]], y=[a[1], a[1] + vector[1]], mode="lines"))
    fig.add_trace(go.Scatter(x=[b[0]], y=[b[1]], mode="markers", marker=dict(color="red")))
    fig.show()


if __name__ == "__main__":
    local_run()
