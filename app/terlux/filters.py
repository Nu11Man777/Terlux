from __future__ import annotations


def money(cents: int | None) -> str:
    if cents is None:
        return ""
    return f"${cents / 100:,.2f}"


def money_short(cents: int | None) -> str:
    if cents is None:
        return ""
    return f"${cents / 100:,.0f}"
