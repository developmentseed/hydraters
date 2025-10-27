# hydraters

[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/developmentseed/hydraters/pr.yaml?style=for-the-badge)](https://github.com/developmentseed/hydraters/actions/workflows/pr.yaml)
[![PyPI - Version](https://img.shields.io/pypi/v/hydraters?style=for-the-badge)](https://pypi.org/project/hydraters/)

Hydrate Python dictionaries with Rust.
A general-purpose algorithm, used in [pgstac](https://github.com/stac-utils/pgstac) to reduce the size of the `items` table.

```python
import hydraters

base = {"a": "first", "b": "second", "c": {"d": "third"}}
item = {"c": {"e": "fourth", "f": "fifth"}}
result = hydraters.hydrate(base, item)
assert result == {
    "a": "first",
    "b": "second",
    "c": {"d": "third", "e": "fourth", "f": "fifth"},
}

```

If you want to clean out any lingering ``DO_NOT_MERGE_MARKER`` entries after
hydration, pass ``strip_unmatched_markers=True``. This will call
``hydraters.strip_unmatched_markers`` on the hydrated item before it is
returned and will emit the same warning when markers are stripped.

```python
import warnings
import hydraters

item = {"a": hydraters.DO_NOT_MERGE_MARKER, "b": {"c": "value"}}

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    hydraters.hydrate({}, item, strip_unmatched_markers=True)

assert item == {"b": {"c": "value"}}
```

Strip existing data back to a clean state by removing any keys whose value is
``DO_NOT_MERGE_MARKER``. A warning lists every stripped path using JSONPath
dot notation (for example ``$.assets[0].href``).

```python
item = {
    "a": hydraters.DO_NOT_MERGE_MARKER,
    "b": {"c": hydraters.DO_NOT_MERGE_MARKER, "d": 1},
}

hydraters.strip_unmatched_markers(item)
assert item == {"b": {"d": 1}}
```

## Installation

```shell
python -m pip install hydraters
```

Or, if you're using **uv**:

```shell
uv add hydraters
```

## Developing

Get [Rust](https://rustup.rs/) and [uv](https://docs.astral.sh/uv/getting-started/installation/).
Then:

```shell
git clone git@github.com:developmentseed/hydraters.git
cd hydraters
uv sync
uv run pre-commit install
```

To run tests:

```shell
uv run pytest
```

## Background

The code for this package was taken from [pypgstac](https://github.com/stac-utils/pgstac/blob/f1d71d5e00392acb970e3b19a62d5f1aa8d50cc6/src/pypgstac/src/lib.rs).
It came from some [benchmarking](https://github.com/gadomski/json-hydrate-benchmark) that determined it was much faster to do this operation in Rust than in pure Python.

## License

MIT
