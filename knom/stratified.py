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
    for triple in g.triples((None, LOG.implies, None)):
        yield cast(Rule, triple)


def matches(head: Triple, fact: Triple) -> bool:
    #print("checking match", print_triple(head), "with", print_triple(fact))
    return all(n1 == n2 or n1 is None or n2 is None for n1, n2 in zip(mask(head), mask(fact), strict=True))


def clauses_depend(clauses: Graph, other_clauses: Graph) -> bool:
    for triple1 in clauses:
        for triple2 in other_clauses:
            if matches(triple1, triple2):
                return True
    return False


def dependent_rules(rule_with_body: Rule, rules_with_head: Graph) -> Iterable[Rule]:
    return {rule for rule in filter_rules(rules_with_head) if clauses_depend(rule_with_body[2], rule[0])}


def triggering_rules(rule_with_head: Rule, rules_with_body: Graph) -> Iterable[Rule]:
    return {rule for rule in filter_rules(rules_with_body) if clauses_depend(rule_with_head[0], rule[2])}


def last_index(index: RuleIndex) -> int:
    if index:
        return max(index.values())
    return 0


def stratify_rule(rule: Rule, rules: Graph, sccs: list[Graph], index: RuleIndex, low: RuleIndex, stack: list[Rule], level: int=0) -> None:
    index[rule] = last_index(index) + 1
    low[rule] = index[rule]
    stack.append(rule)
    for trigger in triggering_rules(rule, rules):
        if trigger not in index:
            stratify_rule(trigger, rules, sccs, index, low, stack, level+1)
            low[rule] = min(low[rule], low[trigger])
        elif trigger in stack:
            low[rule] = min(low[trigger], index[rule])
    if low[rule] == index[rule]:
        print("strata")
        top = None
        scc = Graph()
        while top != rule:
            top = stack.pop()
            print(print_rule(top))
            scc.add(top)
        sccs.append(scc)


def stratify_rules(rules: Graph) -> Iterable[Graph]:
    index: RuleIndex = {}
    low: RuleIndex = {}
    stack: list[Rule] = []
    stratified_rules: list[Graph] = []
    for rule in filter_rules(rules):
        if rule not in index:
            stratify_rule(rule, rules, stratified_rules, index, low, stack)

    return stratified_rules


def execute(rules: Graph, facts: Graph) -> Graph:
    stratas = stratify_rules(rules)
    inferred = Graph()
    for strata in stratas:
        for new_tuple in single_pass(facts + inferred, strata):
            inferred.add(new_tuple)
    return inferred
