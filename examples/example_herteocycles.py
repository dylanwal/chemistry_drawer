
import chemdraw

mols_dict = {
    "aziridine": "C1CN1",
    "oxirane": "C1CO1",
    "thiirane": "C1CS1",
}

mols = [chemdraw.Molecule(v, label=k) for k, v in mols_dict.items()]
fig = chemdraw.draw_grid(mols)
fig.show()
# fig.savefig('heterocycles.svg', transparent=True, format='svg')