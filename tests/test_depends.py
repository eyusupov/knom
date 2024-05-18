from knom.stratified import depends

from . import bn_a, bn_c, bna_triple, bnb_triple2, lit_triple, lit_triple2, vara_triple


def test_depends_lits_not_match() -> None:
    assert not depends(lit_triple, lit_triple2, {})


def test_depends_lits_match() -> None:
    assert depends(lit_triple, lit_triple, {})


def test_depends_var_lits_match() -> None:
    assert depends(lit_triple, vara_triple, {})


def test_depends_var_lits_not_match() -> None:
    assert not depends(lit_triple2, vara_triple, {})


def test_depends_bns_lits_match() -> None:
    assert depends(lit_triple, bna_triple, {})


def test_depend_bns_lits_not_match() -> None:
    assert not depends(lit_triple2, bna_triple, {})


def test_depend_bns_match() -> None:
    assert depends(bna_triple, bnb_triple2, {})


def test_depend_bns_conlicts_do_not_match() -> None:
    assert not depends(bna_triple, bnb_triple2, {bn_a: bn_c})
