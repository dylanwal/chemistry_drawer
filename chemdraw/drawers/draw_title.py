import plotly.graph_objs as go

from chemdraw.drawers.general_classes import Font
from chemdraw.objects.molecule import Molecule


class ConfigDrawerTitle:
    def __init__(self, parent):
        self.parent = parent

        self.show = True
        self.location = "bottom"  # options = ["top", "bottom"]
        self.font = Font(parent, family="Arial", size=32, bold=True, color="black")
        self.auto_wrap = True
        self.auto_wrap_length = 30
        self.pad_structure = 1
        self.line_height = 0.5

    def __repr__(self):
        return f"show: {self.show}"

    def get_font_size(self) -> float:
        return self.font.size / self.parent._scaling

    def get_pad_structure(self) -> float:
        return self.pad_structure / self.parent._scaling

    def get_line_height(self) -> float:
        return self.line_height / self.parent._scaling

    def get_text(self, text: str) -> str:
        if "\n" in text:
            text = text.replace("\n", "<br>")
        else:
            if self.auto_wrap:
                number_of_lines = int(len(text) / self.auto_wrap_length) + 1
                list_title = [text[i*self.auto_wrap_length:(i+1)*self.auto_wrap_length] for i in range(number_of_lines)]
                text = "<br>".join(list_title)

        if self.font.bold:
            text = "<b>" + text + "</b>"

        return text

    def text_box_size(self, title: str):
        return len(self.get_text(title).split("<br>")) * self.get_line_height()


def draw_title(fig: go.Figure, config: ConfigDrawerTitle, title: str, molecule: Molecule) -> go.Figure:
    if not config.show or title is None:
        return fig

    x, y = _get_position(config, title, molecule)
    fig.add_annotation(
        x=x,
        y=y,
        text=config.get_text(title),
        showarrow=False,
        align="center",
        font=dict(
            family=config.font.family,
            size=config.get_font_size(),
            color=config.font.color
        )
    )

    return fig


def _get_position(config: ConfigDrawerTitle, title: str, molecule: Molecule):
    lines_of_text = len(config.get_text(title).split("<br>"))

    # get y
    if config.location == "top":
        y = molecule.get_top_atom().coordinates[1]
        y += config.get_pad_structure()
        y += config.line_height * lines_of_text
    elif config.location == "bottom":
        y = molecule.get_bottom_atom().coordinates[1]
        y -= config.get_pad_structure()
        y -= config.line_height * lines_of_text
    else:
        raise KeyError(f"Invalid title location. {config.location}")

    # get x
    x = molecule.coordinates[0]

    return x, y
