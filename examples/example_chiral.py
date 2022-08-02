import chemdraw


def main():
    mol = r"C([C@@H]1[C@H]([C@@H]([C@H]([C@H](O1)O)O)O)O)O"

    molecule = chemdraw.Molecule(mol)

    molecule_drawer = chemdraw.Drawer(molecule, title=mol)
    fig = molecule_drawer.draw()
    fig.write_html("temp.html", auto_open=True)


if __name__ == "__main__":
    main()

