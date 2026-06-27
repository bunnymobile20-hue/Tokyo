import httpx
from .config import settings
from .policy import validate_request_intent, SiberianPolicyError

class SiberianClient:
    def __init__(self):
        self.base_url = settings.SIBERIAN_API_BASE_URL.rstrip('/')
        self.token = settings.SIBERIAN_API_TOKEN
        
    async def request(self, method: str, endpoint: str, **kwargs) -> dict:
        if not settings.is_configured:
            raise Exception("SIBERIAN_NOT_CONFIGURED")
            
        validate_request_intent(method, endpoint)
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.token}"
        headers["Accept"] = "application/json"
        
        timeout = kwargs.pop("timeout", settings.SIBERIAN_TIMEOUT_SECONDS)
        verify = settings.SIBERIAN_VERIFY_SSL
        
        async with httpx.AsyncClient(verify=verify, timeout=timeout) as client:
            # Em modo 'read_only' bloqueamos preventivamente qualquer body
            # que normalmente acompanha métodos de escrita, embora o policy 
            # já tenha bloqueado os verbos.
            if "json" in kwargs:
                del kwargs["json"]
            if "data" in kwargs:
                del kwargs["data"]
                
            response = await client.request(method, url, headers=headers, **kwargs)
            
            # Aqui trataríamos os status HTTP do ERP de forma segura
            if response.status_code == 404:
                return {}
                
            response.raise_for_status()
            
            try:
                return response.json()
            except Exception:
                return {"text_response": response.text[:500]}
                
siberian_client = SiberianClient()
