from rdflib import BNode, Graph, Literal, Namespace, URIRef, Variable
from rdflib.namespace import NamespaceManager
from rdflib.term import Node

from knom.typing import Triple

LOG = Namespace("http://www.w3.org/2000/10/swap/log#")



def node_repr(node: Node | None, namespace_manager: NamespaceManager | None = None) -> str:
    if node is None:
        return "_"
    if isinstance(node, URIRef | Literal | BNode):
        return node.n3(namespace_manager=namespace_manager)
    assert isinstance(node, Variable)
    return node.toPython()


def print_triple(triple: Triple, namespace_manager: NamespaceManager | None = None) -> str:
    return ", ".join([node_repr(c, namespace_manager=namespace_manager) for c in triple])


def print_graph(formula: Graph) -> str:
    return "{" + ". ".join([print_triple(c, namespace_manager=formula.namespace_manager) for c in formula]) + "}"


def print_rule(rule: Triple) -> str:
    head, implies, body = rule
    assert implies == LOG.implies
    assert isinstance(head, Graph)
    assert isinstance(body, Graph)
    return f"{print_graph(head)} => {print_graph(body)}"
