from collections.abc import Iterator

from rdflib import Literal, Variable

from knom.typing import Bindings


def notLessThan(s: Literal, o: Literal, bindings: Bindings) -> Iterator[Bindings]:
    assert isinstance(s.value, str)
    assert isinstance(o.value, str)
    if s.value >= o.value:
        yield bindings
    else:
        return


def notGreaterThan(s: Literal, o: Literal, bindings: Bindings) -> Iterator[Bindings]:
    assert isinstance(s.value, str)
    assert isinstance(o.value, str)
    if s.value <= o.value:
        yield bindings
    else:
        return


def ord_(s: Literal, o: Literal, bindings: Bindings) -> Iterator[Bindings]:
    assert isinstance(s, Variable)
    o_ = bindings[o] if isinstance(o, Variable) else o
    assert isinstance(o_, str)
    bindings[s] = Literal(ord(o_.value))
    yield bindings
