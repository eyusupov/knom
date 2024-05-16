from rdflib import Namespace

from . import math, string

STRING = Namespace("http://www.w3.org/2000/10/swap/string#")
MATH = Namespace("http://www.w3.org/2000/10/swap/math#")

# TODO: build with annotations or something
BUILTINS = {
    MATH.notLessThan: math.notLessThan,
    MATH.notGreaterThan: math.notGreaterThan,
    STRING.notLessThan: string.notLessThan,
    STRING.notGreaterThan: string.notGreaterThan,
}
