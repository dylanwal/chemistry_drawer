
import chemdraw


def simple():
    mol = "O=C(C)Oc1ccccc1C(=O)O"
    drawer = chemdraw.Drawer(mol, title=mol)
    drawer.draw_img(".\\imgs\\simple.svg")


def grid():
    molecules = [
        "CCCCCCCCCC",
        "CC(CC(CCC)C)CC",
        "CCC1CC1",
        "C1=CC=CC=C1C",
        "C([C@@H]1[C@H]([C@@H]([C@H]([C@H](O1)O)O)O)O)O",
        "O=C(C)Oc1ccccc1C(=O)O",
        "C1(CCC2)=C3C2=CC4=C5C3=C(CCC5CCC4)C=C1",
        "CC(C)(C)N(C)C(=O)C14C3C2C1C5C2C3C45C(=O)C69C8C7C6C%10C7C8C9%10",
        "CC3C(C(=O)OCC1=CCN2C1C(CC2)OC(=O)C(CC(=O)O3)(C(C)C)O)(C(C)C)O",
        "N#CCC1(CC(O1)C2=CC(=NC2=O)OC)O"
    ]

    drawer = chemdraw.GridDrawer(molecules)
    drawer.draw_png(".\\imgs\\grid.png")


def atom_bond_numbers():
    mol = "C1(CCC2)=C3C2=CC4=C5C3=C(CCC5CCC4)C=C1"

    config = chemdraw.ConfigDrawer()
    config.atom_numbers.show = True
    config.bond_numbers.show = True
    config.ring_numbers.show = True

    drawer = chemdraw.Drawer(mol, title=mol, config=config)
    drawer.draw_img(".\\imgs\\atom_bond_numbers.svg")


def ring_highlights():
    mol = "C1(CCC2)=C3C2=CC4=C5C3=C(CCC5CCC4)C=C1"

    config = chemdraw.ConfigDrawer()
    config.ring_highlights.show = True

    molecule = chemdraw.Molecule(mol)
    for ring in molecule.rings:
        ring.highlight = True  # all rings are highlighted (with default highlight_color)
        if ring.aromatic:  # aromatic are green highlighted
            ring.highlight_color = "rgba(0,255,0,0.5)"

    drawer = chemdraw.Drawer(molecule, title=mol, config=config)
    drawer.draw_img(".\\imgs\\ring_highlights.svg")


def atom_bond_highlights():
    mol = "C1(CCC2)=C3C2=CC4=C5C3=C(CCC5CCC4)C=C1"

    config = chemdraw.ConfigDrawer()
    config.highlights.show = True

    molecule = chemdraw.Molecule(mol)
    bond_ids = [0, 1,  2, 19, 5, 6, 21, 15, 14, 13, 12, 11, 10, 16, 17, 18]
    for id_ in bond_ids:
        molecule.bonds[id_].highlight = True

    for atom in molecule.atoms:
        atom.highlight = True

    accent_color = "rgb(252,186,63)"
    molecule.bonds[8].highlight = True
    molecule.bonds[8].highlight_color = accent_color
    molecule.bonds[20].highlight = True
    molecule.bonds[20].highlight_color = accent_color
    atoms_ids = [4, 8, 9]
    for id_ in atoms_ids:
        molecule.atoms[id_].highlight_color = accent_color

    drawer = chemdraw.Drawer(molecule, title=mol, config=config)
    drawer.draw_img(".\\imgs\\highlights.svg")


if __name__ == "__main__":
    simple()
    grid()
    atom_bond_numbers()
    ring_highlights()
    atom_bond_highlights()
