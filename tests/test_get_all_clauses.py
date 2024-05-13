import pytest
from rdflib import BNode, Graph, Namespace, Variable

from knom import LOG
from knom.stratified import get_all_clauses

EX = Namespace("http://example.com/")


def test_get_all_clauses() -> None:
    g = Graph().parse(location="tests/n3/recursive/simple.n3", format="n3")
    clauses = get_all_clauses(g)
    rule_body = next(g.triples((None, LOG.implies, None)))[2]
    assert isinstance(rule_body, Graph)
    bnode = rule_body.value(Variable("y"), EX.rest, None)
    assert isinstance(bnode, BNode)
    assert set(clauses) == {
        (Variable("x"), EX.rest, Variable("y")),
        (Variable("y"), EX.rest, bnode),
    }


def test_get_all_clauses_with_graph() -> None:
    g = Graph().parse(location="tests/n3/recursive/with_graph.n3", format="n3")
    clauses = get_all_clauses(g)
    pytest.xfail("Not sure if we need to extract clauses from graph terms yet")
    return
    rule_body = next(g.triples((None, LOG.implies, None)))[2]
    assert isinstance(rule_body, Graph)
    bnode_a = rule_body.value(Variable("y"), EX.rest, None)
    assert isinstance(bnode_a, BNode)
    bnode_b = rule_body.value(None, Variable("b"), EX.jump)
    assert isinstance(bnode_a, BNode)
    assert set(clauses) == {
        (Variable("x"), EX.rest, Variable("y")),
        (Variable("y"), EX.rest, bnode_a),
        (Variable("a"), Variable("b"), Variable("c")),
        (bnode_b, Variable("b"), EX.jump),
    }
