from rdflib import BNode, Literal, Namespace, Variable

from knom import node_matches

EX = Namespace("http://example.com/")

var_a = Variable("a")
var_b = Variable("b")
lit_a = Literal("a")
lit_b = Literal("b")


def test_two_vars_match() -> None:
    assert node_matches(var_a, var_b)


def test_var_matches_uriref() -> None:
    assert node_matches(var_a, EX.a)


def test_uriref_matches_var() -> None:
    assert node_matches(EX.a, var_a)


def test_bnode_matches_var() -> None:
    assert node_matches(BNode(), var_a)


def test_var_matches_bnode() -> None:
    assert node_matches(var_a, BNode())


def test_bnode_matches_uriref() -> None:
    assert node_matches(BNode(), EX.a)


def test_uriref_matches_bnode() -> None:
    assert node_matches(EX.a, BNode())


def test_uriref_matches_uriref() -> None:
    assert node_matches(EX.a, EX.a)


def test_var_matches_literal() -> None:
    assert node_matches(var_a, lit_a)


def test_bnode_matches_literal() -> None:
    assert node_matches(BNode(), lit_a)


def test_uriref_not_matches_literal() -> None:
    assert not node_matches(EX.a, lit_a)


def test_same_urirefs_match() -> None:
    assert node_matches(EX.a, EX.a)


def test_same_literals_match() -> None:
    assert node_matches(lit_a, lit_a)


def test_not_different_urirefs_match() -> None:
    assert not node_matches(EX.a, EX.b)


def test_not_different_literals_match() -> None:
    assert not node_matches(lit_a, lit_b)
