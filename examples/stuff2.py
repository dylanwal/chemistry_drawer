import numpy as np
from scipy.spatial import ConvexHull

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

    return {
        'min_area': min_area,
        'rotation_angle_rad': best_angle,
        'rotation_angle_deg': np.degrees(best_angle),
        'rotation_matrix': best_rotation_matrix,
        'transformed_points': best_transformed_points,
        'bbox_width': best_dims[0],
        'bbox_height': best_dims[1]
    }

def visualize_results(original_points, result):
    """
    Visualizes the original points and the optimized bounding box.
    """
    try:
        import matplotlib.pyplot as plt
        from matplotlib.patches import Polygon
    except ImportError:
        print("Matplotlib not installed. Skipping visualization.")
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

    # Plot 1: Original Points
    ax1.scatter(original_points[:, 0], original_points[:, 1], c='blue', label='Points')
    ax1.set_title("Original Points")
    ax1.set_aspect('equal')
    ax1.grid(True)

    # Calculate corners of the bbox in original space for visualization
    # We take the aligned box corners and apply the INVERSE rotation
    tp = result['transformed_points']
    min_x, min_y = np.min(tp, axis=0)
    max_x, max_y = np.max(tp, axis=0)

    corners_aligned = np.array([
        [min_x, min_y],
        [max_x, min_y],
        [max_x, max_y],
        [min_x, max_y]
    ])

    # Inverse rotate: P_orig = P_rot * R_inv
    # Since R is orthogonal, R_inv = R.T
    R = result['rotation_matrix']
    corners_original = np.dot(corners_aligned, R) # R.T.T = R

    # Draw box on original plot
    poly = Polygon(corners_original, closed=True, fill=False, edgecolor='red', linewidth=2, label='Min Area Box')
    ax1.add_patch(poly)
    ax1.legend()

    # Plot 2: Rotated Points (Axis Aligned)
    ax2.scatter(tp[:, 0], tp[:, 1], c='green', label='Rotated Points')

    # Draw axis aligned box
    rect = plt.Rectangle((min_x, min_y), max_x-min_x, max_y-min_y,
                         fill=False, edgecolor='red', linewidth=2, label='Aligned Box')
    ax2.add_patch(rect)

    ax2.set_title(f"Rotated (Angle: {result['rotation_angle_deg']:.2f}°)")
    ax2.set_aspect('equal')
    ax2.grid(True)
    ax2.legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Generate random points
    np.random.seed(42)
    # Create a cluster of points that is clearly elongated diagonally
    # to test if the algorithm finds the diagonal rotation
    mean = [10, 10]
    cov = [[20, 15], [15, 20]]  # Diagonal covariance
    points = np.random.multivariate_normal(mean, cov, 50)

    try:
        result = find_min_bbox_rotation_vector(points)

        print("-" * 30)
        print("OPTIMIZATION RESULTS")
        print("-" * 30)
        print(f"Minimum Area: {result['min_area']:.4f}")
        print(f"Rotation Angle: {result['rotation_angle_deg']:.2f} degrees")
        print(f"Rotation Matrix:\n{result['rotation_matrix']}")
        print(f"Box Dimensions: {result['bbox_width']:.2f} x {result['bbox_height']:.2f}")

        visualize_results(points, result)

    except Exception as e:
        print(f"Error: {e}")