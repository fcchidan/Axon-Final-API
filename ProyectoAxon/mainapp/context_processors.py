# mainapp/context_processors.py

from .views import obtener_categorias  # Asegúrate de importar la función

def categorias_processor(request):
    categorias = obtener_categorias()
    if 'data' in categorias and categorias['data']:
        return {'categorias': categorias['data']}
    return {'categorias': []}
