import numpy as np

from chemdraw.objects.molecule import Molecule
from chemdraw.utils.math_points import transform_points

def scale(mol: Molecule, scale_: float) -> Molecule:
    """

    Parameters
    ----------
    mol: Molecule

    scale_ : float, optional
        Uniform scaling factor.
    """
    mol.coordinates = transform_points(mol.coordinates, scale=scale_)
    return mol


def rotate(mol: Molecule, vector: np.ndarray) -> Molecule:
    """

    Parameters
    ----------
    mol: Molecule

    vector : np.ndarray, optional
        Either a rotation matrix (DxD) or a target vector to rotate the x-axis into.
    """
    mol.coordinates = transform_points(mol.coordinates, rotation=vector)
    return mol


def move_center_to(mol: Molecule, center: np.ndarray) -> Molecule:
    """

    Parameters
    ----------
    mol: Molecule

    center : array-like of shape (D,), optional
        New geometric center (translation target).
    """
    mol.coordinates = transform_points(mol.coordinates, center= center)
    return mol


def move(mol: Molecule, offset: np.ndarray) -> Molecule:
    """

    Parameters
    ----------
    mol: Molecule

    offset: np.ndarray shape (D,), optional
        translate points in x,y,z directions.
    """
    mol.coordinates = transform_points(mol.coordinates, move=offset)
    return mol


def mirror(mol: Molecule, axis: int) -> Molecule:
    """

    Parameters
    ----------
    mol: Molecule

    axis: int, optional
        If specified, mirror only across the given axis (0 = x, 1 = y, 2 = z).
        If 3, mirror across the center in all directions (i.e., invert around center).
    """
    mol.coordinates = transform_points(mol.coordinates, mirror=axis)
    return mol