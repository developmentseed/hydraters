# hydraters

[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/gadomski/hydraters/ci.yml?style=for-the-badge)](https://github.com/gadomski/hydraters/actions/workflows/ci.yml)
[![PyPI - Version](https://img.shields.io/pypi/v/hydraters?style=for-the-badge)](https://pypi.org/project/hydraters/)

Hydrate Python dictionaries with Rust.
A general-purpose algorithm, used in [pgstac](https://github.com/stac-utils/pgstac) to reduce the size of the `items` table.

```python
import hydraters

base = {"a": "first", "b": "second", "c": {"d": "third"}}
item = {"c": {"e": "fourth", "f": "fifth"}}
result = hyrdraters.hydrate(base, item)
assert result == {
    "a": "first",
    "b": "second",
    "c": {"d": "third", "e": "fourth", "f": "fifth"},
}
```

## Installation

```shell
python -m pip install hydraters
```

## Background

The code for this package was taken from [pypgstac](https://github.com/stac-utils/pgstac/blob/f1d71d5e00392acb970e3b19a62d5f1aa8d50cc6/src/pypgstac/src/lib.rs).
It came from some [benchmarking](https://github.com/gadomski/json-hydrate-benchmark) that determined it was much faster to do this operation in Rust than in pure Python.

## License

MIT
