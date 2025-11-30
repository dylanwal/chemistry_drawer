import os
import pathlib
from typing import Sequence


from chemdraw.objects.molecule import Molecule
from chemdraw.config.style_template import STYLE_TEMPLATE
import chemdraw.drawers.two_d.draw_debug as draw_debug
import chemdraw.drawers.two_d.draw_label as draw_label
import chemdraw.drawers.two_d.draw_atoms as draw_atoms
import chemdraw.drawers.two_d.draw_bonds as draw_bonds
import chemdraw.drawers.two_d.draw_atom_numbers as draw_atom_numbers
import chemdraw.drawers.two_d.draw_bond_numbers as draw_bond_numbers
import chemdraw.drawers.two_d.draw_ring_numbers as draw_ring_numbers
# import chemdraw.drawers.draw_parenthesis as draw_parenthesis
import chemdraw.drawers.two_d.draw_highlights as draw_highlights
# import chemdraw.drawers.draw_ring_highlights as draw_ring_highlights

from chemdraw.drawers.two_d.primitives_for_drawing import DrawingContainer, DrawingContainerGrid


DRAWERS = {
        "bonds": draw_bonds.draw_bonds,
        "atoms": draw_atoms.draw_atoms,
        "label": draw_label.draw_label,
        "debug": draw_debug.draw_debug,
        "atom_numbers": draw_atom_numbers.draw_atom_numbers,
        "bond_numbers": draw_bond_numbers.draw_bond_numbers,
        "ring_numbers": draw_ring_numbers.draw_ring_numbers,
        "highlights": draw_highlights.draw_highlights,
        # "ring_highlights": draw_ring_highlights.draw_ring_highlight,
        # "parenthesis": draw_parenthesis.draw_parenthesis,
    }

### drawing (first in list is drawn at the bottom)
# 'label' should be last as it needs the molecule built to know where it should be.
# self.draw_order = ["ring_highlights", "highlights", "parenthesis", ]
DRAW_ORDER = ["highlights", "bonds", "atoms", "debug", "bond_numbers", "atom_numbers", "ring_numbers", "label"]


def draw(molecule: str | Molecule):
    """
    Return a figure object for a single molecule.
    Figure object depends on plotting package used.

    Parameters
    ----------
    molecule: str | Molecule
        str = SMILES string

    Returns
    -------
    Plotly: go.Figure
    Matplotlib: plt.subplots

    """
    if isinstance(molecule, str):
        molecule = Molecule(molecule, label=molecule)

    container = DrawingContainer("base")
    for key in DRAW_ORDER:
        drawer = DRAWERS[key]
        drawer(container, molecule)

    container = container.prepare_for_drawing()
    plotter = STYLE_TEMPLATE.get_plotter()

    return plotter(container)


def draw_grid(
        molecules: Sequence[str] | Sequence[Molecule],
        shape: Sequence[int] | None = None,
):
    """
    Returns a figure object for a grid of molecules.

    Recommendation: show or generate svg file. If you need png file, use 'draw_grid_png'.

    Parameters
    ----------
    molecules: Sequence[str | Molecule]
        molecules to draw
        str = SMILES string
    shape: Sequence[int]
        if len(shape) == 2: it will be interpreted as (number of rows, number of columns)
        Sequence of integers representing the number of molecules in each row
        None = auto-determine

    Returns
    -------
    Plotly: go.Figure
    Matplotlib: plt.subplots

    """
    if isinstance(molecules[0], str):
        molecules = (Molecule(m) for m in molecules)

    container_grid = DrawingContainerGrid(shape)
    for m in molecules:
        container = DrawingContainer("base")
        for key in DRAW_ORDER:
            drawer = DRAWERS[key]
            drawer(container, m)
        container_grid.add(container)

    container_grid = container_grid.prepare_for_drawing()
    plotter = STYLE_TEMPLATE.get_plotter()

    return plotter(container_grid)


def draw_multiple_images(
        molecules: Sequence[str] | Sequence[Molecule],
        type_: str = "png",
        out_folder: str | pathlib.Path = "imgs",
        num_processes: int | None = None,
) -> None:
    """

    Parameters
    ----------
    molecules: Sequence[str | Molecule]
        molecules to draw
    type_:
        image type (default: "png" or "svg")
    out_folder:
        location where images will be saved to
    num_processes:
        number of processes to use

    """
    output_path = pathlib.Path(out_folder).resolve()
    output_path.mkdir(parents=True, exist_ok=True)

    if (num_processes is not None and num_processes <= 1) or len(molecules) < 100:
        for i, m in enumerate(molecules):
            create_image(m, type_, output_path,  str(i))
    else:
        import multiprocessing as mp
        map_ = ((m, type_, output_path, str(i)) for i, m in enumerate(molecules))
        with mp.Pool(processes=num_processes) as pool:
            pool.starmap(create_image, map_)


def create_image(
        molecule: str | Molecule,
        type_: str,
        path: pathlib.Path,
        name: str
):
    fig = draw(molecule)

    if STYLE_TEMPLATE.plotter == "matplotlib" and type_ == "png":
        path = path / f"{name}.png"
        fig.savefig(path, transparent=True)
    elif STYLE_TEMPLATE.plotter == "matplotlib" and type_ == "svg":
        path = path / f"{name}.svg"
        fig.savefig(path, transparent=True, format='svg')
    elif STYLE_TEMPLATE.plotter == "plotly" and type_ == "png":
        path = path / f"{name}.png"
        fig.write_image(path)
    elif STYLE_TEMPLATE.plotter == "plotly" and type_ == "svg":
        path = path / f"{name}.svg"
        fig.write_image(path)
    else:
        raise NotImplementedError("Not implemented yet.")


def draw_grid_png(
        molecules: Sequence[str] | Sequence[Molecule],
        output_path: str | pathlib.Path,
        shape: Sequence[int] | None = None,
        num_processes: int | None = None,
):
    """
    Generates a png for a grid of molecules.

    This method generates png of each molecule separately and combines them at the end.
    This method exists because Matplotlib and Plotly are extremely slow or fail completely when
    generating large png files. So this is a workaround with Pillow (need to be installed).

    Parameters
    ----------
    molecules: Sequence[str | Molecule]
        molecules to draw
        str = SMILES string
    output_path: str | pathlib.Path
        location where image will be saved to
    shape: Sequence[int]
        if len(shape) == 2: it will be interpreted as (number of rows, number of columns)
        Sequence of integers representing the number of molecules in each row
        None = auto-determine
    num_processes:
        number of processes to use
    """
    imgs_path = pathlib.Path("temp_imgs")
    try:
        output_path = pathlib.Path(output_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        draw_multiple_images(molecules, type_="png", out_folder=imgs_path, num_processes=num_processes)

        import chemdraw.utils.png_grid
        chemdraw.utils.png_grid.png_grid(imgs_path, output_path, shape)

    finally:
        # delete temp folder of images
        import shutil
        shutil.rmtree(imgs_path)
