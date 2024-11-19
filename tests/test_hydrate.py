from typing import Any

import hydraters
from hydraters import DO_NOT_MERGE_MARKER


def test_full_hydrate() -> None:
    base_item = {"a": "first", "b": "second", "c": "third"}
    dehydrated: dict[str, Any] = {}

    rehydrated = hydraters.hydrate(base_item, dehydrated)
    assert rehydrated == base_item


def test_full_nested() -> None:
    base_item = {"a": "first", "b": "second", "c": {"d": "third"}}
    dehydrated: dict[str, Any] = {}

    rehydrated = hydraters.hydrate(base_item, dehydrated)
    assert rehydrated == base_item


def test_nested_extra_keys() -> None:
    base_item = {"a": "first", "b": "second", "c": {"d": "third"}}
    dehydrated = {"c": {"e": "fourth", "f": "fifth"}}
    hydrated = hydraters.hydrate(base_item, dehydrated)

    assert hydrated == {
        "a": "first",
        "b": "second",
        "c": {"d": "third", "e": "fourth", "f": "fifth"},
    }


def test_list_of_dicts_extra_keys() -> None:
    base_item = {"a": [{"b1": 1, "b2": 2}, {"c1": 1, "c2": 2}]}
    dehydrated = {"a": [{"b3": 3}, {"c3": 3}]}

    hydrated = hydraters.hydrate(base_item, dehydrated)
    assert hydrated == {
        "a": [{"b1": 1, "b2": 2, "b3": 3}, {"c1": 1, "c2": 2, "c3": 3}],
    }


def test_equal_len_list_of_mixed_types() -> None:
    base_item = {"a": [{"b1": 1, "b2": 2}, "foo", {"c1": 1, "c2": 2}, "bar"]}
    dehydrated = {"a": [{"b3": 3}, "far", {"c3": 3}, "boo"]}

    hydrated = hydraters.hydrate(base_item, dehydrated)
    assert hydrated == {
        "a": [
            {"b1": 1, "b2": 2, "b3": 3},
            "far",
            {"c1": 1, "c2": 2, "c3": 3},
            "boo",
        ],
    }


def test_unequal_len_list() -> None:
    base_item = {"a": [{"b1": 1}, {"c1": 1}, {"d1": 1}]}
    dehydrated = {"a": [{"b1": 1, "b2": 2}, {"c1": 1, "c2": 2}]}

    hydrated = hydraters.hydrate(base_item, dehydrated)
    assert hydrated == dehydrated


def test_marked_non_merged_fields() -> None:
    base_item = {
        "a": "first",
        "b": "second",
        "c": {"d": "third", "e": "fourth"},
    }
    dehydrated = {"c": {"e": DO_NOT_MERGE_MARKER, "f": "fifth"}}

    hydrated = hydraters.hydrate(base_item, dehydrated)
    assert hydrated == {
        "a": "first",
        "b": "second",
        "c": {"d": "third", "f": "fifth"},
    }


def test_marked_non_merged_fields_in_list() -> None:
    base_item = {
        "a": [{"b": "first", "d": "third"}, {"c": "second", "e": "fourth"}],
    }
    dehydrated = {
        "a": [
            {"d": DO_NOT_MERGE_MARKER},
            {"e": DO_NOT_MERGE_MARKER, "f": "fifth"},
        ],
    }

    hydrated = hydraters.hydrate(base_item, dehydrated)
    assert hydrated == {"a": [{"b": "first"}, {"c": "second", "f": "fifth"}]}


def test_deeply_nested_dict() -> None:
    base_item = {"a": {"b": {"c": {"d": "first", "d1": "second"}}}}
    dehydrated = {"a": {"b": {"c": {"d2": "third"}}}}

    hydrated = hydraters.hydrate(base_item, dehydrated)
    assert hydrated == {
        "a": {"b": {"c": {"d": "first", "d1": "second", "d2": "third"}}},
    }


def test_equal_list_of_non_dicts() -> None:
    base_item = {"assets": {"thumbnail": {"roles": ["thumbnail"]}}}
    dehydrated = {"assets": {"thumbnail": {"href": "http://foo.com"}}}

    hydrated = hydraters.hydrate(base_item, dehydrated)
    assert hydrated == {
        "assets": {"thumbnail": {"roles": ["thumbnail"], "href": "http://foo.com"}},
    }


def test_invalid_assets_removed() -> None:
    base_item = {
        "type": "Feature",
        "assets": {
            "asset1": {"name": "Asset one"},
            "asset2": {"name": "Asset two"},
        },
    }

    dehydrated = {
        "assets": {
            "asset1": {"href": "http://foo.com"},
            "asset2": DO_NOT_MERGE_MARKER,
        },
    }

    hydrated = hydraters.hydrate(base_item, dehydrated)

    assert hydrated == {
        "type": "Feature",
        "assets": {"asset1": {"name": "Asset one", "href": "http://foo.com"}},
    }


def test_top_level_base_keys_marked() -> None:
    base_item = {
        "single": "Feature",
        "double": {"nested": "value"},
        "triple": {"nested": {"deep": "value"}},
        "included": "value",
    }

    dehydrated = {
        "single": DO_NOT_MERGE_MARKER,
        "double": DO_NOT_MERGE_MARKER,
        "triple": DO_NOT_MERGE_MARKER,
        "unique": "value",
    }

    hydrated = hydraters.hydrate(base_item, dehydrated)

    assert hydrated == {"included": "value", "unique": "value"}


def test_base_none() -> None:
    base_item = {"value": None}
    dehydrated = {"value": {"a": "b"}}
    hydrated = hydraters.hydrate(base_item, dehydrated)
    assert hydrated == {"value": {"a": "b"}}
