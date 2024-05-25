from collections.abc import Iterator

from rdflib import Literal
from rdflib.term import Node

from knom.typing import Bindings

from .util import _get_cmp_args


def not_less_than(s: Literal, o: Literal, bindings: Bindings) -> Iterator[Bindings]:
    # TODO
    yield bindings


def not_greater_than(s: Literal, o: Literal, bindings: Bindings) -> Iterator[Bindings]:
    # TODO
    yield bindings


def greater_than(s: Node, o: Node, bindings: Bindings) -> Iterator[Bindings]:
    s_, o_ = _get_cmp_args(s, o, bindings)
    if s_ is None or o_ is None:
        return
    if s_ > o_:
        yield bindings
