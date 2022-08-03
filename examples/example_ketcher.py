import chemdraw


def main():
    mole_file_name = "ketcher_mol_file.txt"
    mol = chemdraw.Molecule(mole_file=mole_file_name)

    config = chemdraw.Config()
    config.debug.debug = False
    config.layout.fix_zoom = False

    molecule_drawer = chemdraw.Drawer(mol, config=config)
    fig = molecule_drawer.draw()
    fig.write_html("temp.html", auto_open=True)


if __name__ == "__main__":
    main()
