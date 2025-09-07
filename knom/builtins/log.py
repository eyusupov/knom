from collections.abc import Iterator

from rdflib import Graph, BNode, Variable, Namespace
from rdflib.term import Node

from knom.typing import Bindings
from knom.util import split_rules_and_facts

LOG = Namespace("http://www.w3.org/2000/10/swap/log#")


def includes(s: Node, o: Node, bindings: Bindings, doc: Graph) -> Iterator[Bindings]:
    if isinstance(s, BNode | Variable):
        _, facts = split_rules_and_facts(doc)
    elif isinstance(s, Graph):
        facts = s
    else:
        raise AssertionError
    from knom import match_rule, single_rule, get_next_head, fire_rule
    for bindings_ in match_rule(o, facts):
        yield bindings_
