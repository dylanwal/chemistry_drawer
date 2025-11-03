class Lines3d:
    """Stores line segments with shared style properties."""

    def __init__(self, color: str, width: float, dash: str, wave: bool):
        self.x: List[Optional[float]] = []
        self.y: List[Optional[float]] = []
        self.z: Optional[List[Optional[float]]] = None
        self.color = color
        self.width = width
        self.dash = dash  # "solid", "dot", "dash", etc.
        self.wave = wave

    def add_segment(
        self, x: List[float], y: List[float], z: Optional[List[float]] = None
    ) -> None:
        """Add a line segment, inserting None to break between segments."""
        self.x.extend(x + [None])
        self.y.extend(y + [None])
        if z is not None:
            if self.z is None:
                self.z = []
            self.z.extend(z + [None])

    def matches(self, color: str, width: float, dash: str, wave: bool) -> bool:
        return (
            self.color == color
            and self.width == width
            and self.dash == dash
            and self.wave == wave
        )

    def to_trace(self, mode: Literal["2d", "3d"]) -> go.Scatter | go.Scatter3d:
        """Convert to a Plotly line trace."""
        if mode == "3d" and self.z is not None:
            return go.Scatter3d(
                x=self.x,
                y=self.y,
                z=self.z,
                mode="lines",
                line=dict(color=self.color, width=self.width),
                hoverinfo="skip",
            )
        else:
            line_shape = "spline" if self.wave else "linear"
            return go.Scatter(
                x=self.x,
                y=self.y,
                mode="lines",
                line=dict(color=self.color, width=self.width, dash=self.dash, shape=line_shape),
                hoverinfo="skip",
            )
