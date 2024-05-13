from knom import bind_node

from . import (
    EX,
    bn_a,
    bn_c,
    bna_graph,
    lit_a,
    lit_b,
    lit_c,
    lit_graph,
    lit_graph2,
    var_a,
    var_b,
    vara_graph,
    varaa_graph,
)


def test_bind_node_var_to_bn() -> None:
    bindings = list(bind_node(var_a, bn_a))
    assert bindings == [{var_a: bn_a}]


def test_bind_node_var_to_same_bn() -> None:
    bindings = list(bind_node(var_a, bn_a, {var_a: bn_a}))
    assert bindings == [{var_a: bn_a}]

# Hmm...
def test_bind_node_var_to_different_bn() -> None:
    bindings = list(bind_node(var_a, bn_a, {var_a: bn_c}))
    assert bindings == []


def test_bind_node_var_to_lit() -> None:
    bindings = list(bind_node(var_a, lit_a))
    assert bindings == [{var_a: lit_a}]


def test_bind_node_var_to_same_lit() -> None:
    bindings = list(bind_node(var_a, lit_a, {var_a: lit_a}))
    assert bindings == [{var_a: lit_a}]


def test_bind_node_var_to_different_lit() -> None:
    bindings = list(bind_node(var_a, lit_a, {var_a: lit_b}))
    assert bindings == []


def test_bind_node_var_to_uriref() -> None:
    bindings = list(bind_node(var_b, EX.b))
    assert bindings == [{var_b: EX.b}]


def test_bind_node_var_to_same_uriref() -> None:
    bindings = list(bind_node(var_b, EX.b, {var_b: EX.b}))
    assert bindings == [{var_b: EX.b}]


def test_bind_node_var_to_different_uriref() -> None:
    bindings = list(bind_node(var_b, EX.a, {var_b: EX.b}))
    assert bindings == []


def test_bind_node_var_to_var() -> None:
    bindings = list(bind_node(var_a, var_b))
    assert bindings == []


def test_bind_node_lit_to_same_lit() -> None:
    bindings = list(bind_node(lit_a, lit_a))
    assert bindings == [{}]


def test_bind_node_lit_to_different_lit() -> None:
    bindings = list(bind_node(lit_b, lit_a))
    assert bindings == []


def test_bind_node_bn_to_lit() -> None:
    bindings = list(bind_node(bn_a, lit_a))
    assert bindings == [{bn_a: lit_a}]


def test_bind_node_bn_to_same_lit() -> None:
    bindings = list(bind_node(bn_c, lit_c, {bn_c: lit_c}))
    assert bindings == [{bn_c: lit_c}]


def test_bind_node_bn_to_different_lits() -> None:
    bindings = list(bind_node(bn_c, lit_c, {bn_c: lit_a}))
    assert bindings == []


def test_bind_node_bn_to_var() -> None:
    bindings = list(bind_node(bn_a, var_b))
    assert bindings == []


def test_bind_node_uriref_to_urifef() -> None:
    bindings = list(bind_node(EX.a, EX.a))
    assert bindings == [{}]


def test_bind_node_uriref_to_different_urifef() -> None:
    bindings = list(bind_node(EX.a, EX.b))
    assert bindings == []


def test_bind_node_graph_to_var() -> None:
    bindings = list(bind_node(var_a, lit_graph))
    assert bindings == [{var_a: lit_graph}]


def test_bind_node_graph_to_var_type_conflict() -> None:
    bindings = list(bind_node(var_a, lit_graph, {var_a: lit_c}))
    assert bindings == []


def test_bind_node_graph_to_var_conflict() -> None:
    bindings = list(bind_node(var_a, lit_graph, {var_a: lit_graph2}))
    assert bindings == []


def test_bind_node_var_graph_to_graph() -> None:
    bindings = list(bind_node(vara_graph, lit_graph))
    assert bindings == [{var_a: lit_a}]


def test_bind_node_var_graph_to_graph_conflict() -> None:
    bindings = list(bind_node(varaa_graph, lit_graph, {var_a: lit_b}))
    assert bindings == []


def test_bind_node_bn_graph_to_graph() -> None:
    bindings = list(bind_node(bna_graph, lit_graph))
    assert bindings == [{bn_a: lit_a}]


def test_bind_node_bn_graph_to_graph_conflict() -> None:
    bindings = list(bind_node(bna_graph, lit_graph, {bn_a: lit_b}))
    assert bindings == []


