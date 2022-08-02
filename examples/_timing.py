import chemdraw


def main():
    mol = "CC12CCC%11C(C1CCC2O[Si](C)(OC3CCC4C3(CCC5C4CCC6=CC(=O)CCC56C)C)OC7CCC8C7(CCC9C8CCC%10=CC(=O)CCC9%10C)C)CCC%12=CC(=O)CCC%11%12C"
    # mol = "C(C(C#N)NC)C2=CC=C1OCOC1=C2"
    #

    config = chemdraw.ConfigDrawer()
    config.layout.fixed_domain = True
    config.title.show = True
    config.layout.show_axis =True

    molecule_drawer = chemdraw.Drawer(mol, title=mol, config=config)
    fig = molecule_drawer.draw()
    fig.show()

    mol = "CCCC1(CC(O1)C2=CC(=NC2=O)OC)O"
    molecule_drawer = chemdraw.Drawer(mol, title=mol, config=config)
    fig = molecule_drawer.draw()
    fig.show()

    # fig.write_html("temp.html", auto_open=True)


def main_profile():
    import cProfile
    mol = "CC12CCC%11C(C1CCC2O[Si](C)(OC3CCC4C3(CCC5C4CCC6=CC(=O)CCC56C)C)OC7CCC8C7(CCC9C8CCC%10=CC(=O)CCC9%10C)C)CCC%12=CC(=O)CCC%11%12C"
    # mol = "C(C(C#N)NC)C2=CC=C1OCOC1=C2"
    
    with cProfile.Profile() as pr:
        molecule_drawer = chemdraw.Drawer(mol, title=mol)
        fig = molecule_drawer.draw()
        
    pr.print_stats(sort="cumtime")
    # fig.write_html("temp.html", auto_open=True)


def main_time():
    import time
    mol = "CC12CCC%11C(C1CCC2O[Si](C)(OC3CCC4C3(CCC5C4CCC6=CC(=O)CCC56C)C)OC7CCC8C7(CCC9C8CCC%10=CC(=O)CCC9%10C)C)CCC%12=CC(=O)CCC%11%12C"
    # mol = "C(C(C#N)NC)C2=CC=C1OCOC1=C2"

    start = time.time()
    molecule_drawer = chemdraw.Drawer(mol, title=mol)
    stop = time.time()
    print("parsing:", stop-start)

    start = time.time()
    fig = molecule_drawer.draw()
    stop = time.time()
    print("drawing", stop - start)

    start = time.time()
    fig.write_html("temp.html", auto_open=True)
    stop = time.time()
    print("rendering", stop - start)


def main_grid():
    molecules = [
        "CCCCCCCCCC",
        "CC(CC(CCC)C)CC",
        "CCC1CC1",
        "O1CCCCC1C",
        "C1CCC(F)C1",
        "C1=CC=CC=C1C",
        "C(C(C)NC)C2=CC=C1OCOC1=C2",
        "CC(C)(C)N(C)C(=O)C14C3C2C1C5C2C3C45C(=O)C69C8C7C6C%10C7C8C9%10",
        "CC3C(C(=O)OCC1=CCN2C1C(CC2)OC(=O)C(CC(=O)O3)(C(C)C)O)(C(C)C)O",
        "CCCC1(CC(O1)C2=CC(=NC2=O)OC)O"
    ]

    drawer = chemdraw.GridDrawer(molecules)
    drawer.draw_png()


if __name__ == "__main__":
    # main()
    main_time()
    # main_profile()
    # main_grid()
