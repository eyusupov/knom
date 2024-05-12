from rdflib import BNode, Graph, Literal, Namespace, URIRef, Variable
from rdflib.term import Node

from knom.typing import Triple

# TODO(eyusupov): remove
EX = Namespace("http://example.com/")

LOG = Namespace("http://www.w3.org/2000/10/swap/log#")



def node_repr(node: Node | None) -> str:
    if node is None:
        return "_"
    assert isinstance(node, URIRef | Literal | BNode | Variable), node.__class__
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
