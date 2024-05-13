import pytest
from rdflib import Graph

from knom.stratified import stratify_rules

from . import split_rules_and_facts


def test_stratify() -> None:
    g = Graph().parse(location="tests/n3/recursive/depends-on-cycle.n3", format="n3")
    rules, facts = split_rules_and_facts(g)
    stratified_rules = stratify_rules(rules)
    __import__('ipdb').set_trace()
    assert stratified_rules == []
