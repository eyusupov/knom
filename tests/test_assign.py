from rdflib import BNode

from knom import assign

from . import EX, bn_a, bn_b, bn_c, lit_b, lit_c, lit_graph, var_a, var_b, var_c


def test_assign() -> None:
    assert assign(
        (var_a, var_b, var_c),
        {
            var_a: bn_a,
            var_b: lit_b,
            var_c: EX.c,
        },
    ) == (bn_a, lit_b, EX.c)


def test_assign_unbound_var() -> None:
    triple = assign(
        (var_a, var_b, var_c),
        {
            var_a: bn_a,
            var_b: lit_b
        },
    )
    assert triple[:2] == (bn_a, lit_b)
    assert isinstance(triple[2], BNode)


def test_assign_unbound_bnode() -> None:
    triple = assign(
        (var_a, var_b, bn_c),
        {
            var_a: bn_a,
            var_b: lit_b
        },
    )
    assert triple[:2] == (bn_a, lit_b)
    assert isinstance(triple[2], BNode)
    assert triple[2] != bn_c


def test_assign_bound_bnode() -> None:
    triple = assign(
        (var_a, var_b, bn_c),
        {
            var_a: bn_a,
            var_b: lit_b,
            bn_c: lit_c
        },
    )
    assert triple == (bn_a, lit_b, lit_c)


def test_assign_bnode_bound_to_bnode() -> None:
    triple = assign(
        (var_a, var_b, bn_c),
        {
            var_a: bn_a,
            var_b: lit_b,
            bn_c: bn_b
        },
    )
    assert triple == (bn_a, lit_b, bn_b)


def test_assign_var_bound_to_graph() -> None:
    triple = assign(
        (var_a, var_b, bn_c),
        {
            var_a: lit_graph,
            var_b: lit_b,
            bn_c: bn_b
        },
    )
    assert triple == (lit_graph, lit_b, bn_b)


def test_assign_bnode_bound_to_graph() -> None:
    triple = assign(
        (bn_a, var_b, bn_c),
        {
            bn_a: lit_graph,
            var_b: lit_b,
            bn_c: bn_b
        },
    )
    assert triple == (lit_graph, lit_b, bn_b)
