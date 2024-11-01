import logging
from collections.abc import Iterable
from typing import cast

from rdflib import BNode, Graph, Variable
from rdflib.graph import ConjunctiveGraph, QuotedGraph
from rdflib.namespace import NamespaceManager
from rdflib.term import Node

from knom import (
    single_rule,
)
from knom.builtins import BUILTINS
from knom.typing import Bindings, Rule, RulesDependencies, Triple
from knom.util import LOG, add_triples, get_body, get_head

logger = logging.getLogger(__name__)

NEGATION_PREDICATE = LOG.notIncludes


def node_depends(body_node: Node, head_node: Node, bnodes: Bindings) -> bool:
    if isinstance(body_node, BNode):
        if isinstance(head_node, BNode):
            if body_node not in bnodes:
                bnodes[body_node] = head_node
            return bnodes[body_node] == head_node
        return False
    if isinstance(body_node, Variable):
        # TODO: check if this is variable is also in the body's rule head (aka bound)
        # unbound variables seem to also produce something new
        return True
    if isinstance(head_node, Variable | BNode):
        # Variable in head cannot match a produced blank node
        return not isinstance(body_node, BNode)
    return body_node == head_node


def depends(body_triple: Triple, head_triple: Triple, bnodes: Bindings) -> bool:
    if isinstance(head_triple, Variable | BNode):
        return True
    return body_triple[1] not in BUILTINS and \
        head_triple[1] not in BUILTINS and \
        all(
            node_depends(nb, nh, bnodes)
            for nb, nh in zip(body_triple, head_triple, strict=True)
        )


def clause_dependencies(
    head: Iterable[Triple] | Variable | BNode,
    body: Iterable[Triple] | Variable | BNode,
    bnodes: Bindings | None = None,
) -> Iterable[frozenset[Triple]]:
    if bnodes is None:
        bnodes = {}

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

    if isinstance(body, Variable):
        return body

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
) -> Iterable[list[Rule]]:
    state.index[rule] = state.new_index()
    state.low[rule] = state.index[rule]
    state.stack.append(rule)
    for firing in rules_dependencies[rule]:
        if firing not in state.low:
            yield from stratify_rule(
                firing, rules_dependencies, state, namespace_manager
            )
            state.low[rule] = min(state.low[rule], state.low[firing])
        elif firing in state.stack:
            state.low[rule] = min(state.low[rule], state.index[firing])
    if state.low[rule] == state.index[rule]:
        top = None
        scc: list[Rule] = []
        while top != rule:
            top = state.stack.pop()
            scc.append(top)
        yield scc


def stratify_rules(rules: Graph, rules_dependencies: RulesDependencies | None = None) -> Iterable[Graph]:
    state = _TarjanState()

    if rules_dependencies is None:
        rules_dependencies = get_rules_dependencies(rules)

    for rule in rules:
        if rule not in state.index:
            yield from stratify_rule(
                        rule, rules_dependencies, state, rules.namespace_manager)


def is_negative(rule: Rule) -> bool:
    head  = get_head(rule)
    if isinstance(head, Graph):
        return any(p == NEGATION_PREDICATE for s, p, o in head)
    return False


def get_guard(rule1: Rule, rule2: Rule) -> tuple[Graph, Graph]:
    head = get_head(rule1)
    body = get_body(rule2)
    deps = set(clause_dependencies(head, body))
    if len(deps) > 1:
        raise NotImplementedError
    if len(deps) == 0:
        raise AssertionError

    unmatched = deps.pop()
    g = Graph()
    guard = QuotedGraph(store=g.store, identifier=BNode())
    rest = QuotedGraph(store=g.store, identifier=BNode())

    for triple in unmatched:
        if triple[1] not in BUILTINS:
            guard.add(triple)

    for triple in head:
        if triple not in unmatched:
            rest.add(triple)
    return guard, rest


def with_guard(facts: Graph, rule: Rule) -> Iterable[Triple]:
    guard, rest = get_guard(rule, rule)

    guard_facts = Graph()
    old_inferred = Graph()
    all_inferred = ConjunctiveGraph()

    assert len(guard) > 0
    logger.debug("querying guard")
    add_triples(guard_facts, single_rule(facts, (guard, LOG.implies, guard)))
    # Guard facts miss the first elements (queried in next line),
    # so the consecutive recursions will not recreate new nodes once more
    logger.debug("querying rest")
    add_triples(old_inferred, single_rule(facts, (rest, LOG.implies, rest))) # Not really inferred, but still

    logger.debug("guard facts")
    logger.debug(guard_facts.serialize(format="n3"))

    for i in range(len(guard_facts) // len(guard)):
        inferred = Graph()
        logger.debug("round %i %i %i", i, len(guard_facts), len(old_inferred))
        logger.debug("old inferred")
        logger.debug(old_inferred.serialize(format="n3"))
        add_triples(inferred, single_rule(guard_facts + old_inferred, rule))
        old_len = len(all_inferred)
        all_inferred += inferred
        if old_len == len(all_inferred):
            break
        old_inferred = inferred
    yield from all_inferred


def create_positive_rule(rule: Rule) -> tuple[Rule, Rule]:
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


def negative_rule(facts: Graph, rule: Rule) -> Iterable[Triple]:
    positive_rule, non_negative_rule = create_positive_rule(rule)

    rules_dependencies: RulesDependencies = {
        positive_rule: set(),
        non_negative_rule: set()
    }
    if head_depends_on_body(get_head(positive_rule), get_body(positive_rule)):
        rules_dependencies[positive_rule].add(positive_rule)

    results = set(stratified_rule(facts, positive_rule, rules_dependencies))

    if head_depends_on_body(get_head(non_negative_rule), get_body(non_negative_rule)):
        rules_dependencies[non_negative_rule].add(non_negative_rule)
    all_results = set(stratified_rule(facts, non_negative_rule, rules_dependencies))
    yield from all_results - results


def stratified_rule(facts: Graph, rule: Triple, rules_dependencies: RulesDependencies) -> Iterable[Triple]:
    recursive = rule in rules_dependencies[rule]
    has_bnodes = any(isinstance(n, BNode) for triple in get_body(rule) for n in triple)
    if is_negative(rule):
        method = negative_rule
    elif len(get_head(rule)) > 0 and recursive and has_bnodes:
        method = with_guard
    else:
        method = single_rule
    logger.debug("using %s", method)
    yield from method(facts, rule)


def walk(facts: Graph, strata: list[Rule], triggered_rules: RulesDependencies) -> Iterable[Triple]:
    rules = strata.copy()
    all_inferred = ConjunctiveGraph()
    while len(rules) > 0:
        rule = rules.pop(0)
        new_inferred = Graph(namespace_manager=facts.namespace_manager)
        add_triples(new_inferred, stratified_rule(facts + all_inferred, rule, triggered_rules))
        logger.debug("inferred")
        logger.debug(new_inferred.serialize(format="n3"))
        old_len = len(all_inferred)
        all_inferred += new_inferred
        if len(all_inferred) == old_len:
            continue
        for triggered in triggered_rules[rule]:
            if triggered not in strata:
                continue
            if triggered in rules:
                rules.remove(triggered)
            rules.insert(0, triggered)
    yield from all_inferred


def _stratified(facts: Graph, rules: Graph) -> Iterable[Triple]:
    closure = ConjunctiveGraph()
    closure += facts # TODO: avoid copying facts, important for real life scenarios
    rules_dependencies = get_rules_dependencies(rules)

    triggered_rules: RulesDependencies = {}
    for rule, firing_rules in rules_dependencies.items():
        for firing_rule in firing_rules:
            if firing_rule not in triggered_rules:
                triggered_rules[firing_rule] = set()
            triggered_rules[firing_rule].add(rule)

    for i, strata in enumerate(stratify_rules(rules, rules_dependencies)):
        logger.debug("strata %i rules %i", i, len(strata))
        g = Graph(namespace_manager=rules.namespace_manager)
        add_triples(g, strata)
        logger.debug(g.serialize(format="n3"))

        new_inferred = Graph(namespace_manager=facts.namespace_manager)
        if len(strata) > 1:
            add_triples(new_inferred, walk(closure, strata, triggered_rules))
        else:
            add_triples(new_inferred, stratified_rule(closure, next(iter(strata)), rules_dependencies))
        yield from new_inferred
        closure += new_inferred
        logger.debug("inferred")
        logger.debug(new_inferred.serialize(format="n3"))


def stratified(facts: Graph, rules: Graph) -> Graph:
    g = Graph(namespace_manager=facts.namespace_manager)
    return add_triples(g, _stratified(facts, rules))
