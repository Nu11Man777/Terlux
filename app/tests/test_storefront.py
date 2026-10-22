import pytest


@pytest.mark.parametrize(
    "path",
    ["/", "/catalogo", "/catalogo/mujer", "/catalogo/hombre", "/catalogo/accesorios",
     "/producto/vestido-larisa", "/carrito", "/healthz",
     "/paginas/envios", "/paginas/devoluciones", "/paginas/tiendas", "/paginas/contacto"],
)
def test_pages_render(client, path):
    assert client.get(path).status_code == 200


@pytest.mark.parametrize("path", ["/catalogo/inexistente", "/producto/inexistente", "/paginas/inexistente"])
def test_unknown_resources_return_404(client, path):
    assert client.get(path).status_code == 404


def test_images_point_at_the_object_storage(client, app):
    body = client.get("/producto/vestido-larisa").get_data(as_text=True)
    expected = f"{app.config['ASSETS_BASE_URL']}/{app.config['ASSETS_BUCKET']}/public/catalog/vestido-larisa/"
    assert expected in body


def test_search_redirects_to_the_collection(client):
    response = client.get("/buscar?q=bolso")
    assert response.status_code == 302
    assert "q=bolso" in response.headers["Location"]


def test_invalid_sort_falls_back(client):
    assert client.get("/catalogo?orden=inventado").status_code == 200


@pytest.mark.parametrize("path", ["/catalogo/mujer?line_slug=hombre", "/catalogo?line_slug=hombre", "/catalogo?categoria=<script>"])
def test_hostile_query_parameters_do_not_break_url_building(client, path):
    assert client.get(path).status_code == 200
