from collections.abc import Callable, Iterable

from rdflib import Namespace, URIRef
from rdflib.term import Node

from knom.typing import Bindings

from . import math, string, log

STRING = Namespace("http://www.w3.org/2000/10/swap/string#")
MATH = Namespace("http://www.w3.org/2000/10/swap/math#")
LOG = Namespace("http://www.w3.org/2000/10/swap/log#")

# TODO: build with annotations or something
BUILTINS: dict[URIRef, Callable[[Node, Node, Bindings], Iterable[Bindings]]] = {
    MATH.notLessThan: math.not_less_than,
    MATH.notGreaterThan: math.not_greater_than,
    MATH.lessThan: math.less_than,
    MATH.greaterThan: math.greater_than,
    STRING.notLessThan: string.not_less_than,
    STRING.notGreaterThan: string.not_greater_than,
    STRING.ord: string.ord_,
    LOG.includes: log.includes
}
