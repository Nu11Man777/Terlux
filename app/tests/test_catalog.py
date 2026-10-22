import pytest


def test_every_product_has_images_and_sizes(catalog):
    for product in catalog.products:
        assert product.images, product.slug
        assert product.sizes, product.slug
        assert product.price > 0


def test_lines_and_categories_are_known(catalog):
    lines = {line.slug for line in catalog.lines}
    categories = {category.slug for category in catalog.categories}
    for product in catalog.products:
        assert product.line in lines
        assert product.category in categories


def test_search_filters_combine(catalog):
    found = catalog.search(line="mujer", category="calzado", size="24")
    assert found
    assert all(p.line == "mujer" and p.category == "calzado" and "24" in p.sizes for p in found)


def test_search_ignores_accents_and_case(catalog):
    assert catalog.search(query="zapatilla aurea") == catalog.search(query="Zapatilla Áurea")


def test_sorting_by_price(catalog):
    prices = [p.price for p in catalog.search(sort="precio-asc")]
    assert prices == sorted(prices)


def test_sale_products_report_a_discount(catalog):
    on_sale = catalog.search(sale=True)
    assert on_sale
    assert all(p.compare_at > p.price and 0 < p.discount < 100 for p in on_sale)


def test_related_excludes_itself(catalog):
    product = catalog.get("vestido-larisa")
    assert product.slug not in {p.slug for p in catalog.related(product)}


@pytest.mark.parametrize("slug", ["vestido-larisa", "gafas-noir", "camisa-nilo"])
def test_known_slugs_resolve(catalog, slug):
    assert catalog.get(slug) is not None
