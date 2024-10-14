import logging

from rdflib import URIRef

from . import (
    generate_tests_from_manifests,
    run_n3_tests,
)

logging.getLogger("knom").setLevel(logging.DEBUG)
logging.getLogger("knom.stratified").setLevel(logging.DEBUG)

def pytest_generate_tests(metafunc) -> None:  # noqa: ANN001
    generate_tests_from_manifests(
        "tests/n3/recursive-manifests.n3", metafunc
    )


def test_recursive(action: URIRef, result: URIRef) -> None:
    run_n3_tests(action, result)
