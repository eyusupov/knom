from collections.abc import Iterator

from rdflib import Graph, BNode, Variable, Namespace
from rdflib.collection import Collection
from rdflib.term import Node

from knom.typing import Bindings
from knom.util import split_rules_and_facts, add_triples

LOG = Namespace("http://www.w3.org/2000/10/swap/log#")


def for_all_in(s: Collection, o: Node, bindings: Bindings, doc: Graph) -> Iterator[Bindings]:
    if isinstance(o, BNode | Variable):
        _, facts = split_rules_and_facts(doc)
    elif isinstance(o, Graph):
        facts = o
    else:
        raise AssertionError
    s1, s2 = s

    from knom.stratified import _stratified
    rules = Graph()
    rules.add((s1, LOG.implies, s1))
    facts1 = set(_stratified(facts, rules))
   
    rule2 = Graph()
    add_triples(rule2, s1)
    add_triples(rule2, s2)

    rules = Graph()
    rules.add((rule2, LOG.implies, rule2))
    facts2 = _stratified(facts, rules)
    if facts1.intersection(facts2) == facts1:
        yield bindings


def includes(s: Node, o: Node, bindings: Bindings, doc: Graph) -> Iterator[Bindings]:
    if isinstance(s, BNode | Variable):
        _, facts = split_rules_and_facts(doc)
    elif isinstance(s, Graph):
        facts = s
    else:
        raise AssertionError
    from knom import match_rule
    for bindings_ in match_rule(o, facts):
        yield bindings_
