import numpy as np

from chemdraw.objects.atoms import Atom
from chemdraw.objects.bonds import Bond


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

#####################################################################################################################


def _depth_first_search_recursion(node_index: int, node_visited: list[bool], graph: dict[int, list[int]]):
    for next_node_index in graph[node_index]:
        if not node_visited[next_node_index]:
            node_visited[node_index] = True
            _depth_first_search_recursion(next_node_index, node_visited, graph)


def depth_first_search(graph: dict[int, list[int]]):
    node_visited = [False] * len(graph)

    for node_index in range(len(graph)):
        if not node_visited[node_index]:
            node_visited[node_index] = True
            _depth_first_search_recursion(node_index, node_visited, graph)


def _depth_first_search_recursion_atoms(current_atom: Atom, node_visited: dict[int, bool], counter: int):
    counter -= 1
    if counter == 0:
        return

    for bond in current_atom.bonds:
        if bond.atoms[0].id_ == current_atom.id_:
            atom = bond.atoms[1]
        else:
            atom = bond.atoms[0]

        if not atom.id_ not in node_visited:
            node_visited[atom.id_] = True
            stop_flag = _depth_first_search_recursion(atom, node_visited, limit)


class GraphDepth:
    def __init__(self, start_atom: Atom, depth_limit: int = 10, branch_limit: int = 5):
        self.depth_limit = depth_limit
        self.branch_limit = branch_limit
        self.visited_atoms = set()
        self.next_branch_atom = None
        self.start_atom = start_atom

    def depth_first_search_atoms(bond: Bond):
        graph = GraphDepth(start_atom=bond.atoms[0].id_)
        _depth_first_search_recursion_atoms(graph)



def main():
    graph = np.array([[1, 2], [1, 3], [1, 4], [2, 3], [3, 4], [2, 6], [4, 6], [8, 7], [8, 9], [9, 7]])

    cycles = get_rings(graph)

    for cy in cycles:
        path = [str(node) for node in cy]
        s = ",".join(path)
        print(s)


if __name__ in "__main__":
    main()
