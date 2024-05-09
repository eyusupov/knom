from rdflib import Graph, Namespace, BNode
from knom.util import is_graph, is_bnode, is_var


LOG = Namespace('http://www.w3.org/2000/10/swap/log#')


def node_matches(n1, n2):
    assert not is_graph(n1) and not is_graph(n2)
    return is_var(n1) or is_var(n2) or n1 == n2 or is_bnode(n1) or is_bnode(n2)


def bind(triple1, triple2):
    bindings = {}
    for x, y in zip(triple1, triple2):
        if is_var(y) or is_bnode(y):
            if is_var(x):
                x = BNode()
            if bindings.get(y, x) != x:
                return None
            bindings[y] = x
        elif not is_var(x) and not is_var(y) and x != y:
            return None
    return bindings


def matches(triple1, triple2):
    return bind(triple2, triple1) is not None  # noqa: W1114


def assign(triple, binding):
    return tuple(binding.get(x, BNode()) if is_var(x) else x for x in triple)


def mask(triple, bindings):
    return tuple(bindings.get(x, None) if is_var(x) else None if is_bnode(x) else x for x in triple)


def match_head(facts, head, bound=set(), bindings={}):
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
    return None


def single_pass(facts, rules):
    inferred = Graph()
    for head, implies, body in rules:
        assert implies == LOG.implies
        for binding in match_head(facts, list(head)):
            for body_clause in body:
                new_tuple = assign(body_clause, binding)
                yield new_tuple
    return inferred


def naive_fixpoint(facts, rules):
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
