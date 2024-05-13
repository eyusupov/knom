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


def stratify_rule(rule: Rule, rules: Graph, stratas: Stratas, visited: set[Rule], level=0) -> None:
    print("rule", print_rule(rule))
    for trigger_rule in triggering_rules(rule, rules):
        print("triggering rule", print_rule(rule))
        if trigger_rule not in visited:
            print("trigger not visited yet, visiting")
            visited.add(trigger_rule)
            stratify_rule(trigger_rule, rules, stratas, visited, level+1)
        else:
            print("trigger visited")

        if trigger_rule not in stratas:
            print("trigger not in strata, assigning 0")
            stratas[trigger_rule] = 0

        stratas[rule] = stratas[trigger_rule]
        if rule not in visited:
            print("this rule is not part of cycle, increasing strata")
            stratas[rule] += 1
        print("set rule strata to", stratas[rule])
    if rule not in stratas:
        print("rule not in strata, assigning 0")
        stratas[rule] = 0


def stratify_rules(rules: Graph) -> Iterable[Graph]:
    stratas: Stratas = {}
    visited: set[Rule] = set()

    for rule in filter_rules(rules):
        stratify_rule(rule, rules, stratas, visited)

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
