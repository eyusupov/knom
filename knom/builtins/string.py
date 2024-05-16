from collections.abc import Iterator

from rdflib import Literal, Variable, BNode

from knom.typing import Bindings


def notLessThan(s: Literal, o: Literal, bindings: Bindings) -> Iterator[Bindings]:
    assert isinstance(s.value, str)
    assert isinstance(o.value, str)
    if s.value >= o.value:
        yield bindings


def notGreaterThan(s: Literal, o: Literal, bindings: Bindings) -> Iterator[Bindings]:
    assert isinstance(s.value, str)
    assert isinstance(o.value, str)
    if s.value <= o.value:
        yield bindings


def ord_(s: Literal, o: Literal, bindings: Bindings) -> Iterator[Bindings]:
    o_ = bindings[o] if isinstance(o, Variable | BNode) else o
    val = Literal(ord(o_.value))
    assert isinstance(o_, str)
    if isinstance(s, Variable):
        bindings[s] = val
        yield bindings
    elif val == s:
        yield bindings
