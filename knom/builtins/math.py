from collections.abc import Iterator

from rdflib import Literal

from knom.typing import Bindings


def notLessThan(s: Literal, o: Literal, bindings: Bindings) -> Iterator[Bindings]:
    # TODO
    yield bindings


def notGreaterThan(s: Literal, o: Literal, bindings: Bindings) -> Iterator[Bindings]:
    # TODO
    yield bindings
