from typing import Any

import hydraters
import pytest


@pytest.fixture
def base() -> dict[str, Any]:
    return {"a": "first", "b": "second", "c": "third"}


def test_equal_hydrate(base: dict[str, Any]) -> None:
    result = hydraters.hydrate(base, base)
    assert result == base


def test_full_hydrate(base: dict[str, Any]) -> None:
    result = hydraters.hydrate(base, {})
    assert result == base


def test_full_nested(base: dict[str, Any]) -> None:
    base["c"] = {"d": "third"}
    result = hydraters.hydrate(base, {})
    assert result == base


def test_nested_exta_keys(base: dict[str, Any]) -> None:
    base["c"] = {"d": "third"}
    item = {"c": {"e": "fourth", "f": "fifth"}}
    result = hydraters.hydrate(base, item)
    assert result == {
        "a": "first",
        "b": "second",
        "c": {"d": "third", "e": "fourth", "f": "fifth"},
    }


def test_list_of_dicts_extra_keys(base: dict[str, Any]) -> None:
    base = {"a": [{"b1": 1, "b2": 2}, "foo", {"c1": 1, "c2": 2}, "bar"]}
    item = {"a": [{"b3": 3}, "far", {"c3": 3}, "boo"]}
    result = hydraters.hydrate(base, item)
    assert result == {
        "a": [
            {"b1": 1, "b2": 2, "b3": 3},
            "far",
            {"c1": 1, "c2": 2, "c3": 3},
            "boo",
        ],
    }


def test_marked_non_merged_fields() -> None:
    base = {
        "a": "first",
        "b": "second",
        "c": {"d": "third", "e": "fourth"},
    }
    item = {"c": {"e": "𒍟※", "f": "fifth"}}
    result = hydraters.hydrate(base, item)
    assert result == {
        "a": "first",
        "b": "second",
        "c": {"d": "third", "f": "fifth"},
    }
