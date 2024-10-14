from rdflib import URIRef

from . import generate_tests_from_manifests, run_n3_tests

MANIFEST_PATH = "tests/n3/scoping-manifests.n3"


def pytest_generate_tests(metafunc) -> None:  # noqa: ANN001
    generate_tests_from_manifests(MANIFEST_PATH, metafunc)


def test_scoping(action: URIRef, result: URIRef) -> None:
    run_n3_tests(action, result)
