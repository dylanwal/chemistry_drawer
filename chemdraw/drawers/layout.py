import numpy as np
import plotly.graph_objs as go

from chemdraw import Molecule


class ConfigLayout:
    def __init__(self, parent):
        self.parent = parent

        self.background_color = 'rgba(255,255,255,1)'
        self.margin = dict(l=0, r=0, b=0, t=0, pad=0)
        self.show_axis = False
        self.fix_zoom = True  # remove controls to do zoom (zoom doesn't change line width and text size)
        self.dragmode = "pan"

        self.fixed_domain = True  # assumed to be square
        self.width = 600
        self.height = 600
        self.range_offset = 1
        self.range_x = None
        self.range_y = None
        self._clear_x_ranges = False
        self._clear_y_ranges = False

        self.scaling = 1

    @property
    def domain_ratio(self) -> float:
        return self.width/self.height

    @property
    def range_ratio(self) -> float:
        return self.range_x.ptp() / self.range_y.ptp()

    def get_scaling(self, molecule: Molecule, title: str):
        if self.range_x is None or self.range_y is None:
            min_ = np.min(molecule.atom_coordinates, axis=0)
            max_ = np.max(molecule.atom_coordinates, axis=0)

            if self.parent.title.show and title is not None:
                title_height = self.parent.title.text_box_size(title)
                if self.parent.title.location == "top":
                    max_ += title_height
                else:
                    min_ -= title_height

            threshold = 5 - self.range_offset
            if self.range_x is None:
                self._clear_x_ranges = True
                if max_[0] > threshold or np.abs(min_[0]) > threshold:
                    value = np.max((np.abs(min_[0] - self.range_offset), max_[0] + self.range_offset))
                    self.range_x = np.array((-value, value))
                else:
                    self.range_x = np.array([-5, 5], dtype="float64")
            if self.range_y is None:
                self._clear_y_ranges = True
                if max_[1] > threshold or np.abs(min_[1]) > threshold:
                    value = np.max((np.abs(min_[1] - self.range_offset), max_[1] + self.range_offset))
                    self.range_y = np.array((-value, value))
                else:
                    self.range_y = np.array([-5, 5], dtype="float64")

            if self.fixed_domain and self.range_y.ptp() != self.range_x.ptp():
                if self.range_x.ptp() > self.range_y.ptp():
                    self.range_y = self.range_x / self.domain_ratio
                else:
                    self.range_x = self.range_y / self.domain_ratio

            self.scaling = np.max((self.range_x.ptp(), self.range_y.ptp())) / 10

    def apply_layout(self, fig: go.Figure, legend: bool = False) -> go.Figure:
        kwargs = {
            "showlegend": legend,
            "hovermode": False,
            "plot_bgcolor": self.background_color,
            "paper_bgcolor": self.background_color,
            "dragmode": self.dragmode,
            "margin": self.margin,
        }

        xaxes_kwargs = {
            "visible": self.show_axis,
            "fixedrange": self.fix_zoom,
            "layer": "below traces",
        }

        yaxes_kwargs = {
            "visible": self.show_axis,
            "fixedrange": self.fix_zoom,
            "layer": "below traces"
        }

        # zooming
        kwargs["width"] = self.width
        if not self.fixed_domain:
            kwargs["height"] = int(self.width / self.range_ratio)
        else:
            kwargs["height"] = self.height
        xaxes_kwargs["range"] = self.range_x
        yaxes_kwargs["range"] = self.range_y

        fig.update_layout(**kwargs)
        fig.update_xaxes(**xaxes_kwargs)
        fig.update_yaxes(**yaxes_kwargs)

        self._clear_ranges()
        return fig

    def _clear_ranges(self):
        if self._clear_x_ranges:
            self.range_x = None
            self.scaling = 1
        if self._clear_y_ranges:
            self.range_y = None
            self.scaling = 1
