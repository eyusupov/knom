from collections.abc import Iterable, Iterator, Sequence
from typing import cast

from rdflib import BNode, Graph, Literal, URIRef, Variable
from rdflib.term import Node

from knom.typing import Bindings, Mask, Triple
from knom.util import LOG
from knom.util import print_triple


def bind_node(
    head_node: Node,
    fact_node: Node,
    bindings: Bindings | None = None,
    *,
    match_mode: bool = False,
) -> Iterator[Bindings]:
    if bindings is None:
        bindings = {}
    if isinstance(fact_node, Variable) and not match_mode:
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
        new_bindings = bindings.copy()
        new_bindings[head_node] = fact_node
        yield new_bindings
    elif isinstance(head_node, Graph):
        if not isinstance(fact_node, Graph):
            return
        new_bindings = bindings.copy()
        yield from match_rule(list(head_node), cast(Graph, fact_node), new_bindings)
    else:
        raise TypeError


def bind(
    head_clause: Triple,
    fact: Triple,
    bindings: Bindings | None = None,
    *,
    match_mode: bool = False,
) -> Iterator[Bindings]:
    if bindings is None:
        bindings = {}
    s, p, o = head_clause
    for s_binding in bind_node(s, fact[0], bindings, match_mode=match_mode):
        for p_binding in bind_node(p, fact[1], s_binding, match_mode=match_mode):
            yield from bind_node(o, fact[2], p_binding, match_mode=match_mode)


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


def match_rule(
    head: Sequence[Triple], facts: Graph, bindings: Bindings
) -> Iterator[Bindings]:
    if len(head) == 0:
        yield bindings
    else:
        head_clause = head[0]
        mask_ = mask(head_clause, bindings)
        for fact in facts.triples(mask_):
            #print("head_clause", print_triple(head_clause, facts.namespace_manager))
            #print("feeding", print_triple(fact, facts.namespace_manager))
            new_bindings = bindings.copy()
            for binding in bind(head_clause, fact, new_bindings):
                yield from match_rule(head[1:], facts, binding)


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
        for bindings in match_rule(list(head), facts, {}):
            if isinstance(body, Variable):
                g = bindings[body]
                assert isinstance(g, Graph)
                for triple in g:
                    yield triple
            else:
                assert isinstance(body, Graph)
                bindings_ = bindings.copy()
                instantiate_bnodes(body, bindings_)
                for triple in body:
                    yield assign(triple, bindings_)


def naive_fixpoint(facts: Graph, rules: Graph) -> Graph:
    inferred = Graph(namespace_manager=facts.namespace_manager)
    feed = Graph()
    for fact in facts:
        feed.add(fact)
    i = 1
    while True:
        old_inferred = len(inferred)
        print("pass ", i)
        for new_triple in single_pass(feed, rules):
            print("inferred", print_triple(new_triple, facts.namespace_manager))
            inferred.add(new_triple)
            feed.add(new_triple)
        if len(inferred) == old_inferred:
            break
        i += 1
    return inferred
