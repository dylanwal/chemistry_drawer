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


def find_rectangle_intersection(box: np.ndarray, vector: np.ndarray) -> np.ndarray:
    """
    Calculates the intersection point where a line segment exits a rectangle.

    Assumes exactly one point of the segment is inside the box and one is outside.

    Args:
        box (np.ndarray): 2x2 array defining the box limits:
                          [[x_min, x_max],
                           [y_min, y_max]]
        vector (np.ndarray): 2x2 array defining the segment points as columns:
                             [[x1, x2],
                              [y1, y2]]

    Returns:
        np.ndarray: (x, y) coordinates of the intersection point.

    Raises:
        ValueError: If the segment is entirely inside or entirely outside the box.
    """
    # 1. Identify bounds
    x_min, x_max = box[0]
    y_min, y_max = box[1]

    # 2. Check which points are inside the box
    # Point 0
    p0 = vector[:, 0]
    p0_in_x = x_min <= p0[0] <= x_max
    p0_in_y = y_min <= p0[1] <= y_max
    p0_in_box = p0_in_x and p0_in_y

    # Point 1
    p1 = vector[:, 1]
    p1_in_x = x_min <= p1[0] <= x_max
    p1_in_y = y_min <= p1[1] <= y_max
    p1_in_box = p1_in_x and p1_in_y

    # 3. Validate "One In, One Out" rule
    if p0_in_box and p1_in_box:
        raise ValueError("Both points are inside the box. No intersection with boundary.")
    if not p0_in_box and not p1_in_box:
        raise ValueError("Both points are outside the box. (Function assumes start-inside logic).")

    # 4. Define Ray: Origin (P_in) -> Direction (P_out - P_in)
    if p0_in_box:
        P_in = p0
        P_out = p1
    else:
        P_in = p1
        P_out = p0

    direction = P_out - P_in

    # 5. Calculate intersection 't' for all 4 infinite boundary lines
    # Line eq: P(t) = P_in + t * direction
    # We want the smallest positive t where the point is ON the box boundary.

    candidates = []

    # Check Vertical Walls (x_min, x_max)
    if direction[0] != 0:
        t_xmin = (x_min - P_in[0]) / direction[0]
        t_xmax = (x_max - P_in[0]) / direction[0]
        candidates.extend([t_xmin, t_xmax])

    # Check Horizontal Walls (y_min, y_max)
    if direction[1] != 0:
        t_ymin = (y_min - P_in[1]) / direction[1]
        t_ymax = (y_max - P_in[1]) / direction[1]
        candidates.extend([t_ymin, t_ymax])

    # 6. Filter and find the best 't'
    best_t = float('inf')
    found_valid = False

    # Floating point tolerance
    epsilon = 1e-9

    for t in candidates:
        # We only care about t > 0 (moving forward from inside point)
        # and t <= 1 (must be within the segment length)
        if t > epsilon and t <= 1.0 + epsilon:

            # Calculate the intersection point for this specific t
            intersect = P_in + t * direction

            # Check if this point is actually on the box boundary
            # (e.g. if we hit the x=x_max plane, is y within [y_min, y_max]?)
            if (x_min - epsilon <= intersect[0] <= x_max + epsilon) and \
               (y_min - epsilon <= intersect[1] <= y_max + epsilon):

                if t < best_t:
                    best_t = t
                    found_valid = True

    if not found_valid:
        raise ValueError("Calculation Error: Could not find valid intersection on boundary.")

    return P_in + best_t * direction