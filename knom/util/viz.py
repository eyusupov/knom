from pygraphviz import AGraph

from knom.typing import Triple
from knom.util import print_triple


def draw_clause_dependencies_graph(
    clause_dependencies: list[tuple[Triple, Triple]],
) -> AGraph:
    dot = AGraph(directed=True)
    for clause1, clause2 in clause_dependencies:
        c1 = print_triple(clause1)
        dot.add_node(c1)
        c2 = print_triple(clause2)
        dot.add_node(c2)
        dot.add_edge(c1, c2)
    return dot
