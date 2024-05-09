from rdflib import BNode, Graph, Variable
from rdflib.term import Node


def is_var(node: Node) -> bool:
    return isinstance(node, Variable)


def is_bnode(node: Node) -> bool:
    return isinstance(node, BNode)


def is_graph(node: Node) -> bool:
    return isinstance(node, Graph)
