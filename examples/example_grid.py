
import chemdraw


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
        "N#CCC1(CC(O1)C2=CC(=NC2=O)OC)O"
    ]

    config = chemdraw.Config()
    # config.atoms.method = True

    drawer = chemdraw.GridDrawer(molecules)
    # drawer.draw(auto_open=True)
    drawer.draw_html(auto_open=True)


if __name__ == "__main__":
    main()
