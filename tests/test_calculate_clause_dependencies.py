from typing import cast

import pytest
from rdflib import Graph, Namespace

from knom.stratified import calculate_clause_dependencies, get_all_clauses

EX = Namespace("http://example.com/")


def test_calculate_clause_dependencies() -> None:
    g = Graph().parse(location="tests/n3/recursive/simple.n3", format="n3")
    expected = Graph().parse(location="tests/n3/recursive/simple-deps.n3", format="n3")
    expected_depends = {
        (next(iter(cast(Graph, formula1))), next(iter(cast(Graph, formula2))))
        for formula1, _, formula2 in expected.triples((None, EX.depends, None))
    }
    clauses = get_all_clauses(g)
    depends = calculate_clause_dependencies(clauses)
    assert depends == expected_depends


def test_calculate_clause_dependencies_with_graph() -> None:
    g = Graph().parse(location="tests/n3/recursive/with_graph.n3", format="n3")
    clauses = get_all_clauses(g)
    depends = calculate_clause_dependencies(clauses)
    pytest.xfail("TODO")
    assert depends == []
