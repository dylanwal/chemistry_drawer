import plotly.graph_objs as go
from rdkit import Chem
import numpy as np


def main():
    xy = np.array([[1,1], [2,2], [3,3], [None, None], [5, 5], [6,6]])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xy[:, 0], y=xy[:, 1], mode="lines+markers"))
    fig.show()

    print("hi")


if __name__ == "__main__":
    main()
