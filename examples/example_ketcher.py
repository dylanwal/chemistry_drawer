import chemdraw


def main():
    mole_file_name = "ketcher_mol_file.txt"
    mol = chemdraw.Molecule(mole_file=mole_file_name)

    molecule_drawer = chemdraw.Drawer(mol)
    fig = molecule_drawer.draw()
    fig.write_html("temp.html", auto_open=True)


if __name__ == "__main__":
    main()
