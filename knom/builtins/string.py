from collections.abc import Iterator

from rdflib import Literal, Variable, BNode
from rdflib.term import Node

from knom.typing import Bindings

def _get_cmp_args(s: Node, o: Node, bindings: Bindings) -> tuple[str, str]:
    s_ = bindings[s] if isinstance(s, Variable | BNode) else s
    o_ = bindings[o] if isinstance(o, Variable | BNode) else o
    assert isinstance(s_, Literal)
    assert isinstance(o_, Literal)
    assert isinstance(s_.value, str)
    assert isinstance(o_.value, str)
    return s_.value, o_.value


def not_less_than(s: Node, o: Node, bindings: Bindings) -> Iterator[Bindings]:
    s_, o_ = _get_cmp_args(s, o, bindings)
    if s_ >= o_:
        yield bindings


def not_greater_than(s: Node, o: Node, bindings: Bindings) -> Iterator[Bindings]:
    s_, o_ = _get_cmp_args(s, o, bindings)
    if s_ <= o_:
        yield bindings


def ord_(s: Node, o: Node, bindings: Bindings) -> Iterator[Bindings]:
    if isinstance(s, Literal) or s in bindings:
        s_ = bindings[s] if isinstance(s, Variable | BNode) else s
        if isinstance(o, Variable | BNode):
            assert isinstance(s_, Literal)
            if o in bindings:
                if chr(s.value) == bindings[o].value:
                    yield bindings
                    return
            else:
                bindings[o] = Literal(chr(s.value))
                yield bindings
                return
    o_ = bindings[o] if isinstance(o, Variable | BNode) else o
    assert isinstance(o_, Literal)
    val = Literal(ord(o_.value))
    assert isinstance(o_, str)
    if isinstance(s, Variable):
        bindings[s] = val
        yield bindings
    elif val == s:
        yield bindings
