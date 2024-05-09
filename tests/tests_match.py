from knom.stratified import matches

from . import EX, bn_a, bn_b, bn_c, var_a, var_b


def test_matches_urifefs() -> None:
    assert matches((EX.a, EX.b, EX.c), (EX.a, EX.b, EX.c))

def test_matches_urirefs_different_1() -> None:
    assert not matches((EX.a, EX.b, EX.c), (EX.b, EX.b, EX.c))

def test_matches_urirefs_different_2() -> None:
    assert not matches((EX.a, EX.b, EX.c), (EX.a, EX.a, EX.c))

def test_matches_urirefs_different_3() -> None:
    assert not matches((EX.a, EX.b, EX.c), (EX.a, EX.b, EX.a))

def test_matches_var_lit() -> None:
    assert matches((var_a, EX.b, EX.c), (EX.a, EX.b, EX.c))

def test_matches_lit_var() -> None:
    assert matches((EX.a, EX.b, EX.c), (var_a, EX.b, EX.c))

def test_matches_diff_lits_var() -> None:
    assert not matches((EX.a, EX.b, EX.c), (var_a, var_a, EX.c))

def test_matches_var_diff_lits_vars() -> None:
    assert not matches((var_a, var_a, EX.c), (EX.a, EX.b, EX.c))

def test_matches_bn_diff_lits_vars() -> None:
    assert not matches((bn_a, bn_a, EX.c), (EX.a, EX.b, EX.c))

def test_matches_diff_lits_vars_bn() -> None:
    assert not matches((EX.a, EX.b, EX.c), (bn_a, bn_a, EX.c))

def test_matches_bn_lit() -> None:
    assert matches((bn_a, EX.b, EX.c), (EX.a, EX.b, EX.c))

def test_matches_lit_bn() -> None:
    assert matches((EX.a, EX.b, EX.c), (bn_a, EX.b, EX.c))

def test_matches_var_var() -> None:
    assert matches((var_a, EX.b, EX.c), (var_b, EX.b, EX.c))

def test_matches_var_bn() -> None:
    assert matches((var_a, EX.b, EX.c), (bn_b, EX.b, EX.c))

def test_matches_bn_var() -> None:
    assert matches((EX.a, bn_b, EX.c), (EX.a, var_b, EX.c))

def test_matches_bn_bn() -> None:
    assert matches((bn_a, EX.b, EX.c), (bn_a, EX.b, EX.c))

def test_matches_bn_bn2() -> None:
    assert matches((EX.a, bn_b, EX.c), (EX.a, bn_c, EX.c))
