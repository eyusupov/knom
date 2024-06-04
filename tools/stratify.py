#!/usr/bin/env python
import sys

from rdflib import Graph

from knom.stratified import stratify_rules
from knom.util import add_triples, split_rules_and_facts

rules, _ = split_rules_and_facts(Graph().parse(sys.argv[1]))
stratified_rules = stratify_rules(rules)
for i, strata in enumerate(stratified_rules):
    g = Graph(namespace_manager=rules.namespace_manager)
    add_triples(g, strata)
    print("strata", i, ", rules:", len(strata))
    print(g.serialize(format="n3"))
