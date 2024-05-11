from rdflib import Graph, URIRef
from rdflib_canon import CanonicalizedGraph

from knom import single_pass

from . import generate_tests_from_manifests, split_rules_and_facts


def pytest_generate_tests(metafunc) -> None:  # noqa: ANN001
    generate_tests_from_manifests("tests/n3/single-pass-manifests.n3", metafunc)


def test_single_pass(action: URIRef, result: URIRef) -> None:
    action_graph = Graph().parse(location=action, format="n3")
    rules, facts = split_rules_and_facts(action_graph)
    id_ = URIRef("#")
    output = Graph(identifier=id_)
    for triple in single_pass(facts, rules):
        output.add(triple)
    result_graph = Graph(identifier=id_).parse(location=result, format="n3")
    assert set(CanonicalizedGraph(output).canon) == set(
        CanonicalizedGraph(result_graph).canon
    )
