import logging
from collections.abc import Iterable, Iterator
from hashlib import sha256
from typing import cast

from rdflib import BNode, Graph, Literal, URIRef, Variable
from rdflib.term import Node

from knom.builtins import BUILTINS, STRING
from knom.typing import Bindings, Mask, Triple
from knom.util import LOG, print_triple

logger = logging.getLogger(__name__)


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
        head = set(head_node)
        yield from match_rule(head.pop(), head, cast(Graph, fact_node), bindings)
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


def head_sort_key(
    prev_clause: Triple, clause: set[Triple], bindings: Bindings
) -> tuple:
    ps, pp, po = prev_clause
    s, p, o = clause

    key = (
        p not in BUILTINS,
        p == STRING.ord,
        ps == s,
        pp == p,
        po == o,
        sum(1 if node in bindings else 0 for node in clause),
    )
    logger.debug("key %s %s", print_triple(clause), key)
    return key


def get_next_head(
    prev_clause: Triple | tuple[None, None, None], head: set[Triple], bindings: Bindings
) -> tuple:
    # TODO: fix hex char range handling (builtins results are used in other builtins)
    if head == set():
        return None, set()
    # TODO: there is still varying performance from run to run, investigate
    next_head = max(
        head, key=lambda triple: head_sort_key(prev_clause, triple, bindings)
    )
    if next_head:
        logger.debug("head clause: %s, bindings %s", next_head, bindings)
    remaining = head.copy()
    remaining.remove(next_head)
    return next_head, remaining


def match_rule(
    head_clause: Triple, head: set[Triple], facts: Graph, bindings: Bindings
) -> Iterator[Bindings]:
    logger.debug("match_rule")
    if head_clause is None:
        yield bindings
    else:
        s, p, o = head_clause
        if p in BUILTINS:
            assert isinstance(p, URIRef)
            # TODO: copy bindings on update only
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
    identifiers = [f"{node}:{binding}" for node, binding in sorted(bindings.items())]
    base_path = "-".join(identifiers)
    for triple in body:
        for node in triple:
            if isinstance(node, BNode) and node not in bindings:
                path = f"{base_path}-{node}"
                id_ = sha256(path.encode("utf-8")).hexdigest()
                bindings[node] = BNode(id_)


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


def fire_rule(rule: Triple, bindings: Bindings) -> Iterator[Triple]:
    body = get_body(rule)
    if isinstance(body, Variable):
        g = bindings[body]
        assert isinstance(g, Graph)
        for triple in g:
            yield triple
    else:
        assert isinstance(body, Graph)
        instantiate_bnodes(body, bindings)
        for triple in body:
            yield assign(triple, bindings)


def single_rule(facts: Graph, rule: Triple) -> Iterator[Triple]:
    logger.debug("single_rule")
    head_graph = get_head(rule)
    assert isinstance(head_graph, Graph)
    head = set(head_graph)
    if head == set():
        yield from cast(Graph, get_body(rule))
        return
    next_head, remaining = get_next_head((None, None, None), head, {})
    for bindings in match_rule(next_head, remaining, facts, {}):
        yield from fire_rule(rule, bindings)


def single_pass(facts: Graph, rules: Iterable[Triple]) -> Iterator[Triple]:
    for rule in rules:
        yield from single_rule(facts, rule)
