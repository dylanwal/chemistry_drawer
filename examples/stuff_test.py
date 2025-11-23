
import chemdraw


# mol = chemdraw.Molecule("NC(C)[C@H](C)[C@@H](C)/C=C/C(C#CC)=C")
# mol = chemdraw.Molecule("F[C@](Br)(C)/C=C/C")
# mol = chemdraw.Molecule("c1cc(c(cc1C(F)(F)F)[N+](=O)[O-])NCc2ccsc2")
mol = chemdraw.Molecule("F[C](F)c1ccc(NCC2CCSC2)c([N+]([O-])=O)c1")
fig = chemdraw.draw(mol)
fig.show("browser")
