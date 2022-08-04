
import chemdraw


def main():
    smiles = "OC(=O)CCCCC(=O)NCCCCCCN"

    mol = chemdraw.Molecule(smiles)
    drawer = chemdraw.Drawer(mol)
    drawer.config.debug.debug = False
    drawer.config.bond_numbers.show = True

    drawer.molecule.add_parenthesis([0, 15], sub_script="n")

    fig = drawer.draw()
    fig.show()


def main2():
    smiles = "CCCC"

    mol = chemdraw.Molecule(smiles)
    drawer = chemdraw.Drawer(mol)
    drawer.config.debug.debug = False
    drawer.config.bond_numbers.show = True

    drawer.molecule.add_parenthesis([0, 2], sub_script="n")

    fig = drawer.draw()
    fig.show()


if __name__ == "__main__":
    main()
    main2()
