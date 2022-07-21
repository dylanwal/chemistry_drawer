import numpy as np


def findNewCycles(path, cycles, graph):
    start_node = path[0]
    next_node = None
    sub = []

    # visit each edge and each node of each edge
    for edge in graph:
        node1, node2 = edge
        if start_node in edge:
            if node1 == start_node:
                next_node = node2
            else:
                next_node = node1
            if not visited(next_node, path):
                # neighbor node not on path yet
                sub = [next_node]
                sub.extend(path)
                # explore extended path
                findNewCycles(sub, cycles, graph)
            elif len(path) > 2 and next_node == path[-1]:
                # cycle found
                p = rotate_to_smallest(path)
                inv = invert(p)
                if isNew(p, cycles) and isNew(inv, cycles):
                    cycles.append(p)


def invert(path):
    return rotate_to_smallest(path[::-1])


#  rotate cycle path such that it begins with the smallest node
def rotate_to_smallest(path):
    n = path.index(min(path))
    return path[n:] + path[:n]


def isNew(path, cycles):
    return not path in cycles


def visited(node, path):
    return node in path


def get_rings(graph: np.ndarray) -> list[list[int]]:
    cycles = []
    for edge in graph:
        for node in edge:
            findNewCycles([node], cycles, graph)

    return cycles


def main():
    graph = np.array([[1, 2], [1, 3], [1, 4], [2, 3], [3, 4], [2, 6], [4, 6], [8, 7], [8, 9], [9, 7]])

    cycles = get_rings(graph)

    for cy in cycles:
        path = [str(node) for node in cy]
        s = ",".join(path)
        print(s)


if __name__ in "__main__":
    main()
