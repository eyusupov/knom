from collections.abc import Iterable, Iterator

from rdflib import BNode, Graph, Namespace, Variable
from rdflib.term import Node

from knom.util import is_bnode, is_var

LOG = Namespace("http://www.w3.org/2000/10/swap/log#")

Triple = tuple[Node, Node, Node]
MaskElement = Node | None
Mask = tuple[MaskElement, MaskElement, MaskElement]
Bindings = dict[Variable | BNode, Node]


def bind(vars_: Triple, vals: Triple) -> Bindings | None:
    bindings: Bindings = {}
    for var, val in zip(vars_, vals, strict=True):
        if isinstance(var, BNode | Variable):
            binding = BNode() if is_var(val) else val
            if bindings.get(var, binding) != binding:
                # A variable is already bound to a different value
                # (used in the match test)
                return None
            bindings[var] = binding
        elif not is_var(val) and not is_var(var) and var != val:
            # Test that literals or uri refs are the same
            # (used in the match test)
            return None
    return bindings


def matches(triple1: Triple, triple2: Triple) -> bool:
    return bind(triple1, triple2) is not None


def get_node_binding(var: Node, bindings: Bindings) -> Node:
    assert isinstance(var, Variable | BNode)
    return bindings.get(var, BNode()) if is_var(var) else var


def assign(triple: Triple, bindings: Bindings) -> Triple:
    return (
        get_node_binding(triple[0], bindings),
        get_node_binding(triple[1], bindings),
        get_node_binding(triple[2], bindings),
    )


def get_node_mask(x: Node, bindings: Bindings) -> Node | None:
    assert isinstance(x, Variable | BNode)
    return bindings.get(x, None) if is_var(x) else None if is_bnode(x) else x


def mask(triple: Triple, bindings: Bindings) -> Mask:
    return (
        get_node_mask(triple[0], bindings),
        get_node_mask(triple[1], bindings),
        get_node_mask(triple[2], bindings),
    )


def match_head(
    facts: Graph,
    head: list[Triple],
    bound: set[Triple] | None = None,
    bindings: Bindings | None = None,
) -> Iterator[Bindings]:
    if bindings is None:
        bindings = {}
    if bound is None:
        bound = set()
    head_clauses = list(head)
    mask_ = mask(head_clauses[0], bindings)
    for fact in facts.triples(mask_):
        if fact in bound:
            continue
        binding = bind(head_clauses[0], fact)
        if binding is None:
            raise AssertionError
        binding.update(bindings)
        if len(head) == 1:
            yield binding
        else:
            yield from match_head(facts, head_clauses[1:], bound.union({fact}), binding)


def single_pass(facts: Graph, rules: Iterable[Triple]) -> Iterator[Triple]:
    for head, implies, body in rules:
        assert isinstance(head, Graph)
        assert implies == LOG.implies
        assert isinstance(body, Graph)
        for binding in match_head(facts, list(head)):
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
