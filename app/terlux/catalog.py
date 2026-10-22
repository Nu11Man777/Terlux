from __future__ import annotations

import json
import unicodedata
from dataclasses import dataclass
from pathlib import Path

SORTS = {
    "destacados": "Destacados",
    "novedades": "Novedades",
    "precio-asc": "Precio: menor a mayor",
    "precio-desc": "Precio: mayor a menor",
    "nombre": "Nombre A–Z",
}


def fold(value: str) -> str:
    stripped = unicodedata.normalize("NFD", value.casefold())
    return "".join(c for c in stripped if unicodedata.category(c) != "Mn")


@dataclass(frozen=True, slots=True)
class Color:
    name: str
    hex: str


@dataclass(frozen=True, slots=True)
class Taxon:
    slug: str
    name: str
    tagline: str = ""


@dataclass(frozen=True, slots=True)
class Product:
    slug: str
    name: str
    line: str
    category: str
    price: int
    compare_at: int | None
    sizes: tuple[str, ...]
    colors: tuple[Color, ...]
    summary: str
    description: str
    materials: str
    care: str
    badge: str | None
    featured: bool
    images: tuple[str, ...]
    index: int

    @property
    def on_sale(self) -> bool:
        return self.compare_at is not None and self.compare_at > self.price

    @property
    def discount(self) -> int:
        if not self.on_sale:
            return 0
        return round((1 - self.price / self.compare_at) * 100)

    @property
    def one_size(self) -> bool:
        return len(self.sizes) == 1


class Catalog:
    def __init__(self, path: Path):
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        self.lines = tuple(Taxon(**item) for item in raw["lines"])
        self.categories = tuple(Taxon(**item) for item in raw["categories"])
        self.products = tuple(
            Product(
                slug=item["slug"],
                name=item["name"],
                line=item["line"],
                category=item["category"],
                price=item["price"],
                compare_at=item["compare_at"],
                sizes=tuple(item["sizes"]),
                colors=tuple(Color(**c) for c in item["colors"]),
                summary=item["summary"],
                description=item["description"],
                materials=item["materials"],
                care=item["care"],
                badge=item["badge"],
                featured=item["featured"],
                images=tuple(item["images"]),
                index=position,
            )
            for position, item in enumerate(raw["products"])
        )
        self._by_slug = {p.slug: p for p in self.products}
        self._lines_by_slug = {t.slug: t for t in self.lines}
        self._categories_by_slug = {t.slug: t for t in self.categories}
        self._haystack = {
            p.slug: fold(" ".join((p.name, p.summary, p.line, p.category, *(c.name for c in p.colors))))
            for p in self.products
        }

    def get(self, slug: str) -> Product | None:
        return self._by_slug.get(slug)

    def line(self, slug: str) -> Taxon | None:
        return self._lines_by_slug.get(slug)

    def category(self, slug: str) -> Taxon | None:
        return self._categories_by_slug.get(slug)

    def categories_for(self, line: str | None) -> tuple[Taxon, ...]:
        present = {p.category for p in self.products if line is None or p.line == line}
        return tuple(t for t in self.categories if t.slug in present)

    def sizes_for(self, line: str | None) -> tuple[str, ...]:
        found: list[str] = []
        for product in self.products:
            if line and product.line != line:
                continue
            for size in product.sizes:
                if size not in found:
                    found.append(size)
        return tuple(found)

    def search(
        self,
        *,
        line: str | None = None,
        category: str | None = None,
        size: str | None = None,
        sale: bool = False,
        query: str = "",
        sort: str = "destacados",
    ) -> tuple[Product, ...]:
        needle = fold(query.strip())
        found = [
            p
            for p in self.products
            if (line is None or p.line == line)
            and (category is None or p.category == category)
            and (size is None or size in p.sizes)
            and (not sale or p.on_sale)
            and (not needle or all(word in self._haystack[p.slug] for word in needle.split()))
        ]
        return tuple(sorted(found, key=self._sort_key(sort)))

    @staticmethod
    def _sort_key(sort: str):
        keys = {
            "precio-asc": lambda p: (p.price, p.index),
            "precio-desc": lambda p: (-p.price, p.index),
            "nombre": lambda p: (fold(p.name), p.index),
            "novedades": lambda p: (p.badge != "Nuevo", p.index),
        }
        return keys.get(sort, lambda p: (not p.featured, p.index))

    def featured(self, limit: int = 8) -> tuple[Product, ...]:
        picks = [p for p in self.products if p.featured]
        return tuple(picks[:limit])

    def related(self, product: Product, limit: int = 4) -> tuple[Product, ...]:
        same = [p for p in self.products if p.category == product.category and p.slug != product.slug]
        if len(same) < limit:
            same += [p for p in self.products if p.line == product.line and p not in same and p.slug != product.slug]
        return tuple(same[:limit])
