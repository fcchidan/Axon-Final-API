import requests_cache

def setup_cache():
    """
    Configura el caché para almacenar respuestas de la API.
    """
    # Instala el caché usando SQLite con expiración de 30 minutos
    requests_cache.install_cache(
        cache_name='obuma_cache',  # Nombre del archivo SQLite que almacenará el caché
        backend='sqlite',         # Backend para el caché (SQLite)
        expire_after=1800         # Tiempo de expiración del caché en segundos (30 minutos)
    )
