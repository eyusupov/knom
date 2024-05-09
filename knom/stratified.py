import itertools
from collections.abc import Iterable

from rdflib import Graph

from knom import Triple, bind, single_pass

Dependencies = set[tuple[Triple, Triple]]


def matches(triple1: Triple, triple2: Triple) -> bool:
    return bind(triple1, triple2) is not None


def calculate_clause_dependencies(
    all_clauses: Iterable[Triple],
) -> Dependencies:
    depends = set()
    for clause1 in all_clauses:
        for clause2 in all_clauses:
            if clause1 == clause2:
                continue
            if not matches(clause1, clause2):
                continue
            depends.add((clause1, clause2))
    return depends


def get_all_clauses(rules: Graph) -> Iterable[Triple]:
    all_clauses: set[Triple] = set()
    for head, _, body in rules:
        assert isinstance(head, Graph)
        assert isinstance(body, Graph)
        all_clauses.update(head)
        all_clauses.update(body)
    return list(all_clauses)


def stratify_clauses(
    all_clauses: Iterable[Triple],
    depends: Dependencies,
) -> dict[Triple, int]:
    stratas = {c: 0 for c in all_clauses}
    while True:
        stratified = True
        for clause1 in all_clauses:
            for clause2 in all_clauses:
                if clause1 == clause2:
                    continue
                tup = (clause1, clause2)
                if tup in depends and stratas[clause2] <= stratas[clause1]:
                    stratas[clause2] += 1
                    stratified = False
                if tup in depends and stratas[clause1] <= stratas[clause2]:
                    stratas[clause2] += 1
                    stratified = False
        if stratified:
            break
    return stratas


def stratify_rules(rules: Graph) -> Iterable[Iterable[Triple]]:
    all_clauses = get_all_clauses(rules)
    depends = calculate_clause_dependencies(all_clauses)
    clause_stratas = stratify_clauses(all_clauses, depends)

    rule_stratas: dict[int, list[Triple]] = {}
    for rule in rules:
        head, _, body = rule
        assert isinstance(head, Graph)
        assert isinstance(body, Graph)
        strata = max([clause_stratas[clause] for clause in itertools.chain(head, body)])
        if strata not in rule_stratas:
            rule_stratas[strata] = []
        rule_stratas[strata].append(rule)
    return [rule_stratas[i] for i in sorted(rule_stratas.keys())]


def stratified(rules: Graph, facts: Graph) -> Graph:
    stratas = stratify_rules(rules)
    inferred = Graph()
    for strata in stratas:
        for new_tuple in single_pass(facts, strata):
            inferred.add(new_tuple)
        new_inferred = Graph()
        for new_tuple in single_pass(inferred, strata):
            new_inferred.add(new_tuple)
        for new_tuple in new_inferred:
            inferred.add(new_tuple)
    return inferred
