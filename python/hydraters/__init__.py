from __future__ import annotations

from typing import Any

from . import hydraters as _rust_module
from .hydraters import (
    DO_NOT_MERGE_MARKER,
    dehydrate,
    hydrate as _hydrate_impl,
    strip_merge_markers as _strip_merge_markers,
)

__all__ = [
    "DO_NOT_MERGE_MARKER",
    "dehydrate",
    "hydrate",
    "strip_merge_markers",
]

__doc__ = _rust_module.__doc__

strip_merge_markers = _strip_merge_markers


def hydrate(
    base: dict[str, Any],
    item: dict[str, Any],
    *,
    strip_merge_markers: bool = False,
) -> dict[str, Any]:
    """Hydrate ``item`` using ``base`` and optionally strip remaining markers.

    Args:
        base: Hydration base to merge from.
        item: Item mutated in-place and also returned.
        strip_merge_markers: When ``True`` call :func:`strip_merge_markers` on
            the hydrated item before returning.

    Returns:
        The hydrated item (identical object as ``item``).
    """

    result = _hydrate_impl(base, item)
    if strip_merge_markers:
        _strip_merge_markers(result)
    return result
