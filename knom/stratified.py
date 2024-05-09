import itertools
from knom import matches


def calculate_clause_dependencies(all_clauses):
    depends = set()
    for clause1 in enumerate(all_clauses):
        for clause2 in all_clauses:
            if clause1 == clause2:
                continue
            if not matches(clause1, clause2):
                continue
            depends.add((clause1, clause2))
    return depends


def get_all_clauses(rules):
    all_clauses = set()
    for head, _, body in rules:
        all_clauses.update(head)
        all_clauses.update(body)
    return list(all_clauses)


def stratify_clauses(all_clauses, depends):
    stratas = {c: 0 for c in all_clauses}
    seen = set()
    while True:
        stratified = True
        for i, clause1 in enumerate(all_clauses):
            for clause2 in all_clauses:
                if clause1 == clause2:
                    continue
                if (clause1, clause2) in depends and stratas[clause2] <= stratas[clause1]:
                    stratas[clause2] += 1
                    stratified = False
                if (clause2, clause1) in depends and stratas[clause1] <= stratas[clause2]:
                    stratas[clause2] += 1
                    stratified = False
        if stratified:
            break
    return stratas


def stratify_rules(rules):
    all_clauses = get_all_clauses(rules)
    depends = calculate_clause_dependencies(all_clauses)
    clause_stratas = stratify_clauses(all_clauses, depends)

    rule_stratas = {}
    for rule in rules:
        head, _, body = rule
        strata = max([clause_stratas[clause] for clause in itertools.chain(head, body)])
        if strata not in rule_stratas:
            rule_stratas[strata] = []
        rule_stratas[strata].append(rule)
    return [rule_stratas[i] for i in sorted(rule_stratas.keys())]


def stratified(rules, facts):
    stratas = stratify_rules(rules) 
    for strata in stratas:
        for rule in rule_stratas[i]:
            for new_tuple in single_pass(facts, rules):
                inferred.add(new_tuple)
            new_inferred = Graph()
            for new_tuple in single_pass(inferred, rules):
                new_inferred.add(new_tuple)
            for new_tuple in new_inferred:
                inferred.add(new_tuple)

