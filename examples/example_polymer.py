
import chemdraw


def main():
    bigsmiles = "O{[>][<]C(=O)CCCCC(=O)NCCCCCCN[>][<]}"

    poly = chemdraw.Polymer(bigsmiles)
    drawer = chemdraw.Drawer(poly)
    fig = drawer.draw()
    fig.show()


if __name__ == "__main__":
    main()
