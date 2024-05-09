from knom import mask

from . import EX, bn_a, bn_b, bn_c, lit_a, lit_b, lit_c, var_a, var_c


def test_mask() -> None:
    assert mask((EX.a, lit_b, lit_c), {}) == (EX.a, lit_b, lit_c)

def test_mask_unbound_var() -> None:
    assert mask((var_a, EX.b, EX.c), {}) == (None, EX.b, EX.c)

def test_mask_bound_var() -> None:
    assert mask(
        (var_a, EX.b, var_c),
        {var_a: lit_a, var_c: bn_b},
    ) == (lit_a, EX.b, bn_b)

def test_mask_bnode() -> None:
    assert mask((var_a, bn_a, EX.c), {var_a: lit_a}) == (lit_a, None, EX.c)

def test_mask_bound_bnode() -> None:
    assert mask(
        (var_a, bn_a, EX.c),
        {var_a: lit_a, bn_a: lit_c},
    ) == (lit_a, lit_c, EX.c)

def test_mask_bound_bnode_to_bnode() -> None:
    assert mask(
        (var_a, bn_a, bn_c),
        {var_a: lit_a, bn_a: bn_b},
    ) == (lit_a, bn_b, None)
