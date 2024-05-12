from knom import bind
from knom.typing import Bindings

from . import (
    EX,
    bn_a,
    bn_b,
    bn_c,
    bna_graph,
    lit_a,
    lit_b,
    lit_c,
    lit_graph,
    var_a,
    var_b,
    var_c,
    vara_graph,
    varaa_graph,
)


def test_bind_var_to_bns() -> None:
    bindings: Bindings = {}
    assert bind((var_a, var_b, var_c), (bn_a, bn_b, bn_c), bindings)
    assert bindings == {
        var_a: bn_a,
        var_b: bn_b,
        var_c: bn_c,
    }


def test_bind_lits() -> None:
    bindings: Bindings = {}
    assert bind((var_a, var_b, var_c), (lit_a, lit_b, lit_c), bindings)
    assert bindings == {
        var_a: lit_a,
        var_b: lit_b,
        var_c: lit_c,
    }


def test_bind_urirefs() -> None:
    bindings: Bindings = {}
    assert bind((var_a, var_b, var_c), (lit_a, EX.b, EX.c), bindings)
    assert bindings == {
        var_a: lit_a,
        var_b: EX.b,
        var_c: EX.c,
    }


def test_bind_same_var_to_different_lits() -> None:
    bindings: Bindings = {}
    assert not bind((var_a, var_a, var_c), (lit_a, lit_b, lit_c), bindings)


def test_bind_lit_to_different_lit() -> None:
    bindings: Bindings = {}
    assert not bind((lit_b, var_b, var_c), (lit_a, lit_b, lit_c), bindings)


def test_bind_lit_to_same_lit() -> None:
    bindings: Bindings = {}
    assert bind((lit_a, var_b, var_c), (lit_a, lit_b, lit_c), bindings)
    assert bindings == {
        var_b: lit_b,
        var_c: lit_c,
    }


def test_bind_all_lits() -> None:
    bindings: Bindings = {}
    assert bind((lit_a, lit_b, lit_c), (lit_a, lit_b, lit_c), bindings)
    assert bindings == {}


def test_bind_bn_to_lit() -> None:
    bindings: Bindings = {}
    assert bind((bn_a, lit_b, lit_c), (lit_a, lit_b, lit_c), bindings)
    assert bindings == {bn_a: lit_a}


def test_bind_bn_to_same_lit() -> None:
    bindings: Bindings = {}
    assert bind((bn_a, bn_b, lit_c), (bn_c, bn_c, lit_c), bindings)
    assert bindings == {
        bn_a: bn_c,
        bn_b: bn_c,
    }


def test_bind_bns_to_same_lit() -> None:
    bindings: Bindings = {}
    assert bind((bn_a, bn_b, lit_c), (bn_c, bn_c, lit_c), bindings)
    assert bindings == {
        bn_a: bn_c,
        bn_b: bn_c,
    }


def test_bind_bn_to_different_lits() -> None:
    bindings: Bindings = {}
    assert not bind((bn_a, bn_a, lit_c), (bn_b, bn_c, lit_c), bindings)


def test_bind_var_to_var() -> None:
    bindings: Bindings = {}
    assert bind((var_a, lit_b, lit_c), (var_b, lit_b, lit_c), bindings)
    assert bindings == {var_a: var_b}


def test_bind_bn_to_var() -> None:
    bindings: Bindings = {}
    assert bind((bn_a, lit_b, lit_c), (var_b, lit_b, lit_c), bindings)
    assert bindings == {bn_a: var_b}


def test_bind_bn_to_bn() -> None:
    bindings: Bindings = {}
    assert bind((bn_a, bn_b, lit_c), (bn_a, bn_c, lit_c), bindings)
    assert bindings == {bn_a: bn_a, bn_b: bn_c}


def test_bind_uriref_to_urifef() -> None:
    bindings: Bindings = {}
    assert bind((EX.a, EX.b, EX.c), (EX.a, EX.b, EX.c), bindings)
    assert bindings == {}


def test_bind_uriref_to_different_urifef() -> None:
    bindings: Bindings = {}
    assert not bind((EX.a, EX.b, EX.c), (EX.a, EX.b, EX.d), bindings)


def test_bind_graph_to_var() -> None:
    bindings: Bindings = {}
    assert bind((var_a, lit_b, lit_c), (lit_graph, lit_b, lit_c), bindings)
    assert bindings == {var_a: lit_graph}


def test_bind_var_graph_to_graph() -> None:
    bindings: Bindings = {}
    assert bind((vara_graph, lit_b, lit_c), (lit_graph, lit_b, lit_c), bindings)
    assert bindings == {var_a: lit_a}


def test_bind_bn_graph_to_graph() -> None:
    bindings: Bindings = {}
    assert bind((bna_graph, lit_b, lit_c), (lit_graph, lit_b, lit_c), bindings)
    assert bindings == {bn_a: lit_a}


def test_bind_var_graph_to_graph_conflict() -> None:
    bindings: Bindings = {}
    assert not bind((varaa_graph, lit_b, lit_c), (lit_graph, lit_b, lit_c), bindings)
