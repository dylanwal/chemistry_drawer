import chemdraw


def main():
    # mol = "C(C(C#N)NC)C2=CC=C1OCOC1=C2"
    mol = "C1=CC=CC=C1C"

    config = chemdraw.DrawerConfig()
    molecule_drawer = chemdraw.Drawer(mol, title=mol, config=config)

    for i in range(5):
        molecule_drawer.molecule.atoms[i].highlight = True

    fig = molecule_drawer.draw()
    fig.write_html("temp.html", auto_open=True)


if __name__ == "__main__":
    main()
