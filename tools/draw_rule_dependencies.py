#!/usr/bin/env python
import sys

from pygraphviz import AGraph
from rdflib import Graph

from knom.stratified import get_rules_dependencies, stratify_rules
from knom.util import print_rule, split_rules_and_facts

g = Graph().parse(sys.argv[1])
rules, facts = split_rules_and_facts(g)
rules_dependencies = get_rules_dependencies(rules)

dot = AGraph(directed=True)
for rule in rules:
    dot.add_node(print_rule(rule))

for rule1, deps in rules_dependencies.items():
    c1 = print_rule(rule1)
    for rule2 in deps:
        c2 = print_rule(rule2)
        dot.add_edge(c2, c1)

stratas = stratify_rules(rules, rules_dependencies)

for i, strata in enumerate(stratas, 1):
    dot.add_subgraph([print_rule(rule) for rule in strata], name=f'cluster_strata{i}', label=str(i))

print(dot.draw(prog='dot', format='svg').decode('utf-8'))
