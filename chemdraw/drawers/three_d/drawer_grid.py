import copy
import os

import plotly.graph_objs as go
import numpy as np

from chemdraw.drawers.two_d.drawer_2d import Drawer, Config
from chemdraw.objects.molecule import Molecule


class GridConfig:

    def __init__(self):
        # config
        # self.drawer_config: Config = Config()

        # grid
        self.cell_width: int = 600
        self.cell_length: int = 600

        # general options
        self.include_titles: bool = True
        self.scale_same_for_all_molecules: bool = True  # TODO: scale

        self.html_table_style: str = "table, th, td { border: 1px solid black; border-collapse: collapse;}"


def make_new_folder(folder: str):
    import os
    if not os.path.exists(folder):
        os.makedirs(folder)


def html_table_from_figs(figs: list[go.Figure], shape: tuple[int, int] | list[int, int], filelabel: str = "grid.html",
                         auto_open: bool = False, include_plotlyjs: bool = False, style: str = None):
    """
    Generates a grid of htmls

    Parameters
    ----------
    figs: list[go.Figure, str]
        list of figures to append together
    shape: tuple[int, int] | list[int, int]
        shape of grid
    filelabel:str
        file label
    auto_open: bool
        open html in browser after creating
    include_plotlyjs: bool
        makes smaller files, but needs internet to render the
    style:
        style the table

    """
    if filelabel[-5:] != ".html":
        filelabel += ".html"

    # get htmls
    if include_plotlyjs:
        kwargs = {}
    else:
        kwargs = dict(include_plotlyjs="cdn")
    fig_htmls = []
    for fig in figs:
        fig_htmls.append(fig.to_html(**kwargs).split('<body>')[1].split('</body>')[0])

    # generate html
    with open(filelabel, 'w') as file:
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
        os.system(fr"start {filelabel}")


def png_table(imgs: list[str], shape: tuple[int, int], file_label: str = "molecule_grid.png", auto_open: bool = True):
    from PIL import Image
    imgs = copy.copy(imgs)

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
            new_im.paste(im, )

        if not FLAG:
            break

    new_im.save(file_label)

    if auto_open:
        new_im.show()


class GridDrawer:

    def __init__(self,
                 molecules: list[str] | list[Molecule],
                 shape: tuple | list = None,  # [columns, rows]
                 config: Config | list[Config] = None,
                 config_grid: GridConfig = None,
                 ):
        self.molecules = molecules
        self.config = config
        self.config_grid = config_grid if config_grid is not None else GridConfig()
        self.drawers = self._get_drawers()
        self.shape = self._get_shape(shape)
        self.grid = self._get_grid()

    def _get_drawers(self) -> list[Drawer]:
        if self.config is None or isinstance(self.config, Drawer):
            return [Drawer(molecule) for molecule in self.molecules]
        if isinstance(self.config, Config):
            return [Drawer(molecule, config=self.config) for molecule in self.molecules]
        if isinstance(self.config, list):
            if len(self.molecules) != len(self.config):
                raise ValueError("'molecules' list must be the same length as 'config_drawer'")
            return [Drawer(molecule, config=drawer_config) for molecule, drawer_config in zip(self.molecules, self.config)]

        raise ValueError("'config' must be a list of Drawer instances or a Drawer instance")

    def _get_shape(self, shape: tuple | list | None) -> tuple[int, int]:
        if shape is None:
            max_dim = int(np.ceil(np.sqrt(len(self.molecules))))
            shape = np.array((max_dim, max_dim), dtype="int16")
        else:
            if shape[0] * shape[1] < len(self.drawers):
                raise ValueError(f"Shape must be a grid larger than need for the # of molecules.\n"
                                 f"Provided: {shape[0]*shape[1]}; needed: {len(self.drawers)}")

        return shape

    def _get_grid(self) -> np.ndarray:
        pass

    # def draw(self, auto_open: bool = False) -> go.Figure:
    #     fig = go.Figure()
    #
    #     # set layout for cells
    #     for drawer in self.drawers:
    #         drawer.config.layout.width = self.config.cell_width
    #
    #     for drawer, coordinates in zip(self.drawers, self.grid):
    #         drawer.molecule.coordinates = coordinates
    #         fig = drawer._draw(fig)
    #
    #     if auto_open:
    #         fig.show()
    #
    #     return fig

    def draw_html(self, file_label: str = "molecule_grid.html", auto_open: bool = False, **kwargs):
        figs = []
        for drawer in self.drawers:
            figs.append(drawer.draw())

        html_table_from_figs(figs, self.shape, file_label, auto_open=auto_open, style=self.config_grid.html_table_style,
                             **kwargs)

    def draw_png(self, file_label: str = "molecule_grid.png", folder: str = "imgs", auto_open: bool = False,
                 save_individual_imgs: bool = False):
        make_new_folder(folder)
        imgs = []
        for i, drawer in enumerate(self.drawers):
            imgs.append(drawer.draw_img(file_location=folder + f"\\img{i}.png", transparent_background=False))

        png_table(imgs, self.shape, file_label, auto_open)

        if not save_individual_imgs:
            # remove temporary images
            for img in imgs:
                os.remove(img)
