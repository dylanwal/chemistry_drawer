
import chemdraw

st = chemdraw.STYLE_TEMPLATE.set_style(r"C:\Users\nicep\Desktop\pyth_proj\chemdraw\chemdraw\config\style_templates\acs_1996_matplotlib.yaml")

# mol = chemdraw.Molecule("NC(C)[C@H](C)[C@@H](C)/C=C/C(C#CC)=C")
# mol = chemdraw.Molecule("F[C@](Br)(C)/C=C/C")
# mol = chemdraw.Molecule("c1cc(c(cc1C(F)(F)F)[N+](=O)[O-])NCc2ccsc2")
# mol = chemdraw.Molecule("FC(NC(=O)C)c1ccc(NCB2C(CC#[CH])CSC2)c([N+]([O-])=O)c1")
# mol = "C12=CC=CC=C1C=CC=C2"
# fig = chemdraw.draw(mol)
# fig.show()
# fig.savefig('my_transparent_plot.png', transparent=True)

mols = [
    "NC(C)[C@H](C)[C@@H](C)/C=C/C(C#CC)=C",
    "FC(NC(=O)C)c1ccc(NCB2C(CC#[CH])CSC2)c([N+]([O-])=O)c1",
    "CCCC",
    "C12=CC=CC=C1C=CC=C2",
    "CNCCCOCCN"
]
fig = chemdraw.draw_grid(mols)
fig.show()
# fig.savefig('my_transparent_plot.svg', transparent=True, format='svg')
