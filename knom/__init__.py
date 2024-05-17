from collections.abc import Iterable, Iterator, Sequence
from typing import cast

from rdflib import BNode, Graph, Literal, URIRef, Variable
from rdflib.term import Node

from knom.builtins import BUILTINS
from knom.typing import Bindings, Mask, Triple
from knom.util import LOG, print_triple


def bind_node(
    head_node: Node,
    fact_node: Node,
    bindings: Bindings | None = None,
) -> Iterator[Bindings]:
    if bindings is None:
        bindings = {}
    if isinstance(fact_node, Variable):
        return
    if isinstance(head_node, URIRef | Literal):
        if head_node != fact_node:
            return
        yield bindings
    elif isinstance(head_node, BNode | Variable):
        if bindings.get(head_node, fact_node) != fact_node:
            if head_node != fact_node:
                return
            yield bindings
        else:
            new_bindings = bindings.copy()
            new_bindings[head_node] = fact_node
            yield new_bindings
    elif isinstance(head_node, Graph):
        if not isinstance(fact_node, Graph):
            return
        yield from match_rule(list(head_node), cast(Graph, fact_node), bindings)
    else:
        raise TypeError


def bind(
    head_clause: Triple,
    fact: Triple,
    bindings: Bindings | None = None,
) -> Iterator[Bindings]:
    s, p, o = head_clause
    if bindings is None:
        bindings = {}
    for s_binding in bind_node(s, fact[0], bindings):
        for p_binding in bind_node(p, fact[1], s_binding):
            yield from bind_node(o, fact[2], p_binding)


def mask_node(node: Node, bindings: Bindings) -> Node | None:
    if isinstance(node, Graph):
        return None
    if isinstance(node, Variable | BNode):
        return bindings.get(node, None)
    assert isinstance(node, URIRef | Literal)
    return node


def mask(head_clause: Triple, bindings: Bindings | None = None) -> Mask:
    if bindings is None:
        bindings = {}
    return (
        mask_node(head_clause[0], bindings),
        mask_node(head_clause[1], bindings),
        mask_node(head_clause[2], bindings),
    )

def head_sort_key(prev_clause, clause, bindings):
    ps, pp, po = prev_clause
    s, p, o = clause
    return (
        ps == s,
        pp == p,
        po == o,
        sum(1 if node in bindings else 0 for node in clause)
    )


def get_next_head(prev_clause: Triple, head: set[Triple], bindings: Bindings) -> tuple:
    if head == set():
        return None, set()
    next_head = max(head, key=lambda triple: head_sort_key(prev_clause, triple, bindings))
    remaining = head.copy()
    remaining.remove(next_head)
    return next_head, remaining


def match_rule(
    head_clause: Triple, head: set[Triple], facts: Graph, bindings: Bindings
) -> Iterator[Bindings]:
    if head_clause == None:
        yield bindings
    else:
        s, p, o = head_clause
        if p in BUILTINS:
            for binding in BUILTINS[p](s, o, bindings.copy()):
                next_head, remaining = get_next_head(head_clause, head, bindings)
                yield from match_rule(next_head, remaining, facts, binding)
        else:
            mask_ = mask(head_clause, bindings)
            triples = facts.triples(mask_)
            for fact in triples:
                for binding in bind(head_clause, fact, bindings):
                    next_head, remaining = get_next_head(head_clause, head, bindings)
                    yield from match_rule(next_head, remaining, facts, binding)


def instantiate_bnodes(body: Graph, bindings: Bindings) -> None:
    for triple in body:
        for node in triple:
            if isinstance(node, BNode) and node not in bindings:
                bindings[node] = BNode()


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
    for s, p, o in rules:
        if p == LOG.implies:
            head = s
            body = o
        elif p == LOG.impliedBy:
            head = o
            body = s
        else:
            continue
        assert isinstance(head, Graph)
        head_ = set(head)
        if head_ == set():
            # TODO
            continue
            raise NotImplemented
        print([print_triple(clause) for clause in head_])
        for bindings in match_rule(head_.pop(), head_, facts, {}):
            if isinstance(body, Variable):
                g = bindings[body]
                assert isinstance(g, Graph)
                for triple in g:
                    yield triple
            else:
                assert isinstance(body, Graph)
                instantiate_bnodes(body, bindings)
                for triple in body:
                    print('inferred')
                    yield assign(triple, bindings)


def naive_fixpoint(facts: Graph, rules: Graph) -> Iterable[Triple]:
    feed = Graph()
    for fact in facts:
        feed.add(fact)
    i = 0
    while True:
        old_len = len(feed)
        for new_triple in single_pass(feed, rules):
            yield new_triple
            feed.add(new_triple)
        if len(feed) == old_len:
            break
        i += 1
