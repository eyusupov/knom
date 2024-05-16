from rdflib import Literal


def notLessThan(s: Literal, o: Literal):
    assert isinstance(s.value, str)
    assert isinstance(o.value, str)
    return s.value >= o.value


def notGreaterThan(s: Literal, o: Literal):
    assert isinstance(s.value, str)
    assert isinstance(o.value, str)
    return s.value <= o.value

