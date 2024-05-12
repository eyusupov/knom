from rdflib import RDF, BNode, Graph, Literal, Namespace, URIRef, Variable
from rdflib.collection import Collection
from rdflib.plugins.serializers.nt import _nt_row
from rdflib_canon import CanonicalizedGraph

from knom import LOG

EX = Namespace("http://example.com/")
var_a = Variable("a")
var_b = Variable("b")
var_c = Variable("c")
lit_a = Literal("a")
lit_b = Literal("b")
lit_c = Literal("c")
bn_a = BNode("a")
bn_b = BNode("b")
bn_c = BNode("c")
lit_triple = (lit_a, lit_b, lit_c)

lit_graph = Graph()
lit_graph.add(lit_triple)

MF = Namespace("http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#")


def generate_tests_from_manifests(path: str, metafunc) -> None:  # noqa: ANN001
    g = Graph().parse(location=path, format="n3")
    names = []
    parameters = []
    for manifest, _, _ in g.triples((None, RDF.type, MF.Manifest)):
        entries = g.value(manifest, MF.entries, None)
        assert entries is not None, "could not find entries in the test manifest"
        for entry in Collection(g, entries):
            name = g.value(entry, MF.name, None)
            action = g.value(entry, MF.action, None)
            result = g.value(entry, MF.result, None)
            if action is None:
                continue
            if result is None:
                continue
            assert isinstance(action, URIRef)
            assert isinstance(result, URIRef)
            names.append(f"{name}".replace(" ", "_"))
            parameters.append((action, result))
        metafunc.parametrize("action, result", parameters, ids=names)


def split_rules_and_facts(graph: Graph) -> tuple[Graph, Graph]:
    rules = Graph(namespace_manager=graph.namespace_manager)
    facts = Graph(namespace_manager=graph.namespace_manager)
    for s, p, o in graph:
        if p == LOG.implies:
            rules.add((s, p, o))
        else:
            facts.add((s, p, o))
    return (rules, facts)


def prettify(g: Graph) -> set[str]:
    return {" ".join(n.n3() for n in triples) for triples in g}


def postprocess(graph: Graph) -> list[str]:
    cg = CanonicalizedGraph(graph)
    return prettify(cg.canon)
