import plotly.graph_objs as go
from rdkit import Chem
import numpy as np


def sort_circle_points(xy: np.ndarray) -> np.ndarray:
    # normalize data  [-1, 1]
    xy_sort = np.empty_like(xy)
    xy_sort[:, 0] = 2 * (xy[:, 0] - np.min(xy[:, 0])) / (np.max(xy[:, 0] - np.min(xy[:, 0]))) - 1
    xy_sort[:, 1] = 2 * (xy[:, 1] - np.min(xy[:, 1])) / (np.max(xy[:, 1] - np.min(xy[:, 1]))) - 1

    # get sort result
    sort_array = np.arctan2(xy_sort[:, 0], xy_sort[:, 1])
    sort_result = np.argsort(sort_array)

    # apply sort result
    return xy[sort_result]


def main():
    points = np.array(
        [
            [0, 1],
            [0, -1],
            [1, 0],
            [-1, 0],
            [1, 1],
            [-1, 1]
        ]
    )
    points = points + 5
    sorted_points = sort_circle_points(points)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=points[:, 0], y=points[:, 1], mode="lines+markers"))
    fig.add_trace(go.Scatter(x=sorted_points[:, 0], y=sorted_points[:, 1], mode="lines+markers"))
    fig.write_html("temp.html", auto_open=True)

    print("hi")


if __name__ == "__main__":
    main()
