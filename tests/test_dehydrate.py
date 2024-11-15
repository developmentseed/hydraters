import hydraters
from hydraters import DO_NOT_MERGE_MARKER


def test_single_depth_equals() -> None:
    base_item = {"a": "first", "b": "second", "c": "third"}
    item = {"a": "first", "b": "second", "c": "third"}
    dehydrated = hydraters.dehydrate(base_item, item)
    assert dehydrated == {}


def test_nested_equals() -> None:
    base_item = {"a": "first", "b": "second", "c": {"d": "third"}}
    item = {"a": "first", "b": "second", "c": {"d": "third"}}
    dehydrated = hydraters.dehydrate(base_item, item)
    assert dehydrated == {}


def test_nested_extra_keys() -> None:
    base_item = {"a": "first", "b": "second", "c": {"d": "third"}}
    item = {
        "a": "first",
        "b": "second",
        "c": {"d": "third", "e": "fourth", "f": "fifth"},
    }
    dehydrated = hydraters.dehydrate(base_item, item)
    assert dehydrated == {"c": {"e": "fourth", "f": "fifth"}}


def test_list_of_dicts_extra_keys() -> None:
    base_item = {"a": [{"b1": 1, "b2": 2}, {"c1": 1, "c2": 2}]}
    item = {"a": [{"b1": 1, "b2": 2, "b3": 3}, {"c1": 1, "c2": 2, "c3": 3}]}

    dehydrated = hydraters.dehydrate(base_item, item)
    assert "a" in dehydrated
    assert dehydrated["a"] == [{"b3": 3}, {"c3": 3}]


def test_equal_len_list_of_mixed_types() -> None:
    base_item = {"a": [{"b1": 1, "b2": 2}, "foo", {"c1": 1, "c2": 2}, "bar"]}
    item = {
        "a": [
            {"b1": 1, "b2": 2, "b3": 3},
            "far",
            {"c1": 1, "c2": 2, "c3": 3},
            "boo",
        ],
    }

    dehydrated = hydraters.dehydrate(base_item, item)
    assert "a" in dehydrated
    assert dehydrated["a"] == [{"b3": 3}, "far", {"c3": 3}, "boo"]


def test_unequal_len_list() -> None:
    """Test that unequal length lists preserve the item value exactly."""
    base_item = {"a": [{"b1": 1}, {"c1": 1}, {"d1": 1}]}
    item = {"a": [{"b1": 1, "b2": 2}, {"c1": 1, "c2": 2}]}

    dehydrated = hydraters.dehydrate(base_item, item)
    assert "a" in dehydrated
    assert dehydrated["a"] == item["a"]


def test_marked_non_merged_fields() -> None:
    base_item = {"a": "first", "b": "second", "c": {"d": "third", "e": "fourth"}}
    item = {
        "a": "first",
        "b": "second",
        "c": {"d": "third", "f": "fifth"},
    }
    dehydrated = hydraters.dehydrate(base_item, item)
    assert dehydrated == {"c": {"e": DO_NOT_MERGE_MARKER, "f": "fifth"}}


def test_marked_non_merged_fields_in_list() -> None:
    base_item = {
        "a": [{"b": "first", "d": "third"}, {"c": "second", "e": "fourth"}],
    }
    item = {"a": [{"b": "first"}, {"c": "second", "f": "fifth"}]}

    dehydrated = hydraters.dehydrate(base_item, item)
    assert dehydrated == {
        "a": [
            {"d": DO_NOT_MERGE_MARKER},
            {"e": DO_NOT_MERGE_MARKER, "f": "fifth"},
        ],
    }


def test_deeply_nested_dict() -> None:
    base_item = {"a": {"b": {"c": {"d": "first", "d1": "second"}}}}
    item = {"a": {"b": {"c": {"d": "first", "d1": "second", "d2": "third"}}}}

    dehydrated = hydraters.dehydrate(base_item, item)
    assert dehydrated == {"a": {"b": {"c": {"d2": "third"}}}}


def test_equal_list_of_non_dicts() -> None:
    base_item = {"assets": {"thumbnail": {"roles": ["thumbnail"]}}}
    item = {
        "assets": {"thumbnail": {"roles": ["thumbnail"], "href": "http://foo.com"}},
    }

    dehydrated = hydraters.dehydrate(base_item, item)
    assert dehydrated == {"assets": {"thumbnail": {"href": "http://foo.com"}}}


def test_invalid_assets_marked() -> None:
    base_item = {
        "type": "Feature",
        "assets": {
            "asset1": {"name": "Asset one"},
            "asset2": {"name": "Asset two"},
        },
    }
    hydrated = {
        "assets": {"asset1": {"name": "Asset one", "href": "http://foo.com"}},
    }

    dehydrated = hydraters.dehydrate(base_item, hydrated)

    assert dehydrated == {
        "type": DO_NOT_MERGE_MARKER,
        "assets": {
            "asset1": {"href": "http://foo.com"},
            "asset2": DO_NOT_MERGE_MARKER,
        },
    }


def test_top_level_base_keys_marked() -> None:
    base_item = {
        "single": "Feature",
        "double": {"nested": "value"},
        "triple": {"nested": {"deep": "value"}},
        "included": "value",
    }
    hydrated = {"included": "value", "unique": "value"}

    dehydrated = hydraters.dehydrate(base_item, hydrated)

    assert dehydrated == {
        "single": DO_NOT_MERGE_MARKER,
        "double": DO_NOT_MERGE_MARKER,
        "triple": DO_NOT_MERGE_MARKER,
        "unique": "value",
    }
