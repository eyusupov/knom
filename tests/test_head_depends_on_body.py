import pytest
from rdflib import Graph

from knom.typing import Triple
from knom.stratified import head_depends_on_body

from . import (
    bna_triple,
    bnb_triple,
    bnb_triple2,
    lit_triple,
    lit_triple2,
    vara_triple,
)


@pytest.fixture()
def head() -> Graph:
    return Graph()


@pytest.fixture()
def body() -> Graph:
    return Graph()


def test_head_depends_on_body_same_lits(head: Graph, body: Graph) -> None:
    head.add(lit_triple)
    body.add(lit_triple)
    assert head_depends_on_body(head, body) == (True, set())


def test_head_depends_on_body_extra_lits(head: Graph, body: Graph) -> None:
    head.add(lit_triple)
    head.add(lit_triple2)
    body.add(lit_triple)
    assert head_depends_on_body(head, body) == (True, {lit_triple2})


def test_head_depends_on_body_bns_in_different_positions(head: Graph, body: Graph) -> None:
    head.add(bna_triple)
    head.add(bnb_triple)
    body.add(bna_triple)
    # TODO: this can actually bind to any triple. or can it?
    # ... => {
    #   _:a :b :c.
    #   :a _:b :c
    # }
    # {_:a :b :c} => ...
    # OR
    # ... => {
    #   :a _:b :c.
    #   _:a :b :c
    # }
    # ... => {_:a :b :c}.
    assert head_depends_on_body(head, body) == (True, {bna_triple})


def test_head_depends_on_body_bn_to_bn_extra_bn(head: Graph, body: Graph) -> None:
    head.add(bna_triple)
    head.add(bnb_triple2)
    body.add(bna_triple)
    assert head_depends_on_body(head, body) == (True, {bnb_triple2})

def test_head_depends_on_body_bn_to_bn_extra_bn_order1(body: Graph) -> None:
    head: list[Triple] = []
    head.append(bnb_triple2)
    head.append(bna_triple)
    body.add(bna_triple)
    assert head_depends_on_body(head, body) == (True, {bnb_triple2})

def test_head_depends_on_body_bn_to_bn_extra_bn_order2(body: Graph) -> None:
    head: list[Triple] = []
    head.append(bna_triple)
    head.append(bnb_triple2)
    body.add(bna_triple)
    assert head_depends_on_body(head, body) == (True, {bnb_triple2})
