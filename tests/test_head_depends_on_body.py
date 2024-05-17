from collections.abc import Iterable

import pytest
from rdflib import Graph

from knom.stratified import head_depends_on_body
from knom.typing import Triple

from . import (
    bna_triple,
    bnb_triple,
    bnb_triple2,
    lit_triple,
    lit_triple2,
)


@pytest.fixture()
def head() -> Graph:
    return Graph()


@pytest.fixture()
def body() -> Graph:
    return Graph()


def frozen(set_: Iterable[Iterable[Triple]]) -> set[frozenset[Triple]]:
    return set(map(frozenset, set_))


def check_result(head: Graph, body: Graph, expected: Iterable[Iterable[Triple]]) -> None:
    assert frozen(head_depends_on_body(head, body)) == frozen(expected)


def test_head_depends_on_body_same_lits(head: Graph, body: Graph) -> None:
    head.add(lit_triple)
    body.add(lit_triple)
    check_result(head, body, [[]])


def test_head_depends_on_body_extra_lits(head: Graph, body: Graph) -> None:
    head.add(lit_triple)
    head.add(lit_triple2)
    body.add(lit_triple)
    check_result(head, body, [[lit_triple2]])


def test_head_depends_on_body_bns_in_different_positions(head: Graph, body: Graph) -> None:
    head.add(bna_triple)
    head.add(bnb_triple)
    body.add(bna_triple)
    check_result(head, body, [[bna_triple], [bnb_triple]])


def test_head_depends_on_body_bn_to_bn_extra_bn(head: Graph, body: Graph) -> None:
    head.add(bna_triple)
    head.add(bnb_triple2)
    body.add(bna_triple)

    check_result(head, body, [[bna_triple], [bnb_triple2]])
