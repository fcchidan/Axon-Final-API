import requests

OBUMA_API_KEY='37bc03e39bdebcb7db9160d6e89474c3'
OBUMA_URL='https://api.obuma.cl/v1.0'

def obtener_productos():
    headers = {
        'content-type': 'application/json',
        'access-token': OBUMA_API_KEY,
    }

    try:
        # Solicita productos a la API
        productos_response = requests.get(f"{OBUMA_URL}/productos.list.json", headers=headers)
        productos_response.raise_for_status()  # Lanza excepción si hay error HTTP

        # Solicita categorías a la API
        categorias_response = requests.get(f"{OBUMA_URL}/productosCategorias.list.json", headers=headers)
        categorias_response.raise_for_status()

        # Extrae datos de las respuestas
        productos = productos_response.json().get('data', [])
        categorias = categorias_response.json().get('data', [])

        # Mapea categorías
        categorias_dict = {cat['producto_categoria_id']: cat['producto_categoria_nombre'] for cat in categorias}

        # Añade el nombre de la categoría a los productos
        for producto in productos:
            producto['categoria_nombre'] = categorias_dict.get(producto.get('producto_categoria'), 'Desconocida')

        return {'data': productos}
    
    except requests.exceptions.RequestException as e:
        return {'error': f'Error en la solicitud: {str(e)}'}
