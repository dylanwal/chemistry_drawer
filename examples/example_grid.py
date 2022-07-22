
import chemdraw


def main():
    molecules = [
        "CCCCCCCCCC",
        "CC(CC(CCC)C)CC",
        "CCC1CC1",
        "O1CCCCC1C",
        "C1=CC=CC=C1C",
        "O=C(C)Oc1ccccc1C(=O)O",
        "CN1CCC23C4C1CC5=C2C(=C(C=C5)O)OC3C(C=C4)O",
        "CC(C)(C)N(C)C(=O)C14C3C2C1C5C2C3C45C(=O)C69C8C7C6C%10C7C8C9%10",
        "CC3C(C(=O)OCC1=CCN2C1C(CC2)OC(=O)C(CC(=O)O3)(C(C)C)O)(C(C)C)O",
        "CCCC1(CC(O1)C2=CC(=NC2=O)OC)O"
    ]

    config = chemdraw.DrawerConfig()
    config.atoms.method = True

    drawer = chemdraw.GridDrawer(molecules)
    drawer.draw_html(auto_open=True)


if __name__ == "__main__":
    main()
