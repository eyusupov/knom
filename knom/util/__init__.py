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
    assert isinstance(s, Graph)
    assert isinstance(o, Graph)
    if p == LOG.implies:
        return f"{print_graph(s)} => {print_graph(o)}."
    if p == LOG.impliedBy:
        return f"{print_graph(o)} => {print_graph(s)}."
    raise ValueError


def bnode_key(triple: Triple) -> tuple[Node]:
    return tuple(n for n in triple if not isinstance(n, BNode))


def compact_bnodes(g: Graph, head: set[Triple]) -> set[Triple]:
    # TODO: think if we need it. Probably it is useless in a normal program.
    # After removing some clauses, non-negative head might contain pathological case
    # To avoid this, we try to compact the blank nodes
    # Maybe it's also worth doing it in the general case.

    bnode_masks = {}
    for triple in head:
        for node in triple:
            if isinstance(node, BNode):
                if node not in bnode_masks:
                    bnode_masks[node] = set()
                bnode_masks[node].add(bnode_key(triple))

    bnode_idx = {}
    for node, mask in bnode_masks.items():
        key = frozenset(mask)
        if key not in bnode_idx:
            bnode_idx[key] = set()
        bnode_idx[key].add(node)

    new_bnodes = {}
    for nodes in bnode_idx.values():
        bnode = BNode()
        for node in nodes:
            new_bnodes[node] = bnode

    compacted_head = QuotedGraph(store=g.store, identifier=BNode())
    for triple in head:
        compacted_triple = tuple(new_bnodes.get(node, node) for node in triple)
        compacted_head.add(compacted_triple)

    print("compacted from", len(head), "to", len(compacted_head))
    return compacted_head


def split_rules_and_facts(graph: Graph) -> tuple[Graph, Graph]:
    rules = Graph(namespace_manager=graph.namespace_manager)
    facts = Graph(namespace_manager=graph.namespace_manager)
    for s, p, o in graph:
        if p in [LOG.implies, LOG.impliedBy]:
            rules.add((s, p, o))
        else:
            facts.add((s, p, o))
    return (rules, facts)
