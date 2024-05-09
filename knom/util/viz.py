from pygraphviz import AGraph
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.term import Node

from knom import LOG, Triple
from knom.stratified import Dependencies

# TODO(eyusupov): remove
EX = Namespace("http://example.com/")


def node_repr(node: Node) -> str:
    assert isinstance(node, URIRef | Literal | BNode)
    return node.toPython().replace(EX, ":")


def print_triple(triple: Triple) -> str:
    return ", ".join([node_repr(c) for c in triple])


def print_formula(formula: Graph) -> str:
    return "{" + ". ".join([print_triple(c) for c in formula]) + "}"


def print_rule(rule: Triple) -> str:
    head, implies, body = rule
    assert implies == LOG.implies
    assert isinstance(head, Graph)
    assert isinstance(body, Graph)
    return f"{print_formula(head)} => {print_formula(body)}"


def draw_clause_dependencies_graph(clause_dependencies: Dependencies) -> AGraph:
    dot = AGraph(directed=True)
    for clause1, clause2 in clause_dependencies:
        c1 = print_triple(clause1)
        dot.add_node(c1)
        c2 = print_triple(clause2)
        dot.add_node(c2)
        dot.add_edge(c1, c2)
    return dot
