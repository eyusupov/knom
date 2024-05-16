from typing import cast

import pytest
from rdflib import Graph, Namespace

from knom.stratified import triggering_rules, get_all_clauses

EX = Namespace("http://example.com/")


def test_triggering_rules() -> None:
    g = Graph().parse(location="tests/n3/recursive/simple.n3", format="n3")
    expected = Graph().parse(location="tests/n3/recursive/simple-deps.n3", format="n3")
    rule = next(expected.triples((None, EX.depends, None)))
    depends = triggering_rules(rule)
    assert depends == [rule]


def test_triggering_rules_with_graph() -> None:
    g = Graph().parse(location="tests/n3/recursive/with_graph.n3", format="n3")
    clauses = get_all_clauses(g)
    depends = calculate_clause_dependencies(clauses)
    pytest.xfail("TODO")
    assert depends == []
