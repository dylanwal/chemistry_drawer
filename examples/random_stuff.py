import plotly.graph_objs as go
from rdkit import Chem
import numpy as np


def main():
    xy = np.array([[1,1], [2,5], [3,3], [None, None], [3, 3], [6,6]])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xy[:, 0], y=xy[:, 1], mode="lines+markers", marker=dict(color="rgba(255,0,0,0.5)", size=40),
                             line=dict(color="rgba(255,0,0,0.5)", width=30)))
    fig.show()

    print("hi")


if __name__ == "__main__":
    main()
