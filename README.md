# ChemDraw

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
    "O1CCCCC1C",
    "C1=CC=CC=C1C",
    "O=C(C)Oc1ccccc1C(=O)O",
    "CN1CCC23C4C1CC5=C2C(=C(C=C5)O)OC3C(C=C4)O",
    "CC(C)(C)N(C)C(=O)C14C3C2C1C5C2C3C45C(=O)C69C8C7C6C%10C7C8C9%10",
    "CC3C(C(=O)OCC1=CCN2C1C(CC2)OC(=O)C(CC(=O)O3)(C(C)C)O)(C(C)C)O",
    "CCCC1(CC(O1)C2=CC(=NC2=O)OC)O"
]

drawer = chemdraw.GridDrawer(molecules)
drawer.draw_png("example_2")
```

![grid example](./examples/imgs/grid.png)

---

## Atom and Bond Numbers

Atom Numbers (black text) 

Bond Numbers (gray text)

Ring Numbers (maroon text)

```python
import chemdraw

mol = "C1(CCC2)=C3C2=CC4=C5C3=C(CCC5CCC4)C=C1"

config = chemdraw.DrawerConfig()
config.atom_numbers.show = True
config.bond_numbers.show = True

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

config = chemdraw.DrawerConfig()
config.ring_highlights.show = True

molecule = chemdraw.Molecule(mol)
for ring in molecule.rings:
    ring.highlight = True  # all rings are highlighted (with default color)
    if ring.aromatic:  #  highlighted aromatic green
        ring.color = "rgba(0,255,0,0.5)"

drawer = chemdraw.Drawer(molecule, title=mol, config=config)
fig = drawer.draw()
fig.show()

```

![ring highlights](./examples/imgs/ring_highlights.svg)


---
## Atom and Bond Highlights

```python
import chemdraw

mol = "C1(CCC2)=C3C2=CC4=C5C3=C(CCC5CCC4)C=C1"

config = chemdraw.DrawerConfig()
config.ring_highlights.show = True

molecule = chemdraw.Molecule(mol)
bonds = 
for ring in molecule.rings:
    ring.highlight = True  # all rings are highlighted (with default color)
    if ring.aromatic:  #  highlighted aromatic green
        ring.color = "rgba(0,255,0,0.5)"

drawer = chemdraw.Drawer(molecule, title=mol, config=config)
fig = drawer.draw()
fig.show()

```

![ring highlights](./examples/imgs/ring_highlights.svg)


