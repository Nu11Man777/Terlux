from __future__ import annotations

from dataclasses import dataclass

from flask import current_app, session

from .catalog import Catalog, Product

SESSION_KEY = "cart"
MAX_QUANTITY = 10


@dataclass(frozen=True, slots=True)
class CartLine:
    key: str
    product: Product
    size: str
    quantity: int

    @property
    def total(self) -> int:
        return self.product.price * self.quantity


def line_key(slug: str, size: str) -> str:
    return f"{slug}|{size}"


class Cart:
    def __init__(self, catalog: Catalog):
        self._catalog = catalog
        self._items: dict[str, int] = session.get(SESSION_KEY, {})

    def _commit(self) -> None:
        session[SESSION_KEY] = self._items
        session.modified = True

    @property
    def lines(self) -> list[CartLine]:
        resolved: list[CartLine] = []
        stale: list[str] = []
        for key, quantity in self._items.items():
            slug, _, size = key.partition("|")
            product = self._catalog.get(slug)
            if product is None or size not in product.sizes:
                stale.append(key)
                continue
            resolved.append(CartLine(key=key, product=product, size=size, quantity=quantity))
        if stale:
            for key in stale:
                self._items.pop(key, None)
            self._commit()
        return resolved

    @property
    def count(self) -> int:
        return sum(self._items.values())

    @property
    def subtotal(self) -> int:
        return sum(line.total for line in self.lines)

    @property
    def shipping(self) -> int:
        subtotal = self.subtotal
        if subtotal == 0 or subtotal >= current_app.config["FREE_SHIPPING_FROM"]:
            return 0
        return current_app.config["SHIPPING_FLAT"]

    @property
    def total(self) -> int:
        return self.subtotal + self.shipping

    @property
    def tax(self) -> int:
        rate = current_app.config["TAX_RATE"]
        return round(self.total - self.total / (1 + rate))

    @property
    def missing_for_free_shipping(self) -> int:
        return max(0, current_app.config["FREE_SHIPPING_FROM"] - self.subtotal)

    @property
    def is_empty(self) -> bool:
        return not self._items

    def add(self, product: Product, size: str, quantity: int = 1) -> None:
        key = line_key(product.slug, size)
        current = self._items.get(key, 0)
        self._items[key] = min(current + quantity, MAX_QUANTITY)
        self._commit()

    def set_quantity(self, key: str, quantity: int) -> None:
        if key not in self._items:
            return
        if quantity <= 0:
            self._items.pop(key)
        else:
            self._items[key] = min(quantity, MAX_QUANTITY)
        self._commit()

    def remove(self, key: str) -> None:
        if self._items.pop(key, None) is not None:
            self._commit()

    def clear(self) -> None:
        self._items = {}
        self._commit()
