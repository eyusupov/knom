from collections.abc import Iterable
from typing import cast

from rdflib import BNode, Graph, URIRef, Variable
from rdflib.graph import QuotedGraph
from rdflib.term import Node

from knom import LOG, single_pass, match_rule, assign, instantiate_bnodes
from knom.typing import Triple, Bindings
from knom.util import print_rule

Rule = tuple[QuotedGraph, URIRef, QuotedGraph | Variable]
RuleIndex = dict[Rule, int]


def filter_rules(g: Graph) -> Iterable[Rule]:
    for triple in g.triples_choices((None, [LOG.implies, LOG.impliedBy], None)):
        yield cast(Rule, triple)


def node_depends(body_node: Node, head_node: Node, bnodes: Bindings) -> bool:
    if isinstance(body_node, BNode):
        if isinstance(head_node, BNode):
            if body_node not in bnodes:
                bnodes[body_node] = head_node
            return bnodes[body_node] == head_node
        return True
    if isinstance(body_node, Variable):
        # TODO: check if this is variable is also in the body's rule head (aka bound)
        # unbound variables seem to also produce something new
        return True
    if isinstance(head_node, Variable | BNode):
        # Variable in head cannot match a produced blank node
        if isinstance(body_node, BNode):
            return False
        return True
    assert not isinstance(body_node, Graph)
    assert not isinstance(head_node, Graph)
    if body_node == head_node:
        return True
    return False


def depends(body_triple: Triple, head_triple: Triple, bnodes: Bindings) -> bool:
    return all(node_depends(nb, nh, bnodes) for nb, nh in zip(body_triple, head_triple, strict=True))


def clause_dependencies(head: Iterable[Triple] | Variable, body: Iterable[Triple] | Variable, bnodes: Bindings | None = None) -> Iterable[frozenset[Triple]]:
    if bnodes is None:
        bnodes = {}
    # something => body
    # head => something2
    assert not isinstance(head, Variable)
    assert not isinstance(body, Variable)

    complete_head = frozenset(head)
    complete_body = frozenset(body)

    try:
        next(iter(body))
    except StopIteration:
        yield complete_head

    if len(complete_head) == 0 and len(bnodes) > 0:
        return

    body_clauses = set(body)
    while len(body_clauses) > 0:
        body_triple = body_clauses.pop()
        head_clauses = set(complete_head)
        while len(head_clauses) > 0:
            bnodes_ = bnodes.copy()
            head_triple = head_clauses.pop()
            if depends(body_triple, head_triple, bnodes_):
                yield from clause_dependencies(complete_head - {head_triple}, complete_body - {body_triple}, bnodes_)


def head(rule: Triple) -> Node:
    s, p, o = rule
    if p == LOG.implies:
        return s
    return o


def body(rule: Triple) -> Node:
    s, p, o = rule
    if p == LOG.implies:
        return o
    return s


def head_depends_on_body(head: Iterable[Triple] | Variable, body: Iterable[Triple] | Variable) -> bool:
    try:
        next(iter(clause_dependencies(head, body)))
    except StopIteration:
        return False
    return True


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


def with_guard(facts: Graph, rules: Iterable[Triple]) -> Iterable[Triple]:
    # TODO: the rules depend on each other, so we need to make sure
    # that each one has been executed after the one it depends on for each
    # element picked by a guard clause. Will it be enough? In what cases?
    print("executing with guard")
    for rule in rules:
        body_ = body(rule)
        deps = set(clause_dependencies(head(rule), body_))
        if len(deps) > 1:
            raise NotImplementedError
        if len(deps) == 0:
            yield from single_pass(facts, rules)
        else:
            guard = set(deps.pop())
            assert len(guard) > 0
            removed_facts = set()
            for bindings in match_rule(guard.pop(), guard, facts, {}):
                for triple in guard:
                    fact = assign(triple, bindings)
                    facts.remove(fact)
                    removed_facts.add(fact)
                instantiate_bnodes(body_, bindings)
                for triple in body_:
                    yield assign(triple, bindings)
            for fact in removed_facts:
                facts.add(fact)


def stratified(facts: Graph, rules: Graph) -> Iterable[Triple]:
    stratas = stratify_rules(rules)
    feed = Graph()
    for triple in facts:
        feed.add(triple)
    for i, strata in enumerate(stratas):
        print("strata start", i, len(strata))
        rule = next(iter(strata))
        print(strata.serialize(format='n3'))
        recursive = len(strata) > 1 or head_depends_on_body(head(rule), body(rule))
        method = with_guard if recursive else single_pass
        for new_tuple in method(feed, strata):
            yield new_tuple
            feed.add(new_tuple)
