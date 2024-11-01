from rdflib import BNode, Literal, URIRef, Variable
from rdflib.graph import QuotedGraph
from rdflib.term import Node

Triple = tuple[Node, Node, Node]
MaskElement = Node | None
Mask = tuple[MaskElement, MaskElement, MaskElement]
ValueNode = URIRef | Literal | BNode
Bindings = dict[Variable | BNode, Node]
Rule = tuple[QuotedGraph, URIRef, QuotedGraph | Variable]
RulesDependencies = dict[Rule, set[Rule]]

