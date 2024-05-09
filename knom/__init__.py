from collections.abc import AbstractSet, Generator, Iterable

from rdflib import BNode, Graph, Literal, Namespace, URIRef, Variable
from rdflib.term import Node

from knom.util import is_bnode, is_graph, is_var

LOG = Namespace("http://www.w3.org/2000/10/swap/log#")

Triple = tuple[Node, Node, Node]
MaskElement = Literal | URIRef | None
Mask = tuple[MaskElement, MaskElement, MaskElement]
Bindings = dict[Variable, Node]


def node_matches(n1: Node, n2: Node) -> bool:
    assert not is_graph(n1)
    assert not is_graph(n2)
    return is_var(n1) or is_var(n2) or n1 == n2 or is_bnode(n1) or is_bnode(n2)


def bind(triple1: Triple, triple2: Triple) -> None:
    bindings: Bindings = {}
    for x, y in zip(triple1, triple2, strict=True):
        if is_var(y) or is_bnode(y):
            binding = BNode if is_var(x) else x
            if bindings.get(y, bind) != binding:
                return None
            bindings[y] = binding
        elif not is_var(x) and not is_var(y) and x != y:
            return None
    return bindings


def matches(triple1: Triple, triple2: Triple) -> bool:
    return bind(triple2, triple1) is not None


def assign(triple: Triple, bindings: Bindings) -> Triple:
    return tuple(bindings.get(x, BNode()) if is_var(x) else x for x in triple)


def mask(triple: Triple, bindings: Bindings) -> Mask:
    return tuple(
        bindings.get(x, None) if is_var(x) else None if is_bnode(x) else x
        for x in triple
    )


def match_head(
    facts: Graph,
    head: Iterable[Triple],
    bound: AbstractSet[Triple] | None = None,
    bindings: Bindings | None = None,
) -> Generator[None, Triple, None]:
    if bindings is None:
        bindings = {}
    if bound is None:
        bound = set()
    mask_ = mask(head[0], bindings)
    for fact in facts.triples(mask_):
        if fact in bound:
            continue
        binding = bind(fact, head[0])
        binding.update(bindings)
        if len(head) == 1:
            yield binding
        else:
            yield match_head(facts, head[1:], bound.union(set(fact)), binding)


def single_pass(facts: Graph, rules: Graph) -> Graph:
    inferred = Graph()
    for head, implies, body in rules:
        assert implies == LOG.implies
        for binding in match_head(facts, list(head)):
            for body_clause in body:
                new_tuple = assign(body_clause, binding)
                yield new_tuple
    return inferred


def naive_fixpoint(facts: Graph, rules: Graph) -> Graph:
    inferred = Graph()
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
