from rdflib import Variable, BNode, Graph


def is_var(node):
    return isinstance(node, Variable)


def is_bnode(node):
    return isinstance(node, BNode)


def is_graph(node):
    return isinstance(node, Graph)
