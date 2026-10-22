from __future__ import annotations

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from .cart import Cart, line_key
from .catalog import SORTS, Catalog

bp = Blueprint("storefront", __name__)


def catalog() -> Catalog:
    return current_app.extensions["catalog"]


def _clean(name: str) -> str | None:
    value = (request.args.get(name) or "").strip()
    return value or None


RESERVED_ARGS = frozenset({"line_slug"})


def _query_args() -> dict[str, str]:
    return {key: value for key, value in request.args.items(multi=False) if key not in RESERVED_ARGS}


@bp.app_template_global()
def filter_url(**overrides):
    params = _query_args()
    for key, value in overrides.items():
        if value is None or value is False or value == "":
            params.pop(key, None)
        else:
            params[key] = value
    view_args = dict(request.view_args or {})
    return url_for(request.endpoint, **view_args, **params)


@bp.app_template_global()
def collection_url(line_slug: str | None = None):
    return url_for("storefront.collection", line_slug=line_slug, **_query_args())


@bp.get("/")
def index():
    data = catalog()
    lines_preview = [(line, data.search(line=line.slug)[0]) for line in data.lines]
    return render_template(
        "index.html",
        hero=data.get("vestido-larisa"),
        hero_small=data.get("bolso-heira"),
        lines_preview=lines_preview,
        featured=data.featured(8),
        editorial=data.search(line="hombre")[:2],
        novedades=data.search(sort="novedades")[:4],
    )


@bp.get("/catalogo")
@bp.get("/catalogo/<line_slug>")
def collection(line_slug: str | None = None):
    data = catalog()
    line = None
    if line_slug is not None:
        line = data.line(line_slug)
        if line is None:
            abort(404)

    category_slug = _clean("categoria")
    if category_slug and data.category(category_slug) is None:
        category_slug = None

    size = _clean("talla")
    query = (request.args.get("q") or "").strip()
    sale = request.args.get("oferta") == "1"
    sort = request.args.get("orden") or "destacados"
    if sort not in SORTS:
        sort = "destacados"

    products = data.search(
        line=line.slug if line else None,
        category=category_slug,
        size=size,
        sale=sale,
        query=query,
        sort=sort,
    )

    return render_template(
        "collection.html",
        line=line,
        products=products,
        categories=data.categories_for(line.slug if line else None),
        sizes=data.sizes_for(line.slug if line else None),
        active={"categoria": category_slug, "talla": size, "q": query, "oferta": sale, "orden": sort},
        sorts=SORTS,
    )


@bp.get("/producto/<slug>")
def product(slug: str):
    data = catalog()
    item = data.get(slug)
    if item is None:
        abort(404)
    return render_template("product.html", product=item, related=data.related(item))


@bp.get("/carrito")
def cart():
    return render_template("cart.html", cart=Cart(catalog()))


@bp.post("/carrito/agregar")
def cart_add():
    data = catalog()
    item = data.get(request.form.get("slug", ""))
    if item is None:
        abort(404)

    size = request.form.get("talla", "")
    if size not in item.sizes:
        flash("Selecciona una talla para continuar.", "error")
        return redirect(url_for("storefront.product", slug=item.slug))

    try:
        quantity = max(1, int(request.form.get("cantidad", 1)))
    except ValueError:
        quantity = 1

    Cart(data).add(item, size, quantity)
    flash(f"{item.name} · talla {size} se agregó a tu bolsa.", "success")
    return redirect(request.form.get("next") or url_for("storefront.cart"))


@bp.post("/carrito/actualizar")
def cart_update():
    try:
        quantity = int(request.form.get("cantidad", 1))
    except ValueError:
        quantity = 1
    Cart(catalog()).set_quantity(request.form.get("key", ""), quantity)
    return redirect(url_for("storefront.cart"))


@bp.post("/carrito/eliminar")
def cart_remove():
    Cart(catalog()).remove(request.form.get("key", ""))
    flash("Se eliminó la pieza de tu bolsa.", "success")
    return redirect(url_for("storefront.cart"))


@bp.get("/buscar")
def search():
    return redirect(url_for("storefront.collection", q=request.args.get("q", "")))


@bp.get("/paginas/<slug>")
def page(slug: str):
    pages = {
        "envios": "Envíos y entregas",
        "devoluciones": "Cambios y devoluciones",
        "contacto": "Contacto",
        "tiendas": "Tiendas",
    }
    if slug not in pages:
        abort(404)
    return render_template(f"pages/{slug}.html", title=pages[slug])


@bp.get("/healthz")
def healthz():
    return {"status": "ok", "products": len(catalog().products)}


@bp.app_errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404
