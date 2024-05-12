from collections.abc import Iterable, Iterator, Sequence
from typing import cast

from rdflib import BNode, Graph, Literal, URIRef, Variable
from rdflib.term import Node

from knom.typing import Bindings, Mask, Triple
from knom.util import LOG


def bind_node(head_node: Node, fact_node: Node, bindings: Bindings) -> Iterator[Bindings | None]:
    if isinstance(fact_node, Variable):
        return # TODO: this is what eye does. should we?
    if isinstance(head_node, URIRef | Literal):
        if head_node != fact_node:
            yield None
    elif isinstance(head_node, BNode | Variable):
        if bindings.get(head_node, fact_node) != fact_node:
            return
        new_bindings = bindings.copy()
        new_bindings[head_node] = fact_node
        yield new_bindings
    elif isinstance(head_node, Graph):
        if not isinstance(fact_node, Graph):
            return
        yield from match(list(head_node), fact_node, bindings)
    else:
        raise TypeError


def bind(head_clause: Triple, fact: Triple, bindings: Bindings) -> Iterator[Bindings | None]:
    for var, val in zip(head_clause, fact, strict=True):
        yield from bind_node(var, val, bindings)


def assign_node(node: Node, bindings: Bindings) -> Node:
    if isinstance(node, Variable | BNode):
        return bindings.get(node, BNode())
    if isinstance(node, Graph):
        g = Graph()
        for triple in node:
            g.add(assign(triple, bindings))
        return g
    return node


def assign(triple: Triple, bindings: Bindings) -> Triple:
    return (
        assign_node(triple[0], bindings),
        assign_node(triple[1], bindings),
        assign_node(triple[2], bindings),
    )


def get_node_mask(node: Node, bindings: Bindings) -> Node | None:
    if isinstance(node, Variable | BNode):
        return bindings.get(node, None)
    assert isinstance(node, URIRef | Literal | Graph)
    return node


def mask(head_clause: Triple, bindings: Bindings) -> Mask:
    return (
        get_node_mask(head_clause[0], bindings),
        get_node_mask(head_clause[1], bindings),
        get_node_mask(head_clause[2], bindings),
    )


def match(
    head: Sequence[Triple],
    facts: Graph,
    bindings: Bindings
) -> Iterator[Bindings]:
    for head_clause in head:
        mask_ = mask(head_clause, bindings)
        for fact in facts.triples(mask_):
            new_bindings : Bindings | None = bindings.copy()
            for new_binding in bind(head_clause, fact, cast(Bindings, new_bindings)):
                if new_binding is None:
                    new_bindings = None
                    break
                cast(Bindings, new_bindings).update(new_binding)
            if new_bindings is not None:
                yield new_bindings


def single_pass(facts: Graph, rules: Iterable[Triple]) -> Iterator[Triple]:
    for head, implies, body in rules:
        assert isinstance(head, Graph)
        assert implies == LOG.implies
        assert isinstance(body, Graph)
        for bindings in match(list(head), facts, {}):
            for triple in body:
                yield assign(triple, bindings)


def naive_fixpoint(facts: Graph, rules: Graph) -> Graph:
    inferred = Graph(namespace_manager=facts.namespace_manager)
    feed = facts
    while True:
        new_feed = Graph()
        old_inferred = len(inferred)
        for new_tuple in single_pass(feed, rules):
            inferred.add(new_tuple)
            new_feed.add(new_tuple)
        if len(inferred) == old_inferred:
            break
        feed = new_feed
    return inferred
