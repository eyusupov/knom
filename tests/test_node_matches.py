from rdflib import BNode, Literal, Namespace, Variable

from knom import node_matches

from . import EX, lit_a, lit_b, var_a, var_b


def test_matches_two_vars_match() -> None:
    assert node_matches(var_a, var_b)


def test_matches_var_matches_uriref() -> None:
    assert node_matches(var_a, EX.a)


def test_matches_uriref_matches_var() -> None:
    assert node_matches(EX.a, var_a)


def test_matches_bnode_matches_var() -> None:
    assert node_matches(BNode(), var_a)


def test_matches_var_matches_bnode() -> None:
    assert node_matches(var_a, BNode())


def test_matches_bnode_matches_uriref() -> None:
    assert node_matches(BNode(), EX.a)


def test_matches_uriref_matches_bnode() -> None:
    assert node_matches(EX.a, BNode())


def test_matches_uriref_matches_uriref() -> None:
    assert node_matches(EX.a, EX.a)


def test_matches_var_matches_literal() -> None:
    assert node_matches(var_a, lit_a)


def test_matches_bnode_matches_literal() -> None:
    assert node_matches(BNode(), lit_a)


def test_matches_uriref_not_matches_literal() -> None:
    assert not node_matches(EX.a, lit_a)


def test_matches_same_urirefs_match() -> None:
    assert node_matches(EX.a, EX.a)


def test_matches_same_literals_match() -> None:
    assert node_matches(lit_a, lit_a)


def test_matches_not_different_urirefs_match() -> None:
    assert not node_matches(EX.a, EX.b)


def test_matches_not_different_literals_match() -> None:
    assert not node_matches(lit_a, lit_b)
