from .client import siberian_client
from .schemas import build_response, not_configured_response
from .config import settings

async def discover_endpoints():
    if not settings.is_configured:
        return not_configured_response("discovery")
        
    # Discovery passivo - apenas avalia o / (ou /api) via GET ou HEAD
    # O ERP Siberian normalmente deve ter um endpoint /status ou raiz para discovery
    try:
        data = await siberian_client.request("GET", "api/status")
        # Mascara tokens se vierem acidentalmente
        return build_response("real_data", safe_to_display=True, data=data, endpoint="discovery")
    except Exception as e:
        if str(e) == "SIBERIAN_NOT_CONFIGURED":
            return not_configured_response("discovery")
        return build_response("error", safe_to_display=True, data={"error": str(e)}, endpoint="discovery")
