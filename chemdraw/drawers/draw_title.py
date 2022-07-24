
import plotly.graph_objs as go

from chemdraw.objects.molecule import Molecule


class ConfigDrawerTitle:
    show = True
    location = "bottom"  # options = ["top", "bottom"]
    font = "Arial"
    font_color = "black"
    font_size = 32
    font_bold = True
    auto_wrap = True
    auto_wrap_length = 30
    pad_structure = 1
    line_height = 0.3

    def __repr__(self):
        return f"show: {self.show}"


def draw_title(fig: go.Figure, config: ConfigDrawerTitle, title: str, molecule: Molecule) -> go.Figure:
    if not config.show or title is None:
        return fig

    title = _get_text(config, title)
    x, y = _get_position(config, title, molecule)
    fig.add_annotation(
        x=x,
        y=y,
        text=title,
        showarrow=False,
        align="center",
        font=dict(
            family=config.font,
            size=config.font_size,
            color=config.font_color
        )
    )

    return fig


def _get_text(config: ConfigDrawerTitle, title: str) -> str:
    if config.auto_wrap:
        number_of_lines = int(len(title) / config.auto_wrap_length) + 1
        list_title = [title[i::number_of_lines] for i in range(number_of_lines)]
        title = "<br>".join(list_title)

    if config.font_bold:
        title = "<b>" + title + "</b>"

    return title


def _get_position(config: ConfigDrawerTitle, title: str, molecule: Molecule):
    lines_of_text = title.count("<br>")

    # get y
    if config.location == "top":
        y = molecule.get_top_atom().coordinates[1]
        y += config.pad_structure
        y += config.line_height * lines_of_text
    elif config.location == "bottom":
        y = molecule.get_bottom_atom().coordinates[1]
        y -= config.pad_structure
        y -= config.line_height * lines_of_text
    else:
        raise KeyError(f"Invalid title location. {config.location}")

    # get x
    x = molecule.coordinates[0]

    return x, y
