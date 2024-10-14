from collections.abc import Iterable
from typing import Any

from rdflib import BNode, Graph, Literal, Namespace, URIRef, Variable
from rdflib.namespace import NamespaceManager
from rdflib.term import Node

from knom.typing import Triple

LOG = Namespace("http://www.w3.org/2000/10/swap/log#")


def get_head(rule: Triple) -> Variable | BNode | Graph:
    s, p, o = rule
    if p == LOG.implies:
        head = s
    elif p == LOG.impliedBy:
        head = o
    else:
        raise AssertionError
    assert isinstance(head, Variable | BNode | Graph)
    return head


def get_body(rule: Triple) -> Variable | Graph:
    s, p, o = rule
    if p == LOG.implies:
        body_ = o
    elif p == LOG.impliedBy:
        body_ = s
    else:
        raise AssertionError
    assert isinstance(body_, Variable | Graph)
    return body_


def only_one(some: Iterable) -> Any:  # noqa: ANN401
    iter_ = iter(some)
    value = next(iter_)
    try:
        next(iter_)
    except StopIteration:
        return value
    raise AssertionError


bnode_names: dict[BNode, str] = {}
cur_bnode_name = "a"

def bnode_name(bnode: BNode) -> str:
    global bnode_names, cur_bnode_name
    if bnode not in bnode_names:
        bnode_names[bnode] = cur_bnode_name
        last_bnode_char = chr(ord(cur_bnode_name[-1]) + 1)
        if last_bnode_char > "z":
            last_bnode_char = "aa"
        cur_bnode_name = cur_bnode_name[:-1] + last_bnode_char
    return bnode_names[bnode]


def add_triples(g: Graph, triples: Iterable[Triple]) -> Graph:
    for triple in triples:
        g.add(triple)
    return g


def node_repr(
    node: Node | None, namespace_manager: NamespaceManager | None = None
) -> str:
    if node is None:
        return "_"
    if isinstance(node, BNode):
        return f"_:{bnode_name(node)}"
    if isinstance(node, URIRef | Literal):
        return node.n3(namespace_manager=namespace_manager)
    if isinstance(node, Graph):
        return print_graph(node)
    assert isinstance(node, Variable), node
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
        "{\n  "
        + ".\n  ".join(
            [
                print_triple(c, namespace_manager=formula.namespace_manager)
                for c in formula
            ]
        )
        + "\n}"
    )


def print_rule(rule: Triple) -> str:
    s, p, o = rule

    subj = print_triple(s) if isinstance(s, Graph) else node_repr(s)
    obj = print_triple(o) if isinstance(o, Graph) else node_repr(s)

    if p == LOG.implies:
        return f"{subj} => {obj}"
    if p == LOG.impliedBy:
        return f"{subj} <= {obj}"
    raise ValueError


def split_rules_and_facts(graph: Graph) -> tuple[Graph, Graph]:
    rules = Graph(namespace_manager=graph.namespace_manager)
    facts = Graph(namespace_manager=graph.namespace_manager)
    for s, p, o in graph:
        if p in [LOG.implies, LOG.impliedBy]:
            rules.add((s, p, o))
        else:
            facts.add((s, p, o))
    return (rules, facts)
