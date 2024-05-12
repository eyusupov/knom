from collections.abc import Iterable, Iterator, Sequence
from typing import cast

from rdflib import BNode, Graph, Literal, URIRef, Variable
from rdflib.term import Node

from knom.typing import Bindings, Mask, Triple
from knom.util import LOG

import json
def bind_node(
    head_node: Node, fact_node: Node, bindings: Bindings
) -> Iterator[Bindings | None]:
    print("bind node: ", head_node.n3(), "->", fact_node.n3(), json.dumps(bindings))
    if isinstance(fact_node, Variable):
        yield None # This is what eye does. should we?
    elif isinstance(head_node, URIRef | Literal):
        if head_node != fact_node:
            print("conflict")
            yield None
        yield bindings
    elif isinstance(head_node, BNode | Variable):
        if bindings.get(head_node, fact_node) != fact_node:
            print("conflict")
            yield None
        bindings[head_node] = fact_node
        print("bound")
        yield bindings
    elif isinstance(head_node, Graph):
        if not isinstance(fact_node, Graph):
            yield None
        yield from match_rule(list(head_node), cast(Graph, fact_node), bindings)
    else:
        raise TypeError


def bind(
    head_clause: Triple, fact: Triple, bindings: Bindings
) -> Iterator[Bindings | None]:
    print("binding triple", head_clause, json.dumps(bindings))
    for var, val in zip(head_clause, fact, strict=True):
        for new_bindings in bind_node(var, val, bindings):
            if new_bindings is None:
                yield None
                return
                bindings.update(bindings)
    yield bindings


def mask_node(node: Node, bindings: Bindings) -> Node | None:
    if isinstance(node, Variable | BNode):
        return bindings.get(node, None)
    assert isinstance(node, URIRef | Literal | Graph)
    return node


def mask(head_clause: Triple, bindings: Bindings) -> Mask:
    return (
        mask_node(head_clause[0], bindings),
        mask_node(head_clause[1], bindings),
        mask_node(head_clause[2], bindings),
    )


def match_rule(
    head: Sequence[Triple], facts: Graph, bindings: Bindings
) -> Iterator[Bindings]:
    if len(head) == 0:
        yield bindings
    else:
        head_clause = head[0]
        mask_ = mask(head_clause, bindings)
        for fact in facts.triples(mask_):
            new_bindings = bindings.copy()
            for binding in bind(head_clause, fact, new_bindings):
                if binding is not None:
                    yield from match_rule(head[1:], facts, new_bindings)



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


def single_pass(facts: Graph, rules: Iterable[Triple]) -> Iterator[Triple]:
    for head, implies, body in rules:
        assert isinstance(head, Graph)
        assert implies == LOG.implies
        assert isinstance(body, Graph)
        for bindings in match_rule(list(head), facts, {}):
            if bindings is None:
                print("there was a conflict, not producing")
                continue
            for triple in body:
                print("producing triple from", triple, json.dumps(bindings))
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
