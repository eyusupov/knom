from collections.abc import Iterable
from typing import cast

from rdflib import Graph, URIRef, Variable
from rdflib.graph import QuotedGraph

from knom import LOG, mask, single_pass
from knom.typing import Triple
from knom.util import print_rule

Rule = tuple[QuotedGraph, URIRef, QuotedGraph | Variable]
RuleIndex = dict[Rule, int]


def filter_rules(g: Graph) -> Iterable[Rule]:
    for triple in g.triples_choices((None, (LOG.implies, LOG.impliedBy), None)):
        yield cast(Rule, triple)


def matches(head: Triple, fact: Triple) -> bool:
    return all(
        n1 == n2 or n1 is None or n2 is None
        for n1, n2 in zip(mask(head), mask(fact), strict=True)
    )


def clauses_depend(clauses: Graph | Variable, other_clauses: Graph | Variable) -> bool:
    assert isinstance(clauses, Graph)
    assert isinstance(other_clauses, Graph)
    for triple1 in clauses:
        for triple2 in other_clauses:
            if matches(triple1, triple2):
                return True
    return False

def head(rule):
    s, p, o = rule
    if p == LOG.implies:
        return s
    else:
        return o


def body(rule):
    s, p, o = rule
    if p == LOG.implies:
        return o
    else:
        return s


def triggering_rules(rule_with_head: Rule, rules_with_body: Graph) -> Iterable[Rule]:
    return {
        rule
        for rule in filter_rules(rules_with_body)
        if clauses_depend(head(rule_with_head), body(rule))
    }


def last_index(index: RuleIndex) -> int:
    if index:
        return max(index.values())
    return 0


class _TarjanState:
    def __init__(self) -> None:
        self.index: dict[Rule, int] = {}
        self.low: dict[Rule,int] = {}
        self.stack: list[Rule]= []
        self.counter: int = 0

    def new_index(self) -> int:
        index = self.counter
        self.counter += 1
        return index


def stratify_rule(
    rule: Rule,
    rules: Graph,
    state: _TarjanState
) -> Iterable[Graph]:
    state.index[rule] = state.new_index()
    state.low[rule] = state.index[rule]
    state.stack.append(rule)
    for trigger in triggering_rules(rule, rules):
        if trigger not in state.index:
            yield from stratify_rule(trigger, rules, state)
            state.low[rule] = min(state.low[rule], state.low[trigger])
        elif trigger in state.stack:
            state.low[rule] = min(state.low[trigger], state.index[rule])
    if state.low[rule] == state.index[rule]:
        top = None
        scc = Graph()
        while top != rule:
            top = state.stack.pop()
            scc.add(top)
        yield scc


def stratify_rules(rules: Graph) -> Iterable[Graph]:
    stratified_rules: list[Graph] = []
    state = _TarjanState()
    for rule in filter_rules(rules):
        if rule not in state.index:
            stratified_rules.extend(stratify_rule(rule, rules, state))
    return stratified_rules


def execute(rules: Graph, facts: Graph) -> Graph:
    stratas = stratify_rules(rules)
    inferred = Graph()
    for strata in stratas:
        for new_tuple in single_pass(facts + inferred, strata):
            inferred.add(new_tuple)
    return inferred
