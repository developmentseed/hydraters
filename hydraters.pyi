from typing import Any

DO_NOT_MERGE_MARKER: str
"""The magic marker that is used to indicate that a field should not be merged."""

def hydrate(base: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    """Hydrates an item using a base.

    Args:
        base:
            The base item to use for hydration. Any values on the base that are
            not on the item will be added back to the item.
        item:
            The item to hydrate. The item is mutated in-place and also returned.

    Returns:
        The hydrated item.
    """

def dehydrate(base: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    """Dehydrates an item using a base.

    Args:
        base:
            The base item to use for dehydration. Any values that are equal on
            the base and the itm will be removed from the item.
        item:
            The item to be dehydrated. The item is mutated in-place, and also
            returned.

    Returns:
        The dehydrated item.
    """
