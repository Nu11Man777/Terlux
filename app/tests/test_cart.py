def add(client, slug="vestido-larisa", size="M", quantity=1):
    return client.post(
        "/carrito/agregar",
        data={"slug": slug, "talla": size, "cantidad": str(quantity)},
        follow_redirects=True,
    )


def test_add_then_read_totals(client, app, catalog):
    add(client, quantity=2)
    body = client.get("/carrito").get_data(as_text=True)
    price = catalog.get("vestido-larisa").price
    assert f"{price * 2 / 100:,.2f}" in body


def test_adding_twice_merges_the_line(client):
    add(client)
    add(client)
    body = client.get("/carrito").get_data(as_text=True)
    assert body.count("vestido-larisa|M") >= 1
    assert 'value="2" selected' in body


def test_size_is_required(client):
    response = client.post("/carrito/agregar", data={"slug": "vestido-larisa"}, follow_redirects=True)
    assert "Selecciona una talla" in response.get_data(as_text=True)


def test_quantity_is_capped(client):
    add(client, quantity=50)
    assert 'value="10" selected' in client.get("/carrito").get_data(as_text=True)


def test_update_and_remove(client):
    add(client, quantity=3)
    client.post("/carrito/actualizar", data={"key": "vestido-larisa|M", "cantidad": "1"}, follow_redirects=True)
    assert 'value="1" selected' in client.get("/carrito").get_data(as_text=True)

    client.post("/carrito/eliminar", data={"key": "vestido-larisa|M"}, follow_redirects=True)
    assert "Todavía no hay nada aquí" in client.get("/carrito").get_data(as_text=True)


def test_setting_quantity_to_zero_removes_the_line(client):
    add(client)
    client.post("/carrito/actualizar", data={"key": "vestido-larisa|M", "cantidad": "0"}, follow_redirects=True)
    assert "Todavía no hay nada aquí" in client.get("/carrito").get_data(as_text=True)


def test_shipping_is_free_above_the_threshold(client, app):
    add(client, quantity=1)
    body = client.get("/carrito").get_data(as_text=True)
    assert "envío sin costo" in body.lower()


def test_shipping_is_charged_below_the_threshold(client, app):
    add(client, slug="gafas-lumen", size="Única")
    body = client.get("/carrito").get_data(as_text=True)
    assert f"{app.config['SHIPPING_FLAT'] / 100:,.2f}" in body
    assert "Te faltan" in body


def test_unknown_product_is_rejected(client):
    assert client.post("/carrito/agregar", data={"slug": "nada", "talla": "M"}).status_code == 404
