from collections.abc import Iterable, Iterator

from rdflib import BNode, Graph, Literal, Namespace, URIRef, Variable
from rdflib.term import Node


LOG = Namespace("http://www.w3.org/2000/10/swap/log#")

Triple = tuple[Node, Node, Node]
MaskElement = Node | None
Mask = tuple[MaskElement, MaskElement, MaskElement]
Bindings = dict[Variable | BNode, Node]


def bind(vars_: Triple, vals: Triple) -> Bindings | None:
    bindings: Bindings = {}
    for var, val in zip(vars_, vals, strict=True):
        if isinstance(var, BNode | Variable):
            if bindings.get(var, val) != val:
                # A variable is already bound to a different value
                return None
            bindings[var] = val
        elif isinstance(var, URIRef | Literal):
            if var != val:
                return None
        else:
            raise TypeError
    return bindings


def get_node_binding(var: Node, bindings: Bindings) -> Node:
    if isinstance(var, Variable):
        return bindings.get(var, BNode())
    return var


def assign(triple: Triple, bindings: Bindings) -> Triple:
    return (
        get_node_binding(triple[0], bindings),
        get_node_binding(triple[1], bindings),
        get_node_binding(triple[2], bindings),
    )


def get_node_mask(x: Node, bindings: Bindings) -> Node | None:
    if isinstance(x, Variable | BNode):
        return bindings.get(x, None)
    assert isinstance(x, URIRef | Literal)
    return x


def mask(triple: Triple, bindings: Bindings) -> Mask:
    return (
        get_node_mask(triple[0], bindings),
        get_node_mask(triple[1], bindings),
        get_node_mask(triple[2], bindings),
    )


def match_head_clause(
    facts: Graph,
    head_first: Triple,
    head_rest: Iterator[Triple],
    bound: set[Triple] | None = None,
    bindings: Bindings | None = None,
) -> Iterator[Bindings]:
    if bindings is None:
        bindings = {}
    if bound is None:
        bound = set()
    mask_ = mask(head_first, bindings)
    for fact in facts.triples(mask_):
        if fact in bound:
            continue
        binding = bind(head_first, fact)
        if binding is None or any(
            isinstance(val, Variable) for val in binding.values()
        ):
            continue
        bindings.update(binding)
        bound.add(fact)
        try:
            head_next = next(head_rest)
            yield from match_head_clause(facts, head_next, head_rest, bound, bindings)
        except StopIteration:
            yield bindings


def match_head(
    facts: Graph,
    head: Iterable[Triple],
) -> Iterator[Bindings]:
    head_iter = iter(head)
    return match_head_clause(facts, next(head_iter), head_iter)


def single_pass(facts: Graph, rules: Iterable[Triple]) -> Iterator[Triple]:
    for head, implies, body in rules:
        assert isinstance(head, Graph)
        assert implies == LOG.implies
        assert isinstance(body, Graph)
        for binding in match_head(facts, head):
            for body_clause in body:
                new_tuple = assign(body_clause, binding)
                yield new_tuple


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
