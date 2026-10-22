from __future__ import annotations

from datetime import date
from pathlib import Path

from flask import Flask

from .cart import Cart
from .catalog import Catalog, Product
from .config import Config
from .filters import money, money_short


def create_app(config_object: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)

    catalog = Catalog(Path(app.root_path) / "data" / "catalog.json")
    app.extensions["catalog"] = catalog

    app.jinja_env.filters["money"] = money
    app.jinja_env.filters["money_short"] = money_short
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    def asset_url(product: Product, image: str | None = None) -> str:
        name = image or (product.images[0] if product.images else "")
        return "/".join(
            (
                app.config["ASSETS_BASE_URL"],
                app.config["ASSETS_BUCKET"],
                app.config["ASSETS_CATALOG_PREFIX"],
                product.slug,
                name,
            )
        )

    @app.context_processor
    def inject_globals():
        return {
            "catalog": catalog,
            "cart_count": Cart(catalog).count,
            "asset_url": asset_url,
            "free_shipping_from": app.config["FREE_SHIPPING_FROM"],
            "now_year": date.today().year,
        }

    from .views import bp

    app.register_blueprint(bp)
    return app
