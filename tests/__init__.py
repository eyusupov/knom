from rdflib import RDF, BNode, Graph, Literal, Namespace, URIRef, Variable
from rdflib.collection import Collection
from rdflib.plugins.parsers.notation3 import N3Parser, SinkParser
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
lit_triple2 = (lit_b, lit_c, lit_a)

vara_triple = (var_a, lit_b, lit_c)
varaa_triple = (var_a, var_a, lit_c)
varb_triple = (lit_a, var_b, lit_c)
varc_triple = (lit_a, lit_b, var_c)

bna_triple = (bn_a, lit_b, lit_c)
bnb_triple = (lit_a, bn_b, lit_c)
bnb_triple2 = (bn_b, lit_b, lit_c)
bnc_triple = (lit_a, lit_b, bn_c)

lit_graph = Graph().add(lit_triple)
lit_graph2 = Graph().add(lit_triple2)

vara_graph = Graph().add(vara_triple)
varaa_graph = Graph().add(varaa_triple)
varb_graph = Graph().add(varb_triple)
varc_graph = Graph().add(varc_triple)

bna_graph = Graph().add(bna_triple)
bnb_graph = Graph().add(bnb_triple)
bnc_graph = Graph().add(bnc_triple)

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


def prettify(g: Graph) -> set[str]:
    return {" ".join(n.n3() for n in triples) for triples in g}


def postprocess(graph: Graph) -> set[str]:
    cg = CanonicalizedGraph(graph)
    return prettify(cg.canon)
