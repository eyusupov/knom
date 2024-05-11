from rdflib import Graph, URIRef
from rdflib_canon import CanonicalizedGraph

from knom import naive_fixpoint

from . import generate_tests_from_manifests, split_rules_and_facts


def pytest_generate_tests(metafunc) -> None:  # noqa: ANN001
    generate_tests_from_manifests(
        "tests/n3/positive-non-recursive-rules-manifests.n3", metafunc
    )


def test_single_pass(action: URIRef, result: URIRef) -> None:
    action_graph = Graph().parse(location=action, format="n3")
    rules, facts = split_rules_and_facts(action_graph)
    output = naive_fixpoint(facts, rules)
    result_graph = Graph().parse(location=result, format="n3")
    assert set(CanonicalizedGraph(output).canon) == set(
        CanonicalizedGraph(result_graph).canon
    )
