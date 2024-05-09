from collections.abc import AbstractSet

from pygraphviz import AGraph
from rdflib import Graph, Namespace

from knom import LOG, Triple

# TODO(eyusupov): remove
EX = Namespace("http://example.com/")


def print_triple(triple: Triple) -> str:
    return ", ".join([c.toPython().replace(EX, ":") for c in triple])


def print_formula(formula: Graph) -> str:
    return "{" + ". ".join([print_triple(c) for c in formula]) + "}"


def print_rule(rule: Triple) -> str:
    head, implies, body = rule
    assert implies == LOG.implies
    return f"{print_formula(head)} => {print_formula(body)}"


def draw_clause_dependencies_graph(clause_dependencies: AbstractSet[Triple]) -> AGraph:
    dot = AGraph(directed=True)
    for clause1, clause2 in clause_dependencies:
        c1 = print_triple(clause1)
        dot.add_node(c1)
        c2 = print_triple(clause2)
        dot.add_node(c2)
        dot.add_edge(c1, c2)
    return dot
