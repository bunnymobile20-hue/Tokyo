from .config import settings

def check_health() -> dict:
    return {
        "status": "online" if settings.is_configured else "SIBERIAN_NOT_CONFIGURED",
        "mode": settings.SIBERIAN_API_MODE,
        "write_enabled": settings.SIBERIAN_WRITE_ENABLED
    }
