import pytest
from rdflib import Graph

from knom import match_head

from . import EX, bn_a, bn_b, bn_c, lit_a, lit_b, lit_c, var_a, var_b, var_c


def test_match_head() -> None:
    facts = Graph()
    facts.add((EX.a, EX.b, EX.c))
    head = [(EX.a, EX.b, EX.c)]
    bindings = list(match_head(facts, head))
    assert(bindings == [{}])

def test_match_head_with_vars() -> None:
    facts = Graph()
    facts.add((EX.a, EX.b, EX.c))
    head = [(var_a, var_b, EX.c)]
    bindings = list(match_head(facts, head))
    assert len(bindings) == 1
    assert bindings[0] == {
        var_a: EX.a,
        var_b: EX.b,
    }

def test_match_head_same_var() -> None:
    facts = Graph()
    facts.add((EX.a, EX.a, EX.c))
    head = [(var_a, var_a, EX.c)]
    bindings = list(match_head(facts, head))
    assert len(bindings) == 1
    assert bindings[0] == {
        var_a: EX.a,
    }

def test_match_head_with_vars_conflict() -> None:
    facts = Graph()
    facts.add((EX.a, EX.b, EX.c))
    head = [(var_a, var_a, EX.c)]
    bindings = list(match_head(facts, head))
    assert bindings == []

def test_match_head_with_vars_conflict_in_clauses() -> None:
    facts = Graph()
    facts.add((EX.a, EX.a, EX.c))
    facts.add((EX.b, EX.c, EX.c))
    head = [(var_a, var_a, EX.c), (var_a, EX.c, EX.c)]
    bindings = list(match_head(facts, head))
    assert bindings == []

def test_match_head_with_vars_multiple_clauses() -> None:
    facts = Graph()
    facts.add((EX.a, EX.a, EX.c))
    facts.add((EX.q, EX.q, EX.d))
    head = [(var_a, var_a, EX.c), (var_b, var_b, EX.d)]
    bindings = list(match_head(facts, head))
    assert len(bindings) == 1
    assert bindings[0] == {
        var_a: EX.a,
        var_b: EX.q,
    }

def test_match_head_with_bnodes() -> None:
    facts = Graph()
    facts.add((EX.a, EX.b, bn_b))
    head = [(bn_a, EX.b, bn_c)]
    bindings = list(match_head(facts, head))
    assert len(bindings) == 1
    assert bindings[0] == {
        bn_a: EX.a,
        bn_c: bn_b,
    }

def test_match_head_same_bnode() -> None:
    facts = Graph()
    facts.add((EX.a, EX.a, EX.c))
    head = [(bn_a, bn_a, EX.c)]
    bindings = list(match_head(facts, head))
    assert len(bindings) == 1
    assert bindings[0] == {
        bn_a: EX.a,
    }

def test_match_head_with_bnodes_conflict() -> None:
    facts = Graph()
    facts.add((EX.a, EX.b, EX.c))
    head = [(bn_a, bn_a, EX.c)]
    bindings = list(match_head(facts, head))
    assert bindings == []

def test_match_head_with_bnodes_conflict_in_clauses() -> None:
    facts = Graph()
    facts.add((EX.a, EX.a, EX.c))
    facts.add((EX.b, EX.c, EX.c))
    head = [(bn_a, bn_a, EX.c), (bn_a, EX.c, EX.c)]
    bindings = list(match_head(facts, head))
    assert bindings == []

def test_match_head_with_bnodes_multiple_clauses() -> None:
    facts = Graph()
    facts.add((EX.a, EX.a, EX.c))
    facts.add((EX.q, EX.q, EX.d))
    head = [(bn_a, bn_a, EX.c), (bn_b, bn_b, EX.d)]
    bindings = list(match_head(facts, head))
    assert len(bindings) == 1
    assert bindings[0] == {
        bn_a: EX.a,
        bn_b: EX.q,
    }
