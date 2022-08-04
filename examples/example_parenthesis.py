
import chemdraw


def main():
    bigsmiles = "OC(=O)CCCCC(=O)NCCCCCCN"

    mol = chemdraw.Molecule(bigsmiles)
    drawer = chemdraw.Drawer(mol)
    drawer.config.debug.debug = True
    fig = drawer.draw()
    fig.show()


if __name__ == "__main__":
    main()
