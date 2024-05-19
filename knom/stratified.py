from collections.abc import Iterable
from typing import cast

from rdflib import BNode, Graph, URIRef, Variable
from rdflib.graph import ConjunctiveGraph, QuotedGraph
from rdflib.namespace import NamespaceManager
from rdflib.term import Node

from knom import (
    LOG,
    get_body,
    get_head,
    single_pass,
    single_rule,
)
from knom.typing import Bindings, Triple
from knom.util import add_triples, only_one

Rule = tuple[QuotedGraph, URIRef, QuotedGraph | Variable]
RuleIndex = dict[Rule, int]
RulesDependencies = dict[Rule, set[Rule]]

NEGATION_PREDICATE = LOG.notIncludes


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
        return not isinstance(body_node, BNode)
    assert not isinstance(body_node, Graph)
    assert not isinstance(head_node, Graph)
    return body_node == head_node


def depends(body_triple: Triple, head_triple: Triple, bnodes: Bindings) -> bool:
    return all(
        node_depends(nb, nh, bnodes)
        for nb, nh in zip(body_triple, head_triple, strict=True)
    )


def clause_dependencies(
    head: Iterable[Triple] | Variable,
    body: Iterable[Triple] | Variable,
    bnodes: Bindings | None = None,
) -> Iterable[frozenset[Triple]]:
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

    if len(complete_head) == 0:
        if len(bnodes) > 0:
            return
        else:
            yield complete_head

    body_clauses = set(body)
    while len(body_clauses) > 0:
        body_triple = body_clauses.pop()
        head_clauses = set(complete_head)
        while len(head_clauses) > 0:
            bnodes_ = bnodes.copy()
            head_triple = head_clauses.pop()
            if depends(body_triple, head_triple, bnodes_):
                yield from clause_dependencies(
                    complete_head - {head_triple},
                    complete_body - {body_triple},
                    bnodes_,
                )


def head_depends_on_body(
    head: Iterable[Triple] | Variable, body: Iterable[Triple] | Variable
) -> bool:
    try:
        next(iter(clause_dependencies(head, body)))
    except StopIteration:
        return False
    return True


def firing_rules(rule_with_head: Rule, rules_with_body: Graph) -> set[Rule]:
    head = get_head(rule_with_head)

    result = set()
    for rule_with_body in rules_with_body:
        if head_depends_on_body(head, get_body(rule_with_body)):
            result.add(rule_with_body)
    return result


def get_rules_dependencies(rules: Graph) -> RulesDependencies:
    rules_dependencies: RulesDependencies = {}
    for rule in rules:
        rules_dependencies[rule] = firing_rules(cast(Rule, rule), rules)
    return rules_dependencies


class _TarjanState:
    def __init__(self) -> None:
        self.index: dict[Rule, int] = {}
        self.low: dict[Rule, int] = {}
        self.stack: list[Rule] = []
        self.counter: int = 0

    def new_index(self) -> int:
        index = self.counter
        self.counter += 1
        return index


def stratify_rule(
    rule: Rule,
    rules_dependencies: RulesDependencies,
    state: _TarjanState,
    namespace_manager: NamespaceManager | None = None,
) -> Iterable[Graph]:
    state.index[rule] = state.new_index()
    state.low[rule] = state.index[rule]
    state.stack.append(rule)
    for firing in rules_dependencies[rule]:
        if firing not in state.index:
            yield from stratify_rule(
                firing, rules_dependencies, state, namespace_manager
            )
            state.low[rule] = min(state.low[rule], state.low[firing])
        elif firing in state.stack:
            state.low[rule] = min(state.low[firing], state.index[rule])
    if state.low[rule] == state.index[rule]:
        top = None
        scc = Graph(namespace_manager=namespace_manager)
        while top != rule:
            top = state.stack.pop()
            scc.add(top)
        yield scc


def stratify_rules(rules: Graph, rules_dependencies: RulesDependencies | None = None) -> Iterable[Graph]:
    state = _TarjanState()

    if rules_dependencies is None:
        rules_dependencies = get_rules_dependencies(rules)

    for rule in rules:
        if rule not in state.index:
            yield from stratify_rule(
                    rule, rules_dependencies, state, rules.namespace_manager
                )


def is_negative(rule: Rule) -> bool:
    return any(p == NEGATION_PREDICATE for s, p, o in get_head(rule))


def with_guard(facts: Graph, rule: Iterable[Triple]) -> Iterable[Triple]:
    if is_negative(rule):
        # TODO: can we handle negative recursive?
        raise NotImplementedError

    head = get_head(rule)
    body = get_body(rule)
    deps = set(clause_dependencies(head, body))
    if len(deps) > 1:
        raise NotImplementedError
    if len(deps) == 0:
        #yield from single_pass(facts, rules)
        raise AssertionError

    unmatched = deps.pop()
    g = Graph()
    guard = QuotedGraph(store=g.store, identifier=BNode())
    rest = QuotedGraph(store=g.store, identifier=BNode())

    add_triples(guard, unmatched)

    for triple in get_head(rule):
        if triple not in unmatched:
            rest.add(triple)

    guard_facts = Graph()
    old_inferred = Graph()
    all_inferred = ConjunctiveGraph()

    assert len(guard) > 0
    add_triples(guard_facts, single_rule(facts, (guard, LOG.implies, guard)))
    add_triples(old_inferred, single_rule(facts, (rest, LOG.implies, rest))) # Not really inferred, but still

    for _ in range(len(guard_facts) // len(guard)):
        inferred = Graph(store=all_inferred.store)
        add_triples(inferred, single_rule(guard_facts + old_inferred, rule))
        old_inferred = inferred
    yield from all_inferred


def create_positive_rule(rule: Triple) -> tuple[Rule, Rule]:
    g = Graph() # Just to create some store implicitly
    positive_head = QuotedGraph(store=g.store, identifier=BNode())
    non_negative_head = QuotedGraph(store=g.store, identifier=BNode())
    for s, p, o in get_head(rule):
        if p == NEGATION_PREDICATE:
            if isinstance(s, Graph):
                raise NotImplementedError
            assert isinstance(s, Variable | BNode)
            assert isinstance(o, Graph)
            for negative_clauses in o:
                positive_head.add(negative_clauses)
        else:
            positive_head.add((s, p, o))
            non_negative_head.add((s, p, o))

    positive_rule = (positive_head, LOG.implies, get_body(rule))
    non_negative_rule = (non_negative_head, LOG.implies, get_body(rule))

    return positive_rule, non_negative_rule


def negative_rule(facts: Graph, rule: Graph) -> Iterable[Triple]:
    positive_rule, non_negative_rule = create_positive_rule(rule)
    results = set(single_rule(facts, positive_rule))
    all_results = set(single_rule(facts, non_negative_rule))
    yield from (all_results - results)


def stratified_rule(facts: Graph, rule: Triple) -> Iterable[Triple]:
    recursive = head_depends_on_body(get_head(rule), get_body(rule))
    if recursive:
        method = with_guard
    elif is_negative(rule):
        method = negative_rule
    else:
        method = single_rule
    yield from method(facts, rule)


def _stratified(facts: Graph, rules: Graph) -> Iterable[Triple]:
    closure = ConjunctiveGraph()
    closure += facts
    rules_dependencies = get_rules_dependencies(rules)
    for i, strata in enumerate(stratify_rules(rules, rules_dependencies)):
        for rule in strata:
            print("strata", i, "rules", len(strata))
            print(strata.serialize(format="n3"))
            inferred = Graph(store=closure.store)
            add_triples(inferred, stratified_rule(closure, rule))
            yield from inferred
            print(inferred.serialize(format="n3"))


def stratified(facts: Graph, rules: Graph) -> Graph():
    g = Graph()
    return add_triples(g, _stratified(facts, rules))
