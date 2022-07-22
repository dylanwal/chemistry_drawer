import chemdraw


def main():
    mol = "CN1CCC23C4C1CC5=C2C(=C(C=C5)O)OC3C(C=C4)O"
    # mol = "C1(CCC2)=C3C2=CC4=C5C3=C(CCC5CCC4)C=C1"

    config = chemdraw.DrawerConfig()
    config.atom_numbers.show = True
    molecule_drawer = chemdraw.Drawer(mol, title=mol, config=config)
    fig = molecule_drawer.draw()
    fig.write_html("temp.html", auto_open=True)


if __name__ == "__main__":
    main()
