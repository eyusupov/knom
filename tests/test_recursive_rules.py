import logging

from rdflib import Graph, URIRef

from knom.stratified import stratified
from knom.util import split_rules_and_facts

from . import (
    generate_tests_from_manifests,
    postprocess,
)

logging.getLogger("knom").setLevel(logging.DEBUG)
logging.getLogger("knom.stratified").setLevel(logging.DEBUG)

def pytest_generate_tests(metafunc) -> None:  # noqa: ANN001
    generate_tests_from_manifests(
        "tests/n3/recursive-manifests.n3", metafunc
    )


def test_recursive(action: URIRef, result: URIRef) -> None:
    action_graph = Graph().parse(location=action, format="n3")
    rules, facts = split_rules_and_facts(action_graph)
    output = stratified(facts, rules)
    result_graph = Graph().parse(location=result, format="n3")

    assert postprocess(output) == postprocess(result_graph)
