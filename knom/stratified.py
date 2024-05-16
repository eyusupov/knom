from collections.abc import Iterable
from typing import cast

from rdflib import BNode, Graph, URIRef, Variable
from rdflib.graph import QuotedGraph
from rdflib.term import Node

from knom import LOG, single_pass
from knom.typing import Triple

Rule = tuple[QuotedGraph, URIRef, QuotedGraph | Variable]
RuleIndex = dict[Rule, int]


def filter_rules(g: Graph) -> Iterable[Rule]:
    for triple in g.triples_choices((None, [LOG.implies, LOG.impliedBy], None)):
        yield cast(Rule, triple)


def node_matches(body_node: Node, head_node: Node) -> bool:
    if isinstance(body_node, BNode):
        # BNodes in body are always new
        return isinstance(head_node, BNode | Variable)
    if isinstance(body_node, Variable):
        # TODO: check if this is variable is also in the body's rule head (aka bound)
        # unbound variables seem to also produce something new
        return True
    assert not isinstance(body_node, Graph)
    assert not isinstance(head_node, Graph)
    if body_node == head_node:
        return True
    return False


def matches(body_triple: Triple, head_triple: Triple) -> bool:
    sb, pb, ob = body_triple
    sh, ph, oh = head_triple
    return node_matches(sb, sh) and node_matches(pb, ph) and node_matches(ob, oh)


def has_bnodes(triple: Triple) -> bool:
    return any(isinstance(node, BNode) for node in triple)


def head_depends_on_body(head_clauses: Graph | Variable, body_clauses: Graph | Variable) -> bool:
    assert isinstance(head_clauses, Graph)
    assert isinstance(body_clauses, Graph)

    for body_triple in body_clauses:
        bnodes_match = not has_bnodes(body_triple)
        for head_triple in head_clauses:
            if matches(body_triple, head_triple):
                if has_bnodes(body_triple):
                    # BNodes in the body always produce new variables,
                    # so for them other rules can't provide missing triples
                    bnodes_match = True
                    break
                return True
        if not bnodes_match:
            return False
    return True

def head(rule):
    s, p, o = rule
    if p == LOG.implies:
        return s
    else:
        return o


def body(rule):
    s, p, o = rule
    if p == LOG.implies:
        return o
    else:
        return s


def triggering_rules(rule_with_body: Rule, rules_with_head: Graph) -> Iterable[Rule]:
    return {
        rule
        for rule in filter_rules(rules_with_head)
        if head_depends_on_body(head(rule), body(rule_with_body))
    }


def firing_rules(rule_with_head: Rule, rules_with_body: Graph) -> Iterable[Rule]:
    return {
        rule_with_body
        for rule_with_body in filter_rules(rules_with_body)
        if head_depends_on_body(head(rule_with_head), body(rule_with_body))
    }


def last_index(index: RuleIndex) -> int:
    if index:
        return max(index.values())
    return 0


class _TarjanState:
    def __init__(self) -> None:
        self.index: dict[Rule, int] = {}
        self.low: dict[Rule,int] = {}
        self.stack: list[Rule]= []
        self.counter: int = 0

    def new_index(self) -> int:
        index = self.counter
        self.counter += 1
        return index


def stratify_rule(
    rule: Rule,
    rules: Graph,
    state: _TarjanState
) -> Iterable[Graph]:
    state.index[rule] = state.new_index()
    state.low[rule] = state.index[rule]
    state.stack.append(rule)
    for firing in firing_rules(rule, rules):
        if firing not in state.index:
            yield from stratify_rule(firing, rules, state)
            state.low[rule] = min(state.low[rule], state.low[firing])
        elif firing in state.stack:
            state.low[rule] = min(state.low[firing], state.index[rule])
    if state.low[rule] == state.index[rule]:
        top = None
        scc = Graph(namespace_manager=rules.namespace_manager)
        while top != rule:
            top = state.stack.pop()
            scc.add(top)
        yield scc


def stratify_rules(rules: Graph) -> Iterable[Graph]:
    stratified_rules: list[Graph] = []
    state = _TarjanState()
    for rule in filter_rules(rules):
        if rule not in state.index:
            stratified_rules.extend(stratify_rule(rule, rules, state))
    return stratified_rules


def stratified(facts: Graph, rules: Graph) -> Iterable[Triple]:
    stratas = stratify_rules(rules)
    feed = Graph()
    for triple in facts:
        feed.add(triple)
    for i, strata in enumerate(stratas):
        print("pass ", i)
        for new_tuple in single_pass(feed, strata):
            yield new_tuple
            feed.add(new_tuple)
