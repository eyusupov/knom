from collections.abc import Iterator

from rdflib import Literal

from knom.typing import Bindings


def not_less_than(s: Literal, o: Literal, bindings: Bindings) -> Iterator[Bindings]:
    # TODO
    yield bindings


def not_greater_than(s: Literal, o: Literal, bindings: Bindings) -> Iterator[Bindings]:
    # TODO
    yield bindings
