from collections.abc import Callable, Iterable

from rdflib import Namespace, URIRef
from rdflib.term import Node

from knom.typing import Bindings

from . import math, string

STRING = Namespace("http://www.w3.org/2000/10/swap/string#")
MATH = Namespace("http://www.w3.org/2000/10/swap/math#")

# TODO: build with annotations or something
BUILTINS: dict[URIRef, Callable[[Node, Node, Bindings], Iterable[Bindings]]] = {
    MATH.notLessThan: math.notLessThan,
    MATH.notGreaterThan: math.notGreaterThan,
    STRING.notLessThan: string.notLessThan,
    STRING.notGreaterThan: string.notGreaterThan,
    STRING.ord: string.ord_,
}
