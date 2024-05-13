import pytest
from rdflib import Graph, BNode, URIRef
from rdflib.collection import Collection

from knom.stratified import stratify_rules

from . import split_rules_and_facts, EX, generate_tests_from_manifests

MANIFEST_PATH = "tests/n3/stratification-manifests.n3"


def pytest_generate_tests(metafunc) -> None:  # noqa: ANN001
    generate_tests_from_manifests(MANIFEST_PATH, metafunc)


def test_single_pass(action: URIRef, result: URIRef) -> None:
    g = Graph().parse(location=action, format="n3")
    rules, facts = split_rules_and_facts(g)
    stratified_rules = stratify_rules(rules)
    expected_graph = Graph().parse(location=result, format="n3")
    expected_node = expected_graph.value(EX.Result, EX.stratas, None)
