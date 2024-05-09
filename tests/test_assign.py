from knom import assign

from . import EX, bn_a, lit_b, var_a, var_b, var_c


def test_assign() -> None:
    assert assign(
        (var_a, var_b, var_c),
        {
            var_a: bn_a,
            var_b: lit_b,
            var_c: EX.c,
        },
    ) == (bn_a, lit_b, EX.c)
