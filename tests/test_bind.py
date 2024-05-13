from knom import bind

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
    bindings = list(bind((var_a, var_b, var_c), (bn_a, bn_b, bn_c), {}))
    assert bindings == [{
        var_a: bn_a,
        var_b: bn_b,
        var_c: bn_c,
    }]


def test_bind_lits() -> None:
    bindings = list(bind((var_a, var_b, var_c), (lit_a, lit_b, lit_c), {}))
    assert bindings == [{
        var_a: lit_a,
        var_b: lit_b,
        var_c: lit_c,
    }]


def test_bind_urirefs() -> None:
    bindings = list(bind((var_a, var_b, var_c), (lit_a, EX.b, EX.c), {}))
    assert bindings == [{
        var_a: lit_a,
        var_b: EX.b,
        var_c: EX.c,
    }]


def test_bind_same_var_to_different_lits() -> None:
    bindings = list(bind((var_a, var_a, var_c), (lit_a, lit_b, lit_c), {}))
    assert bindings == []


def test_bind_lit_to_different_lit() -> None:
    bindings = list(bind((lit_b, var_b, var_c), (lit_a, lit_b, lit_c), {}))
    assert bindings == []


def test_bind_lit_to_same_lit() -> None:
    bindings = list(bind((lit_a, var_b, var_c), (lit_a, lit_b, lit_c), {}))
    assert bindings == [{
        var_b: lit_b,
        var_c: lit_c,
    }]


def test_bind_all_lits() -> None:
    bindings = list(bind((lit_a, lit_b, lit_c), (lit_a, lit_b, lit_c), {}))
    assert bindings == [{}]


def test_bind_bn_to_lit() -> None:
    bindings = list(bind((bn_a, lit_b, lit_c), (lit_a, lit_b, lit_c), {}))
    assert bindings == [{bn_a: lit_a}]


def test_bind_bn_to_same_lit() -> None:
    bindings = list(bind((bn_a, bn_b, lit_c), (bn_c, bn_c, lit_c), {}))
    assert bindings == [{
        bn_a: bn_c,
        bn_b: bn_c,
    }]


def test_bind_bns_to_same_lit() -> None:
    bindings = list(bind((bn_a, bn_b, lit_c), (bn_c, bn_c, lit_c), {}))
    assert bindings == [{
        bn_a: bn_c,
        bn_b: bn_c,
    }]


def test_bind_bn_to_different_lits() -> None:
    bindings = list(bind((bn_a, bn_a, lit_c), (bn_b, bn_c, lit_c), {}))
    assert bindings == []


def test_bind_var_to_var() -> None:
    bindings = list(bind((var_a, lit_b, lit_c), (var_b, lit_b, lit_c), {}))
    assert bindings == []


def test_bind_bn_to_var() -> None:
    bindings = list(bind((bn_a, lit_b, lit_c), (var_b, lit_b, lit_c), {}))
    assert bindings == []


def test_bind_bn_to_bn() -> None:
    bindings = list(bind((bn_a, bn_b, lit_c), (bn_a, bn_c, lit_c), {}))
    assert bindings == [{bn_a: bn_a, bn_b: bn_c}]


def test_bind_uriref_to_urifef() -> None:
    bindings = list(bind((EX.a, EX.b, EX.c), (EX.a, EX.b, EX.c), {}))
    assert bindings == [{}]


def test_bind_uriref_to_different_urifef() -> None:
    bindings = list(bind((EX.a, EX.b, EX.c), (EX.a, EX.b, EX.d), {}))
    assert bindings == []


def test_bind_graph_to_var() -> None:
    bindings = list(bind((var_a, lit_b, lit_c), (lit_graph, lit_b, lit_c), {}))
    assert bindings == [{var_a: lit_graph}]


def test_bind_var_graph_to_graph() -> None:
    bindings = list(bind((vara_graph, lit_b, lit_c), (lit_graph, lit_b, lit_c), {}))
    assert bindings == [{var_a: lit_a}]


def test_bind_bn_graph_to_graph() -> None:
    bindings = list(bind((bna_graph, lit_b, lit_c), (lit_graph, lit_b, lit_c), {}))
    assert bindings == [{bn_a: lit_a}]


def test_bind_var_graph_to_graph_conflict() -> None:
    bindings = list(bind((varaa_graph, lit_b, lit_c), (lit_graph, lit_b, lit_c), {}))
    assert bindings == []
