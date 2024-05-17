from knom.stratified import node_depends

from . import EX, bn_a, bn_b, bn_c, lit_a, lit_b, var_a, var_b


def test_node_depends_diff_urirefs() -> None:
    assert not node_depends(EX.a, EX.b, {})

def test_node_depends_same_urirefs() -> None:
    assert node_depends(EX.a, EX.a, {})

def test_node_depends_diff_literals() -> None:
    assert not node_depends(lit_a, lit_b, {})

def test_node_depends_same_literals() -> None:
    assert node_depends(lit_a, lit_a, {})

def test_node_depends_same_vars() -> None:
    assert node_depends(var_a, var_a, {})

def test_node_depends_diff_vars() -> None:
    assert node_depends(var_a, var_b, {})

def test_node_depends_var_uriref() -> None:
    assert node_depends(var_a, EX.a, {})

def test_node_depends_uriref_var() -> None:
    assert node_depends(EX.a, var_b, {})

def test_node_depends_same_bns() -> None:
    assert node_depends(bn_a, bn_a, {})

def test_node_depends_diff_bns() -> None:
    assert node_depends(bn_a, bn_b, {})

def test_node_depends_var_bn() -> None:
    assert node_depends(var_a, bn_a, {})

def test_node_depends_bn_var() -> None:
    assert node_depends(bn_a, var_a, {})

def test_node_depends_bns_no_conflict() -> None:
    assert node_depends(bn_a, bn_b, {bn_b: bn_a})

def test_node_depends_bns_conflict() -> None:
    assert not node_depends(bn_a, bn_b, {bn_a: bn_c})

def test_node_depends_bn_lit() -> None:
    assert node_depends(bn_a, lit_a, {})

def test_node_depends_lit_bn() -> None:
    assert node_depends(lit_a, bn_a, {})
