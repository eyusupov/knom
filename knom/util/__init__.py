from collections.abc import Iterable
from typing import Any

from rdflib import BNode, Graph, Literal, Namespace, URIRef, Variable
from rdflib.namespace import NamespaceManager
from rdflib.term import Node

from knom.typing import Triple

LOG = Namespace("http://www.w3.org/2000/10/swap/log#")


def only_one(some: Iterable) -> Any:  # noqa: ANN401
    iter_ = iter(some)
    value = next(iter_)
    try:
        next(iter_)
    except StopIteration:
        return value
    raise AssertionError


def node_repr(
    node: Node | None, namespace_manager: NamespaceManager | None = None
) -> str:
    if node is None:
        return "_"
    if isinstance(node, URIRef | Literal | BNode):
        return node.n3(namespace_manager=namespace_manager)
    if isinstance(node, Graph):
        return print_graph(node)
    assert isinstance(node, Variable)
    return node.toPython()


def print_triple(
    triple: Triple, namespace_manager: NamespaceManager | None = None
) -> str:
    if isinstance(triple, Graph):
        return print_graph(triple)
    return ", ".join(
        [node_repr(c, namespace_manager=namespace_manager) for c in triple]
    )


def print_graph(formula: Graph) -> str:
    return (
        "{"
        + ". ".join(
            [
                print_triple(c, namespace_manager=formula.namespace_manager)
                for c in formula
            ]
        )
        + "}"
    )


def print_rule(rule: Triple) -> str:
    s, p, o = rule
    assert isinstance(s, Graph)
    assert isinstance(o, Graph)
    if p == LOG.implies:
        return f"{print_graph(s)} => {print_graph(o)}"
    if p == LOG.impliedBy:
        return f"{print_graph(o)} => {print_graph(s)}"
    raise ValueError
