
import chemdraw


def main():
    mol = "C1=CC=CC=C1C"
    mod_drawer = chemdraw.Drawer(mol, title=mol)
    fig = mod_drawer.draw_img(".\\imgs\\example_1.svg")


if __name__ == "__main__":
    main()
