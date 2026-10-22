from __future__ import annotations

import os


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.environ[name])
    except (KeyError, ValueError):
        return default


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "terlux-local-development")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 14

    ASSETS_BASE_URL = os.environ.get("ASSETS_BASE_URL", "http://assets.terlux.internal:9000").rstrip("/")
    ASSETS_BUCKET = os.environ.get("ASSETS_BUCKET", "terlux-assets")
    ASSETS_CATALOG_PREFIX = os.environ.get("ASSETS_CATALOG_PREFIX", "public/catalog").strip("/")

    SHIPPING_FLAT = _int_env("SHIPPING_FLAT", 14900)
    FREE_SHIPPING_FROM = _int_env("FREE_SHIPPING_FROM", 150000)
    TAX_RATE = 0.16
