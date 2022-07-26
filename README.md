# Chemistry Drawer

---

![PyPI](https://img.shields.io/pypi/v/chemdraw)
![downloads](https://static.pepy.tech/badge/chemdraw)
![license](https://img.shields.io/github/license/dylanwal/chemdraw)

Draw molecules with [Plotly](https://github.com/plotly/plotly.py).

**Make molecules look the way you want it!**

The package provides global control of aesthetics with `config`, and allows for local control by specifying details 
for every atom, bond, and ring.


(Development still in progress. So there are some bugs. But its working pretty well so far!)

---

## Installation

Pip installable package available.

`pip install chemdraw`

[pypi: chemdraw](https://pypi.org/project/chemdraw/)

---
---

## Dependencies

* [numpy](https://github.com/numpy/numpy) (1.23.1)
  * Used for math
* [plotly](https://github.com/plotly/plotly.py) (5.9.0)
  * Plots molecules
* [kaleido](https://github.com/plotly/Kaleido)  (0.1.0post1)
  * Converts plotly graphs to images (png, svg, etc.)
  * I am not using the most recent version of kaleido as it does not play nice with my computer. Try the newest 
    version, but if you are having issues install this specific version. 
* [rdkit](https://github.com/rdkit/rdkit) (2022.3.4)
  * Convert SMILES to position coordinates.
* [Pillow](https://github.com/python-pillow/Pillow) (9.2.0)
  * Used for image manipulation.
* [scikit-learn](https://github.com/scikit-learn/scikit-learn) (1.1.1)
  * Used to reorient molecules.

---
---

# Examples:
(Image may be distorted from viewer, but real image is not.)


## Basic Usage
```python
import chemdraw

mol = "O=C(C)Oc1ccccc1C(=O)O"
drawer = chemdraw.Drawer(mol, title=mol)
fig = drawer.draw()
fig.show()
```

![simple example](./examples/imgs/simple.svg)

---
## Grid


```python
import chemdraw

molecules = [
    "CCCCCCCCCC",
    "CC(CC(CCC)C)CC",
    "CCC1CC1",
    "C([C@@H]1[C@H]([C@@H]([C@H]([C@H](O1)O)O)O)O)O",
    "O=C(C)Oc1ccccc1C(=O)O",
    "C1(CCC2)=C3C2=CC4=C5C3=C(CCC5CCC4)C=C1",
    "CC(C)(C)N(C)C(=O)C14C3C2C1C5C2C3C45C(=O)C69C8C7C6C%10C7C8C9%10",
    "CC3C(C(=O)OCC1=CCN2C1C(CC2)OC(=O)C(CC(=O)O3)(C(C)C)O)(C(C)C)O",
    "N#CCC1(CC(O1)C2=CC(=NC2=O)OC)O"
]

drawer = chemdraw.GridDrawer(molecules)
drawer.draw_png("example_2.png")
```

![grid example](./examples/imgs/grid.png)

---

## Atom, Bond, and Ring Numbers

Atom Numbers (black text) 

Bond Numbers (gray text)

Ring Numbers (maroon text)

```python
import chemdraw

mol = "C1(CCC2)=C3C2=CC4=C5C3=C(CCC5CCC4)C=C1"

config = chemdraw.Config()
config.atom_numbers.show = True
config.bond_numbers.show = True
config.ring_numbers.show = True

drawer = chemdraw.Drawer(mol, title=mol, config=config)
fig = drawer.draw()
fig.show()

```


![atom bond example](./examples/imgs/atom_bond_numbers.svg)


---

## Ring Highlights

```python
import chemdraw

mol = "C1(CCC2)=C3C2=CC4=C5C3=C(CCC5CCC4)C=C1"

molecule = chemdraw.Molecule(mol)
for ring in molecule.rings:
  ring.highlight.show = True  # all rings are highlighted (with default highlight_color)
  if ring.aromatic:  # highlighted aromatic green
    ring.highlight.color = "rgba(0,255,0,0.5)"

drawer = chemdraw.Drawer(molecule, title=mol)
fig = drawer.draw()
fig.show()

```

![ring highlights](./examples/imgs/ring_highlights.svg)


---
## Atom and Bond Highlights

```python
import chemdraw

mol = "C1(CCC2)=C3C2=CC4=C5C3=C(CCC5CCC4)C=C1"

molecule = chemdraw.Molecule(mol)

# highlight outer ring bonds and atoms
bond_ids = [0, 1, 2, 19, 5, 6, 21, 15, 14, 13, 12, 11, 10, 16, 17, 18]
for id_ in bond_ids:
  molecule.bonds[id_].highlight.show = True
for atom in molecule.atoms:
  atom.highlight.show = True

# highlight inner bonds and atoms
accent_color = "rgb(252,186,63)"
molecule.bonds[8].highlight.show = True
molecule.bonds[8].highlight.color = accent_color
molecule.bonds[20].highlight.show = True
molecule.bonds[20].highlight.color = accent_color
atoms_ids = [4, 8, 9]
for id_ in atoms_ids:
  molecule.atoms[id_].highlight.color = accent_color

drawer = chemdraw.Drawer(molecule, title=mol)
fig = drawer.draw()
fig.show()
```

![ring highlights](./examples/imgs/highlights.svg)

---
## Polymers

From mole file
```python
import chemdraw

mole_file_name = "ketcher_mol_file.txt"
mol = chemdraw.Molecule(mole_file=mole_file_name)

drawer = chemdraw.Drawer(mol)
fig = drawer.draw()
fig.show()
```

![polymer](./examples/imgs/polymer.svg)


Add parenthesis to a SMILES

```python
import chemdraw

mol = chemdraw.Molecule("OC(=O)CCCCC(=O)NCCCCCCN")
mol.add_parenthesis([0, 15], sub_script="n")

drawer = chemdraw.Drawer(mol)
fig = drawer.draw()
fig.show()
```

![polymer2](./examples/imgs/polymer2.svg)

---
---

# Mole Files

You can also pass a file path to mole files into 'Molecule'. 
Support for V2000 only.

```python
import chemdraw

mole_file_name = "examples/mol_files/poly_diblock.txt"
mol = chemdraw.Molecule(mole_file=mole_file_name)

molecule_drawer = chemdraw.Drawer(mol)
fig = molecule_drawer.draw()
fig.show()
```


# More Info

For more information on how the code works see: 
[chemdraw.README.md](https://github.com/dylanwal/chemdraw/tree/master/chemdraw) 
