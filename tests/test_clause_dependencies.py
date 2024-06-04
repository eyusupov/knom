from collections.abc import Iterable

import pytest
from rdflib import Graph

from knom.stratified import clause_dependencies
from knom.typing import Triple

from . import (
    EX,
    bn_a,
    bna_triple,
    bnb_triple,
    bnb_triple2,
    lit_a,
    lit_triple,
    lit_triple2,
    var_a,
    var_b,
    var_c,
)


@pytest.fixture()
def head() -> Graph:
    return Graph()


@pytest.fixture()
def body() -> Graph:
    return Graph()


def frozen(set_: Iterable[Iterable[Triple]] | None) -> set[frozenset[Triple]]:
    if set_ is None:
        return set()
    return set(map(frozenset, set_))


def check_result(
    head: Graph, body: Graph, expected: Iterable[Iterable[Triple]] | None
) -> None:
    result = clause_dependencies(head, body)
    assert frozen(result) == frozen(expected)


def test_clause_dependencies_same_lits(head: Graph, body: Graph) -> None:
    body.add(lit_triple)
    head.add(lit_triple)
    check_result(head, body, [[]])


def test_clause_dependencies_extra_lits_in_body(head: Graph, body: Graph) -> None:
    body.add(lit_triple)
    body.add(lit_triple2)
    head.add(lit_triple)
    check_result(head, body, [[]])


def test_clause_dependencies_extra_lits_in_head(head: Graph, body: Graph) -> None:
    body.add(lit_triple)
    head.add(lit_triple)
    head.add(lit_triple2)
    check_result(head, body, [[lit_triple2]])


def test_clause_dependencies_bns_in_different_positions(
    head: Graph, body: Graph
) -> None:
    body.add(bna_triple)
    head.add(bna_triple)
    head.add(bnb_triple)
    check_result(head, body, [[bnb_triple]])


def test_clause_dependencies_extra_bns_in_head(head: Graph, body: Graph) -> None:
    body.add(bna_triple)
    head.add(bna_triple)
    head.add(bnb_triple2)

    check_result(head, body, [[bna_triple], [bnb_triple2]])


def test_clause_dependencies_extra_bns_in_body(head: Graph, body: Graph) -> None:
    body.add(bna_triple)
    body.add(bnb_triple)
    head.add(bna_triple)

    check_result(head, body, [])


def test_clause_dependencies_real_case_debug(head: Graph, body: Graph) -> None:
    body.add((bn_a, EX.type, EX.B))
    body.add((bn_a, EX.start, var_b))

    head.add((var_a, EX.start, var_b))
    head.add((var_a, EX.value, lit_a))

    check_result(head, body, None)


def test_clause_dependencies_real_case(head: Graph, body: Graph) -> None:
    body.add((bn_a, EX.type, EX.B))
    body.add((bn_a, EX.start, var_b))
    body.add((bn_a, EX.end, var_c))

    head.add((var_a, EX.start, var_b))
    head.add((var_a, EX.end, var_c))
    head.add((var_a, EX.value, lit_a))

    check_result(head, body, None)
