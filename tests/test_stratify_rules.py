from rdflib import Graph, URIRef

from knom.stratified import stratify_rules, get_rules_dependencies
from knom.util import print_rule

from . import EX, generate_tests_from_manifests, split_rules_and_facts

MANIFEST_PATH = "tests/n3/stratification-manifests.n3"


def pytest_generate_tests(metafunc) -> None:  # noqa: ANN001
    generate_tests_from_manifests(MANIFEST_PATH, metafunc)


def test_stratify_rules(action: URIRef, result: URIRef) -> None:
    g = Graph().parse(location=action, format="n3")
    rules, facts = split_rules_and_facts(g)
    stratified_rules = stratify_rules(rules)
    for strata in stratified_rules:
        print("strata")
        for rule in strata:
            print(print_rule(rule))
    expected_graph = Graph().parse(location=result, format="n3")
    expected_node = expected_graph.value(EX.Result, EX.stratas, None)
