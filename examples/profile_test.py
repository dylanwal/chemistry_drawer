
import chemdraw

mols = [
    "NC(C)[C@H](C)[C@@H](C)/C=C/C(C#CC)=C",
    "FC(NC(=O)C)c1ccc(NCB2C(CC#[CH])CSC2)c([N+]([O-])=O)c1",
    "CCCC",
    "C12=CC=CC=C1C=CC=C2",
    "CNCCCOCCN",
    "C1CCCC2=C1CCCC2",
    "CC1=CC=C(C#N)C=C1",
] *20
mols = [chemdraw.Molecule(m) for m in mols]
fig = chemdraw.draw_grid(mols)
# fig.show()
fig.savefig('my_transparent_plot.svg', transparent=True, format='svg')
# fig.savefig('my_transparent_plot.png', transparent=True)
