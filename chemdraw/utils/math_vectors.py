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


# def shorten_line(x0: float, x1: float, y0: float, y1: float, short_percent: float) -> (float, float, float, float):
#     if short_percent == 1 or short_percent < 0:
#         return x0, x1, y0, y1
#
#     if (x1 - x0) == 0:
#         # vertical line
#         length = y0 - y1
#         cut_distance = (1 - short_percent) / 2 * length
#         return x0, x1, y0 + cut_distance, y1 - cut_distance
#
#     if (y1 - y0) == 0:
#         # horizontal line
#         length = x0 - x1
#         cut_distance = (1 - short_percent) / 2 * length
#         return x0 - cut_distance, x1 + cut_distance, y0, y1
#
#     # line with slope
#     slope = (y1 - y0) / (x1 - x0)
#     intercept = y0 - slope * x0
#     length = pythagoras_theorem([x0, y0], [x1, y1])
#     cut_distance = (1 - short_percent) / 2 * length
#
#     # quadratic formula
#     a = 1 + slope ** 2
#     b = 2 * intercept * slope - 2 * y0 * slope - 2 * x0
#     c = x0 ** 2 + intercept ** 2 - 2 * y0 * intercept + y0 ** 2 - cut_distance ** 2
#     x0_new = (-b + (b ** 2 - 4 * a * c) ** (1 / 2)) / (2 * a)
#     if short_percent < 1:
#         if not (x0 < x0_new < x1):
#             # use second solution to quadratic formula
#             x0_new = (-b - (b ** 2 - 4 * a * c) ** (1 / 2)) / (2 * a)
#     else:  # if short_percent > 1
#         if x0 < x0_new < x1:
#             # use second solution to quadratic formula
#             x0_new = (-b - (b ** 2 - 4 * a * c) ** (1 / 2)) / (2 * a)
#
#     y0_new = slope * x0_new + intercept
#     x1_new = x1 - (x0_new - x0)
#     y1_new = slope * x1_new + intercept
#
#     return x0_new, x1_new, y0_new, y1_new

def shorten_line(x0: float, x1: float, y0: float, y1: float, short_percent: float) -> tuple[float, float, float, float]:
    if short_percent >= 1 or short_percent < 0:
        return x0, x1, y0, y1

    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    cut_distance = (1 - short_percent) / 2 * length

    if dx == 0:  # Vertical line
        return x0, x1, y0 + cut_distance, y1 - cut_distance
    if dy == 0:  # Horizontal line
        return x0 + cut_distance, x1 - cut_distance, y0, y1

    # General case for sloped lines
    scale = cut_distance / length
    x0_new, y0_new = x0 + dx * scale, y0 + dy * scale
    x1_new, y1_new = x1 - dx * scale, y1 - dy * scale

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
