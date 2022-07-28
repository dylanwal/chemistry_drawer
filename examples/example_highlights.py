import chemdraw


def main():
    # mol = "C(C(C#N)NC)C2=CC=C1OCOC1=C2"
    mol = "C1(CCC2)=C3C2=CC4=C5C3=C(CCC5CCC4)C=C1"

    config = chemdraw.DrawerConfig()
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

    fig = drawer.draw()
    fig.write_html("temp.html", auto_open=True)


if __name__ == "__main__":
    main()
