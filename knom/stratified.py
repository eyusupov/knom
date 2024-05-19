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
from knom.util import only_one

Rule = tuple[QuotedGraph, URIRef, QuotedGraph | Variable]
RuleIndex = dict[Rule, int]

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


def last_index(index: RuleIndex) -> int:
    if index:
        return max(index.values())
    return 0


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
    rules_dependencies: dict[Rule, set[Rule]],
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


def stratify_rules(rules: Graph) -> Iterable[Graph]:
    state = _TarjanState()

    rules_dependencies: dict[Rule, set[Rule]] = {}

    for rule in rules:
        rules_dependencies[rule] = firing_rules(cast(Rule, rule), rules)

    for rule in rules:
        if rule not in state.index:
            yield from stratify_rule(
                    rule, rules_dependencies, state, rules.namespace_manager
                )


def is_negative(rule: Rule) -> bool:
    return any(p == NEGATION_PREDICATE for s, p, o in get_head(rule))


def with_guard(facts: Graph, rules: Iterable[Triple]) -> Iterable[Triple]:
    # TODO: the rules depend on each other, so we need to make sure
    # that each one has been executed after the one it depends on for each
    # element picked by a guard clause. Will it be enough? In what cases?
    for rule in rules:
        if is_negative(rule):
            raise NotImplementedError
        head = get_head(rule)
        body = get_body(rule)
        deps = set(clause_dependencies(head, body))
        if len(deps) > 1:
            raise NotImplementedError
        if len(deps) == 0:
            yield from single_pass(facts, rules)
        else:
            unmatched = deps.pop()
            g = Graph()
            guard = QuotedGraph(store=g.store, identifier=BNode())
            rest = QuotedGraph(store=g.store, identifier=BNode())

            for triple in unmatched:
                guard.add(triple)

            for triple in get_head(rule):
                if triple not in unmatched:
                    rest.add(triple)

            assert len(guard) > 0
            guard_facts = Graph()
            old_inferred = Graph()
            for fact in single_rule((guard, LOG.implies, guard), facts):
                guard_facts.add(fact)

            for fact in single_rule((rest, LOG.implies, rest), facts):
                old_inferred.add(fact) # Not really inferred

            all_inferred = ConjunctiveGraph()
            for _ in range(len(guard_facts) // len(guard)):
                inferred = Graph(store=all_inferred.store)
                for fact in single_rule(rule, guard_facts + old_inferred):
                    inferred.add(fact)
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


def negative_rules(facts: Graph, rules: Graph) -> Iterable[Triple]:
    rule = only_one(rules)
    positive_rule, non_negative_rule = create_positive_rule(rule)
    results = set(single_rule(positive_rule, facts))
    all_results = set(single_rule(non_negative_rule, facts))
    yield from (all_results - results)


def stratified(facts: Graph, rules: Graph) -> Graph:
    closure = ConjunctiveGraph()
    closure += facts
    inferred = Graph(store=closure.store)
    for strata in stratify_rules(rules):
        rule = next(iter(strata))
        recursive = len(strata) > 1 or head_depends_on_body(get_head(rule), get_body(rule))
        if is_negative(rule) and len(strata) == 1:
            method = negative_rules
        else:
            method = with_guard if recursive else single_pass

        # We don't add to inferred directly because then
        # new facts will be available in the same strata due
        # to yields, and we don't need that (maybe we don't care though if we do)
        new_inferred = Graph()
        for new_triple in method(closure, strata):
            new_inferred.add(new_triple)
        inferred += new_inferred
    return inferred
