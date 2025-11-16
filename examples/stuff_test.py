
import chemdraw


mol = chemdraw.Molecule("CC(C)[C@H](C)[C@@H](C)/C=C/C(C#CC)=C")
# mol = chemdraw.Molecule("F[C@](Br)(C)/C=C/C")
fig = chemdraw.draw(mol)
fig.show("browser")
