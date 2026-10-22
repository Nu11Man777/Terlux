# Terlux — tienda en línea

Tienda de ropa y accesorios en Flask y Jinja2. Cubre el catálogo con filtros, el detalle de producto
y la bolsa de compra. El pago en línea todavía no está integrado.

Los estilos se compilan con Tailwind CSS a una hoja estática y las tipografías se sirven desde la
propia aplicación, de modo que el sitio no depende de ninguna CDN en tiempo de ejecución.

Las piezas se definen en `app/terlux/data/catalog.json`. Las fotografías viven en el almacenamiento
de objetos y las plantillas las referencian por su URL directa, así que el navegador las pide al
servicio de almacenamiento y no a la aplicación.

## Variables de entorno

| Variable                 | Valor por omisión                    | Descripción                                  |
|--------------------------|--------------------------------------|----------------------------------------------|
| `SECRET_KEY`             | `terlux-local-development`           | Firma de la cookie de sesión                 |
| `ASSETS_BASE_URL`        | `http://assets.terlux.internal:9000` | Base desde la que el navegador pide imágenes |
| `ASSETS_BUCKET`          | `terlux-assets`                      | Bucket de activos                            |
| `ASSETS_CATALOG_PREFIX`  | `public/catalog`                     | Prefijo de las fotografías de catálogo       |
| `SHIPPING_FLAT`          | `14900`                              | Costo de envío en centavos                   |
| `FREE_SHIPPING_FROM`     | `150000`                             | Umbral de envío sin costo en centavos        |

## Estilos

La hoja compilada (`app/terlux/static/css/terlux.css`) está versionada para que la imagen de la
aplicación no necesite Node. Para regenerarla tras cambiar plantillas:

```sh
cd frontend
npm install
npm run build
```

## Pruebas

```sh
cd app
python -m pytest
```
