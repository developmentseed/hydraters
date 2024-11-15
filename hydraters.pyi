from typing import Any

DO_NOT_MERGE_MARKER: str
"""The magic marker that is used to indicate that a field should not be merged."""

def hydrate(base: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    """Hydrates an item using a base."""

def dehydrate(base: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    """Dehydrates an item using a base."""
