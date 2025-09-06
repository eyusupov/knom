from rdflib import URIRef

from . import generate_tests_from_manifests, run_n3_tests


def pytest_generate_tests(metafunc) -> None:  # noqa: ANN001
    generate_tests_from_manifests(
        "tests/n3/builtins-manifests.n3", metafunc
    )


def test_negative_rules(action: URIRef, result: URIRef) -> None:
    run_n3_tests(action, result)
