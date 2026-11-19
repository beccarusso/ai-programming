"""
test_agent.py - Deterministic tests for the Campus Resource Assistant tool.

These tests call get_campus_resource_info directly. There is no LLM, no
network and no API key involved, so the same input always gives the same
output.

Run with:  python -m pytest test_agent.py -v
or:        python test_agent.py
"""

from agent import get_campus_resource_info


def test_library_lookup():
    result = get_campus_resource_info("library")
    assert result["status"] == "success"
    assert result["name"] == "Library (Hultquist Library)"


def test_tutoring_alias():
    # "tutoring" is an alias, not the official name of the resource.
    result = get_campus_resource_info("tutoring")
    assert result["status"] == "success"
    assert result["name"] == "Learning Center (Tutoring)"


def test_case_insensitive():
    result = get_campus_resource_info("LIBRARY")
    assert result["status"] == "success"
    assert result["name"] == "Library (Hultquist Library)"


def test_resource_not_found():
    result = get_campus_resource_info("dental office")
    assert result["status"] == "error"
    assert "error_message" in result
    assert "Available resources" in result["error_message"]


def test_list_all_resources():
    result = get_campus_resource_info("all")
    assert result["status"] == "success"
    assert "available_resources" in result
    assert isinstance(result["available_resources"], list)
    assert len(result["available_resources"]) >= 4


if __name__ == "__main__":
    # Plain-Python runner for use without pytest.
    tests = [
        test_library_lookup,
        test_tutoring_alias,
        test_case_insensitive,
        test_resource_not_found,
        test_list_all_resources,
    ]
    failed = 0
    for test in tests:
        try:
            test()
            print(f"PASS  {test.__name__}")
        except AssertionError as error:
            failed += 1
            print(f"FAIL  {test.__name__}: {error}")
    print(f"\n{len(tests) - failed} of {len(tests)} tests passed")
    raise SystemExit(1 if failed else 0)
