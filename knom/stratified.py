from collections.abc import Iterable
from typing import cast

from rdflib import Graph, URIRef, Variable
from rdflib.graph import QuotedGraph

from knom import LOG, mask, single_pass
from knom.typing import Triple
from knom.util import print_rule

Rule = tuple[QuotedGraph, URIRef, QuotedGraph | Variable]
Stratas = dict[Rule, int]


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


def last_strata(stratas: Stratas) -> int:
    if stratas:
        return max(stratas.values()) + 1
    return 0


def stratify_rule(rule: Rule, rules: Graph, stratas: Stratas, visited: set[Rule], stratified: list[Rule], level=0) -> None:
    print(level, "stratify rule", print_rule(rule))
    if rule not in visited:
        visited.add(rule)
        for trigger_rule in dependent_rules(rule, rules):
            print(level, "processing neighbor", print_rule(trigger_rule))
            stratify_rule(trigger_rule, rules, stratas, visited, stratified, level+1)
        stratified.insert(0, rule)

def assign_strata(rule: Rule, rules: Graph, stratas: Stratas, counter: int, level: int = 0) -> None:
    if rule not in stratas:
        print(level, "assign strata", print_rule(rule), counter)
        stratas[rule] = counter
        for trigger in triggering_rules(rule, rules):
            print(level, "processing neighbor", print_rule(rule), counter)
            assign_strata(trigger, rules, stratas, counter, level+1)



def stratify_rules(rules: Graph) -> Iterable[Graph]:
    print("!!! stratifying")
    stratas: Stratas = {}
    visited: set[Rule] = set()
    stratified: list[Rule] = []

    for rule in filter_rules(rules):
        stratify_rule(rule, rules, stratas, visited, stratified)

    counter = 0
    for rule in stratified:
        if rule not in stratas:
            counter += 1
            assign_strata(rule, rules, stratas, counter)

    prev = -1
    stratified_rules = []
    for rule, i in sorted(stratas.items(), key=lambda item: item[1]):
        if prev < i:
            print("strata", i)
            strata = Graph()
            stratified_rules.append(strata)
        print(print_rule(rule))
        strata.add(rule)
        prev = i
    return stratified_rules


def execute(rules: Graph, facts: Graph) -> Graph:
    stratas = stratify_rules(rules)
    inferred = Graph()
    for strata in stratas:
        for new_tuple in single_pass(facts + inferred, strata):
            inferred.add(new_tuple)
    return inferred
