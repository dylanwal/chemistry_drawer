import chemdraw
import rdkit.Chem as Chem

mol_block = '\n     RDKit          2D\n\n  6  5  0  0  0  0  0  0  0  0999 V2000\n    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0\n    1.2990    0.7500    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0\n    2.5981   -0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0\n    3.8971    0.7500    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0\n    5.1962   -0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0\n    6.4952    0.7500    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0\n  1  2  1  0\n  2  3  1  0\n  3  4  1  0\n  4  5  1  0\n  5  6  1  0\nM  END\n'


def main():
    molecules = [
        "CCCCCCCCCC",
        "CC(CC(CCC)C)CC",
        "CCC1CC1",
        "O1CCCCC1C",
        "C1=CC=CC=C1C",
        "O=C(C)Oc1ccccc1C(=O)O",
        "C1(CCC2)=C3C2=CC4=C5C3=C(CCC5CCC4)C=C1",
        "CC(C)(C)N(C)C(=O)C14C3C2C1C5C2C3C45C(=O)C69C8C7C6C%10C7C8C9%10",
        "CC3C(C(=O)OCC1=CCN2C1C(CC2)OC(=O)C(CC(=O)O3)(C(C)C)O)(C(C)C)O",
        "N#CCC1(CC(O1)C2=CC(=NC2=O)OC)O",
        "C1CCCC2=C1CCCC2",
        "CC1=CC=C(C#N)C=C1",
        "c1cccc2c1cccc2",
        mol_block,
        "./mol_files/test_mol1.mol",
        Chem.MolFromSmiles("c1cccc2c1cccc2")
    ]

    mols = []
    for i, m in enumerate(molecules):
        mol = chemdraw.Molecule(m)
        mols.append(mol)
        print(mol)

    fig = chemdraw.draw_grid(mols)
    fig.savefig('my_transparent_plot.svg', transparent=True, format='svg')

if __name__ == '__main__':
    main()
