from rdflib import BNode, Literal, Variable
from rdflib.term import Node

from knom.typing import Bindings


def _get_cmp_args(s: Node, o: Node, bindings: Bindings) -> tuple:
    s_ = bindings.get(s) if isinstance(s, Variable | BNode) else s
    o_ = bindings.get(o) if isinstance(o, Variable | BNode) else o
    if s_ is None or o_ is None:
        return None, None
    assert isinstance(s_, Literal)
    assert isinstance(o_, Literal)
    #assert isinstance(s_.value, str)
    #assert isinstance(o_.value, str)
    return s_.value, o_.value
