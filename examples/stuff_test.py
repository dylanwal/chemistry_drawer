import time

import chemdraw

chemdraw.STYLE_TEMPLATE.set_style(r"C:\Users\nicep\Desktop\pyth_proj\chemdraw\chemdraw\config\style_templates\acs_1996_matplotlib.yaml")

# mol = "C12=CC=CC=C1C=CC=C2"
# mol = chemdraw.Molecule("NC(C)[C@H](C)[C@@H](C)/C=C/C(C#CC)=C")
# mol = chemdraw.Molecule("F[C@](Br)(C)/C=C/C")
# mol = chemdraw.Molecule("c1cc(c(cc1C(F)(F)F)[N+](=O)[O-])NCc2ccsc2")
# mol = chemdraw.Molecule("FC(NC(=O)C)c1ccc(NCB2C(CC#[CH])CSC2)c([N+]([O-])=O)c1")
#
# fig = chemdraw.draw(mol)
# fig.show()
# fig.savefig('my_transparent_plot.png', transparent=True)




mols = [
    "NC(C)[C@H](C)[C@@H](C)/C=C/C(C#CC)=C",
    "FC(NC(=O)C)c1ccc(NCB2C(CC#[CH])CSC2)c([N+]([O-])=O)c1",
    "CCCC",
    "C12=CC=CC=C1C=CC=C2",
    "CNCCCOCCN"
] *50
start = time.perf_counter()
mols = [chemdraw.Molecule(m) for m in mols]
early = time.perf_counter()
fig = chemdraw.draw_grid(mols)
mid = time.perf_counter()
# fig.show()
fig.savefig('my_transparent_plot.svg', transparent=True, format='svg')
# fig.savefig('my_transparent_plot.png', transparent=True)
end = time.perf_counter()
print("times", early-start, mid-start, end-start)



# import polars as pl
#
# loc = r"C:\Users\nicep\Desktop\pyth_proj\Wisc_ML\wisc_ML\chlorination2\data\SMILES_lib_filtered\combined_filter_1.csv"
# df = pl.read_csv(loc)
# start = time.perf_counter()
# fig = chemdraw.draw_grid(df["SMILES"].to_list()[:1000])
# fig.savefig('my_transparent_plot.svg', transparent=True, format='svg')
# end = time.perf_counter()
# print("times", end-start)