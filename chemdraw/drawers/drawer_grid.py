import math

import plotly.graph_objs as go
import numpy as np

from chemdraw.drawers.drawer import Drawer, DrawerConfig
from chemdraw.objects.molecule import Molecule


class GridConfig:

    def __init__(self):
        # config
        self.drawer_config: DrawerConfig = DrawerConfig()

        # grid
        self.grid_ratio: int = 1  # length/layout_width
        self.max_width: int | None = 5  # only fill out one [max_width, or max_length]; only used if shape not provided
        self.max_length: int | None = None  # only fill out one [max_width, or max_length]; only used if shape not provided

        # general options
        self.include_titles: bool = True

        self.html_table_style: str = "table, th, td { border: 1px solid black; border-collapse: collapse;}"


def make_new_folder(folder: str):
    import os
    if not os.path.exists(folder):
        os.makedirs(folder)


def html_table_from_figs(figs: list[go.Figure], shape: tuple[int, int] | list[int, int], filename: str = "grid.html",
                         auto_open: bool = False, include_plotlyjs: bool = False, style: str = None):
    """
    Generates a grid of htmls

    Parameters
    ----------
    figs: list[go.Figure, str]
        list of figures to append together
    shape: tuple[int, int] | list[int, int]
        shape of grid
    filename:str
        file name
    auto_open: bool
        open html in browser after creating
    include_plotlyjs: bool
        makes smaller files, but needs internet to render the
    style:
        style the table

    """
    if filename[-5:] != ".html":
        filename += ".html"

    # get htmls
    if include_plotlyjs:
        kwargs = {}
    else:
        kwargs = dict(include_plotlyjs="cdn")
    fig_htmls = []
    for fig in figs:
        fig_htmls.append(fig.to_html(**kwargs).split('<body>')[1].split('</body>')[0])

    # generate html
    with open(filename, 'w') as file:
        file.write(f'<html>\n<head><meta charset="utf-8" /></head><body>')
        if style is not None:
            file.write("<style>" + style + "</style>")

        file.write('<table>')
        FLAG = True
        for row in range(shape[1]):
            file.write("<tr>")
            for col in range(shape[0]):
                try:
                    html = fig_htmls.pop(0)
                except IndexError:
                    FLAG = False
                    break
                file.write("<td>" + html + "</td>")

            file.write("</tr>")
            if not FLAG:
                break

        file.write('</table>')
        file.write("</body></html>" + "\n")

    if auto_open:
        import os
        os.system(fr"start {filename}")


def png_table(imgs: list[str], shape: tuple[int, int], file_name: str = "molecule_grid.png", auto_open: bool = True):
    from PIL import Image
    im = Image.open(imgs[0])

    cell_width = im.width
    cell_height = im.height

    new_im = Image.new('RGB', (cell_width * shape[0], cell_height * shape[1]))

    FLAG = True
    for row in range(shape[1]):
        for col in range(shape[0]):
            try:
                img = imgs.pop(0)
            except IndexError:
                FLAG = False
                break
            im = Image.open(img)
            new_im.paste(im, (col*cell_width, row*cell_height))

        if not FLAG:
            break

    new_im.save(file_name)

    if auto_open:
        new_im.show()


class GridDrawer:

    def __init__(self,
                 molecules: list[str] | list[Molecule],
                 shape: tuple | list = None,  # [columns, rows]
                 config: GridConfig = None
                 ):
        self.molecules = molecules
        self.config = config if config is not None else GridConfig()
        self.drawers = [Drawer(molecule, config=self.config.drawer_config) for molecule in self.molecules]
        self.shape = self._get_shape(shape)
        self.grid = self._get_grid(self.shape)

    def _get_shape(self, shape: tuple | list | None) -> tuple[int, int]:
        if shape is not None:
            if shape[0] * shape[1] < len(self.drawers):
                raise ValueError(f"Shape must be a grid larger than need for the # of molecules.\n"
                                 f"Provided: {shape[0]*shape[1]}; needed: {len(self.drawers)}")
            return shape

        if self.config.max_width is not None:
            return self.config.max_width, int(math.ceil(len(self.drawers)/self.config.max_width))
        elif self.config.max_width is not None:
            return int(math.ceil(len(self.drawers)/self.config.max_length)), self.config.max_length
        else:
            raise ValueError("Can't determine grid shape. ")

    def _get_grid(self, shape) -> np.ndarray:
        pass

    # def draw(self):
    # subplots
    #     from plotly.subplots import make_subplots
    #     fig = make_subplots(
    #         rows=self.shape[1], cols=self.shape[0],
    #         horizontal_spacing=0.25,
    #         vertical_spacing=0.1 * 3 / self.shape[1]
    #     )
    #
    #     for i, drawer in enumerate(self.drawers):
    #         # get index for current subplot
    #         row_index = int(i / self.shape[0]) + 1
    #         cols_index = i % self.shape[0] + 1
    #
    #         fig = drawer._draw(fig)
    #
    #         # # create heatmap
    #         # df = pd.DataFrame(datum, columns=["x", "y"])
    #         # canvas = ds.Canvas(plot_width=res, plot_height=res)
    #         # agg = canvas.points(df, 'x', 'y')
    #         # fig.add_trace(go.Heatmap(x=x, y=y, z=agg,
    #         #                          colorbar=dict(len=1 / rows, x=colorbar_pos[i][0], y=colorbar_pos[i][1],
    #         #                                        title="count")),
    #         #               row=row_index, col=cols_index)
    #         #
    #         # # set axis values
    #         # fig.update_xaxes(title="<b>x (cm)</b>", row=row_index, col=cols_index)
    #         # fig.update_yaxes(title="<b>y (cm)</b>", row=row_index, col=cols_index)
    #         #
    #         # # final formatting and save
    #         # fig.update_layout(height=400 * rows, width=600 * cols, title_text=title)
    #         # if not file_name.endswith(".html"):
    #         #     file_name += ".html"

    def draw_html(self, file_name: str = "molecule_grid.html", auto_open: bool = False, **kwargs):
        figs = []
        for drawer in self.drawers:
            figs.append(drawer.draw())

        html_table_from_figs(figs, self.shape, file_name, auto_open=auto_open, style=self.config.html_table_style,
                             **kwargs)

    def draw_png(self, file_name: str = "molecule_grid.png", folder: str = "imgs", auto_open: bool = False):
        make_new_folder(folder)
        imgs = []
        for i, drawer in enumerate(self.drawers):
            imgs.append(drawer.draw_img(file_location=folder + f"\\img{i}.png"))

        png_table(imgs, self.shape, file_name, auto_open)
