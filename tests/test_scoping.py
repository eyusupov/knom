from rdflib import Graph, URIRef

from knom.stratified import stratified
from knom.util import split_rules_and_facts

from . import generate_tests_from_manifests, postprocess

MANIFEST_PATH = "tests/n3/scoping-manifests.n3"


def pytest_generate_tests(metafunc) -> None:  # noqa: ANN001
    generate_tests_from_manifests(MANIFEST_PATH, metafunc)


def test_scoping(action: URIRef, result: URIRef) -> None:
    action_graph = Graph().parse(location=action, format="n3")
    rules, facts = split_rules_and_facts(action_graph)
    output = stratified(facts, rules)
    result_graph = Graph().parse(location=result, format="n3")

    assert postprocess(output) == postprocess(result_graph)
