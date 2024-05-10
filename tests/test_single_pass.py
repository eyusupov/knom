from typing import T

from rdflib import RDF, Graph, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.compare import to_canonical_graph

from knom import LOG, single_pass

MF = Namespace("http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#")


def pytest_generate_tests(metafunc: T) -> None:
    g = Graph().parse(location="tests/n3/single-pass-manifests.n3", format="n3")
    names = []
    parameters = []
    for manifest, _, _  in g.triples((None, RDF.type, MF.Manifest)):
        mf_name = g.value(manifest, MF.name, None)
        entries = g.value(manifest, MF.entries, None)
        assert entries is not None, "could not find entries in the test manifest"
        for entry in Collection(g, entries):
            name = g.value(entry, MF.name, None)
            action = g.value(entry, MF.action, None)
            result = g.value(entry, MF.result, None)
            assert action is not None, f"action is empty for {name}"
            assert result is not None, f"result is empty for {name}"
            assert isinstance(action, URIRef)
            assert isinstance(result, URIRef)
            names.append(f"{mf_name}:{name}")
            parameters.append((action, result))
        metafunc.parametrize("action, result", parameters, ids=names)


def test_single_pass(action: URIRef, result: URIRef) -> None:
    action_graph = Graph().parse(location=action, format="n3")
    result_graph = Graph().parse(location=result, format="n3")
    rules = Graph(namespace_manager=action_graph.namespace_manager)
    facts = Graph(namespace_manager=action_graph.namespace_manager)
    for s, p, o in action_graph:
        if p == LOG.implies:
            rules.add((s, p, o))
        else:
            facts.add((s, p, o))
    output = Graph()
    for triple in single_pass(facts, rules):
        output.add(triple)
    assert set(to_canonical_graph(output)) == set(to_canonical_graph(result_graph))
