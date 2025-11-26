import chemdraw


def main():
    mol = r"C([C@@H]1[C@H]([C@@H]([C@H]([C@H](O1)O)O)O)O)O"

    molecule = chemdraw.Molecule(mol)
    fig = chemdraw.draw(molecule)
    fig.show()


if __name__ == "__main__":
    main()

