import chemdraw


def main():
    mole_file_name = "mol_files/poly_diblock.txt"
    mol = chemdraw.Molecule(mole_file=mole_file_name)

    drawer = chemdraw.Drawer(mol)
    fig = drawer.draw()
    fig.write_html("temp.html", auto_open=True)


def grid():
    import glob
    molecules = [chemdraw.Molecule(mole_file=file) for file in glob.glob("mol_files\\*.txt")]
    drawer = chemdraw.GridDrawer(molecules)
    drawer.draw_html(auto_open=True)


if __name__ == "__main__":
    # single()
    grid()
