from rdflib import BNode, Literal, URIRef, Variable
from rdflib.term import Node

Triple = tuple[Node, Node, Node]
MaskElement = Node | None
Mask = tuple[MaskElement, MaskElement, MaskElement]
ValueNode = URIRef | Literal | BNode
Bindings = dict[Variable | BNode, ValueNode]
