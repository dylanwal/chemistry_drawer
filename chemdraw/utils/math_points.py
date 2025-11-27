
import numpy as np
from scipy.spatial import ConvexHull


def transform_points(
    points: np.ndarray,
    move: np.ndarray | None = None,
    rotation: np.ndarray | None = None,
    scale: float | None = None,
    mirror: int | None = None,
    center: np.ndarray | None = None,
) -> np.ndarray:
    """
    Apply uniform scaling, rotation, and translation to a set of 2D or 3D points.

    Parameters
    ----------
    points : np.ndarray
        Array of shape (D, N), where D = 2 or 3.
    move: np.ndarray shape (D,), optional
        translate points in x,y,z directions.
    rotation : np.ndarray, optional
        Either a rotation matrix (DxD) or a target vector to rotate the x-axis into.
    scale : float, optional
        Uniform scaling factor.
    mirror: int, optional
        If specified, mirror only across the given axis (0 = x, 1 = y, 2 = z).
        If 3, mirror across the center in all directions (i.e., invert around center).
    center : array-like of shape (D,), optional
        New geometric center (translation target).

    Returns
    -------
    transformed : np.ndarray
        Transformed array of shape (D, N).
    """
    if points.ndim != 2 or points.shape[0] not in (2, 3):
        raise ValueError("`points` must have shape (2, N) or (3, N).")

    D = points.shape[0]
    transformed = points.copy()
    mean = transformed.mean(axis=1, keepdims=True)

    # 1. Scale
    if scale is not None:
        transformed = (transformed - mean) * scale + mean

    # 2. Rotate
    if rotation is not None:
        if rotation.shape == (D, D):
            R = rotation
        else:
            # Rotate from x-axis to target vector
            v_from = np.eye(D)[0]
            v_to = rotation
            R = rotation_matrix_from_vectors(v_from, v_to)
        transformed = R @ (transformed - mean) + mean

    # 3. Mirror
    if mirror is not None:
        transformed = rotation_matrix_from_axis_angle(transformed, mirror)

    # 4. Translate
    if move is not None:
        transformed += np.asarray(move).reshape(D, 1)
    if center is not None:
        transformed += (np.asarray(center).reshape(D, 1) - mean)

    return transformed


def rotation_matrix_from_vectors(v_from: np.ndarray, v_to: np.ndarray) -> np.ndarray:
    """
    Compute rotation matrix that rotates v_from to v_to (2D or 3D).
    """
    v_from = np.asarray(v_from, dtype=float)
    v_to = np.asarray(v_to, dtype=float)
    v_from /= np.linalg.norm(v_from)
    v_to /= np.linalg.norm(v_to)

    if v_from.shape[0] == 2:
        angle = np.arctan2(v_to[1], v_to[0]) - np.arctan2(v_from[1], v_from[0])
        c, s = np.cos(angle), np.sin(angle)
        return np.array([[c, -s], [s, c]])

    elif v_from.shape[0] == 3:
        cross = np.cross(v_from, v_to)
        dot = np.dot(v_from, v_to)
        norm_cross = np.linalg.norm(cross)
        if norm_cross < 1e-12:
            if dot > 0:
                return np.eye(3)
            # 180° rotation around an arbitrary perpendicular axis
            perp = np.array([1, 0, 0]) if abs(v_from[0]) < 0.9 else np.array([0, 1, 0])
            axis = np.cross(v_from, perp)
            axis /= np.linalg.norm(axis)
            return rotation_matrix_from_axis_angle(axis, np.pi)
        axis = cross / norm_cross
        angle = np.arctan2(norm_cross, dot)
        return rotation_matrix_from_axis_angle(axis, angle)
    else:
        raise ValueError("Only 2D or 3D vectors are supported.")


def rotation_matrix_from_axis_angle(axis: np.ndarray, angle: float) -> np.ndarray:
    """Compute a 3×3 rotation matrix using Rodrigues' formula."""
    axis = np.asarray(axis, dtype=float)
    axis /= np.linalg.norm(axis)
    K = np.array([
        [0, -axis[2], axis[1]],
        [axis[2], 0, -axis[0]],
        [-axis[1], axis[0], 0],
    ])
    I = np.eye(3)
    return I + np.sin(angle) * K + (1 - np.cos(angle)) * (K @ K)


def mirror_points_about_center(points: np.ndarray, axis: int | None = None) -> np.ndarray:
    """
    Mirror (reflect) a set of 2D or 3D points about their geometric center.

    Parameters
    ----------
    points : np.ndarray
        Array of shape (D, N), where D = 2 or 3 and each column is a point.
    axis : int, optional
        If specified, mirror only across the given axis (0 = x, 1 = y, 2 = z).
        If None, mirror across the center in all directions (i.e., invert around center).

    Returns
    -------
    mirrored : np.ndarray
        Mirrored points of shape (D, N).
    """
    if points.ndim != 2 or points.shape[0] not in (2, 3):
        raise ValueError("`points` must have shape (2, N) or (3, N).")

    center = points.mean(axis=1, keepdims=True)
    shifted = points - center  # translate center to origin

    if axis == 3:
        mirrored = -shifted  # reflect in all directions
    else:
        if not (0 <= axis < points.shape[0]):
            raise ValueError(f"`axis` must be between 0 and {points.shape[0]-1}.")
        mirrored = shifted.copy()
        mirrored[axis, :] *= -1  # flip across specified axis

    return mirrored + center  # translate back



def get_bounding_box(points: np.ndarray) -> np.ndarray:
    """
    Calculates the corner points of an axis-aligned bounding box for a set of points.

    Args:
        points (list or np.array): An array of points (Nx2 or Nx3).

    Returns:
        np.array: An array containing the corners of the bounding box.
                  (4 points for 2D, 8 points for 3D)
    """
    pts = np.asarray(points)

    if pts.shape[1] < 3:
        raise ValueError("`points` must contain at least 3 points.")

    # Find min and max along each axis (x, y, z...)
    min_vals = np.min(pts, axis=1)
    max_vals = np.max(pts, axis=1)

    # corners = list(itertools.product(*zip(min_vals, max_vals)))
    corners = np.array(
        [
            [min_vals[0], min_vals[0], max_vals[0], max_vals[0]],
            [min_vals[1], max_vals[1], max_vals[1], min_vals[1]],
        ]
    )
    return np.array(corners)

def get_bounding_box_center(points: np.ndarray) -> np.ndarray:
    return np.mean(get_bounding_box(points), axis=1)


def find_min_bbox_rotation_vector(points):
    """
    Finds the rotation vector (and angle) that minimizes the axis-aligned
    bounding box area for a set of 2D points.

    Args:
        points (list or np.array): A list of (x, y) coordinates.

    Returns:
        dict: A dictionary containing:
            - 'min_area': The area of the best fit box.
            - 'rotation_angle_deg': The angle to rotate points (in degrees).
            - 'rotation_matrix': The 2x2 matrix to apply to the points.
            - 'transformed_points': The points after rotation (axis-aligned).
            - 'bbox_width': Width of the box.
            - 'bbox_height': Height of the box.
    """
    points = np.array(points)

    # Edge case: Not enough points to form a shape
    if len(points) < 3:
        raise ValueError("At least 3 points are required.")

    # 1. Compute Convex Hull
    # We only need to check alignment with the edges of the convex hull,
    # not every pair of points.
    hull = ConvexHull(points)
    hull_points = points[hull.vertices]

    min_area = float('inf')
    best_rotation_matrix = None
    best_angle = 0
    best_transformed_points = None
    best_dims = (0, 0)

    # 2. Iterate over all edges of the convex hull
    # The minimum area rectangle must be collinear with one of the hull edges.
    num_hull_vertices = len(hull_points)

    for i in range(num_hull_vertices):
        # Get two adjacent vertices forming an edge
        p1 = hull_points[i]
        p2 = hull_points[(i + 1) % num_hull_vertices]

        # Calculate the angle of this edge relative to the X-axis
        edge_vector = p2 - p1
        # Angle of the edge
        angle = np.arctan2(edge_vector[1], edge_vector[0])

        # We want to rotate this edge to be flat (horizontal) to measure AABB.
        # So we rotate by -angle.
        rotation_angle = -angle

        # Create Rotation Matrix (2D)
        # | cos  -sin |
        # | sin   cos |
        c, s = np.cos(rotation_angle), np.sin(rotation_angle)
        R = np.array([[c, -s], [s, c]])

        # Rotate all hull points (sufficient to find bounds)
        # Using matrix multiplication: (N, 2) dot (2, 2).T -> (N, 2)
        rotated_hull = np.dot(hull_points, R.T)

        # Calculate Axis-Aligned Bounding Box (AABB) of rotated points
        min_xy = np.min(rotated_hull, axis=0)
        max_xy = np.max(rotated_hull, axis=0)

        width = max_xy[0] - min_xy[0]
        height = max_xy[1] - min_xy[1]
        area = width * height

        # Track minimum
        if area < min_area:
            min_area = area
            best_rotation_matrix = R
            best_angle = rotation_angle
            best_dims = (width, height)

            # For the final return, we rotate ALL original points, not just hull
            best_transformed_points = np.dot(points, R.T)

    # return {
    #     'min_area': min_area,
    #     'rotation_angle_rad': best_angle,
    #     'rotation_angle_deg': np.degrees(best_angle),
    #     'rotation_matrix': best_rotation_matrix,
    #     'transformed_points': best_transformed_points,
    #     'bbox_width': best_dims[0],
    #     'bbox_height': best_dims[1]
    # }
    return best_transformed_points


def tests():
    import plotly.graph_objects as go

    def main_3d_test():
            # Create square of 3D points (shape (3, N))
        points = np.array([
            [0, 0, 0],
            [.5, 1, 0],
            [1, 0, 0],
            [0, 0, 0],
            [0.5, 0.5, 0.5]
        ], dtype=float).T  # (3, 4)

        # Transform: rotate around z-axis, scale, translate
        rotation_target = np.array([0, 0, 1])  # rotate x-axis → y-axis
        center_target = np.array([1, 0, 0])
        scale_factor = 2

        transformed = transform_points(points,  rotation=rotation_target)

        # Plot
        fig = go.Figure()
        fig.add_scatter3d(x=points[0], y=points[1], z=points[2],
                          mode="lines+markers", name="Original")
        fig.add_scatter3d(x=transformed[0], y=transformed[1], z=transformed[2],
                          mode="lines+markers", name="Transformed")
        fig.update_layout(scene_aspectmode="data")
        fig.show("browser")

    def main_2d_test():
        # Create square of 3D points (shape (3, N))
        points = np.array([
            [0, 0],
            [.5, 1],
            [1, 0],
            [0, 0],
        ], dtype=float).T  # (3, 4)

        # Transform: rotate around z-axis, scale, translate
        rotation_target = np.array([1, .1])  # rotate x-axis → y-axis
        center_target = np.array([1, 0])
        scale_factor = 2

        transformed = transform_points(points,  rotation=rotation_target)

        # Plot
        fig = go.Figure()
        fig.add_scatter(x=points[0], y=points[1],
                          mode="lines+markers", name="Original")
        fig.add_scatter(x=transformed[0], y=transformed[1],
                          mode="lines+markers", name="Transformed")
        fig.update_layout(scene_aspectmode="data")
        fig.show("browser")

    def main_mirror_2d_test():
        # Create square of 3D points (shape (3, N))
        points = np.array([
            [0, 0],
            [.25, 1],
            [1, 0],
            # [0, 0],
        ], dtype=float).T  # (3, 4)


        transformed = mirror_points_about_center(points, 0)
        transformed2 = mirror_points_about_center(points, 1)

        # Plot
        fig = go.Figure()
        fig.add_scatter(x=points[0], y=points[1],
                          mode="lines+markers", name="Original")
        fig.add_scatter(x=transformed[0], y=transformed[1],
                          mode="lines+markers", name="Transformed-0")
        fig.add_scatter(x=transformed2[0], y=transformed2[1],
                      mode="lines+markers", name="Transformed-1")
        fig.update_layout(scene_aspectmode="data")
        fig.show("browser")

    def main_mirror_3d_test():
        # Create square of 3D points (shape (3, N))
        points = np.array([
            [0, 0, 0],
            [.5, 1, 0],
            [1, 0, 0],
            [0.5, 0.5, 0.5]
        ], dtype=float).T  # (3, 4)

        transformed = mirror_points_about_center(points, 0)
        transformed2 = mirror_points_about_center(points, 1)
        transformed3 = mirror_points_about_center(points, 2)

        # Plot
        fig = go.Figure()
        fig.add_scatter3d(x=points[0], y=points[1], z=points[2],
                          mode="lines+markers", name="Original")
        fig.add_scatter3d(x=transformed[0], y=transformed[1], z=transformed[2],
                          mode="lines+markers", name="Transformed-0")
        fig.add_scatter3d(x=transformed2[0], y=transformed2[1], z=transformed2[2],
                      mode="lines+markers", name="Transformed-1")
        fig.add_scatter3d(x=transformed3[0], y=transformed3[1], z=transformed3[2],
                      mode="lines+markers", name="Transformed-2")
        fig.update_layout(scene_aspectmode="data")
        fig.show("browser")


    main_2d_test()
    main_3d_test()
    main_mirror_2d_test()
    main_mirror_3d_test()


if __name__ == "__main__":
    tests()
