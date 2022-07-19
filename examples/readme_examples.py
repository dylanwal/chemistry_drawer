
import chemdraw


def main():
    mol = "O=C(C)Oc1ccccc1C(=O)O"
    mod_drawer = chemdraw.Drawer(mol, title=mol)
    fig = mod_drawer.draw_img(".\\imgs\\example_1.svg")


if __name__ == "__main__":
    main()
