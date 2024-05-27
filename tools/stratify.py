#!/usr/bin/env python
import sys

from rdflib import Graph

from knom.stratified import stratify_rules
from knom.util import print_rule, split_rules_and_facts

rules, _ = split_rules_and_facts(Graph().parse(sys.argv[1]))
stratified_rules = stratify_rules(rules)
for i, strata in enumerate(stratified_rules):
    print("strata", i, ", rules:", len(strata))
    for rule in strata:
        print(print_rule(rule))
    #for rule in strata:
    #    print(print_rule(rule))
