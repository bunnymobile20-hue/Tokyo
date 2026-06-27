import os
from pydantic_settings import BaseSettings

class SiberianConfig(BaseSettings):
    SIBERIAN_API_BASE_URL: str = os.getenv("SIBERIAN_API_BASE_URL", "")
    SIBERIAN_API_TOKEN: str = os.getenv("SIBERIAN_API_TOKEN", "")
    SIBERIAN_API_MODE: str = os.getenv("SIBERIAN_API_MODE", "read_only")
    SIBERIAN_WRITE_ENABLED: bool = os.getenv("SIBERIAN_WRITE_ENABLED", "false").lower() == "true"
    SIBERIAN_TIMEOUT_SECONDS: int = int(os.getenv("SIBERIAN_TIMEOUT_SECONDS", "30"))
    SIBERIAN_VERIFY_SSL: bool = os.getenv("SIBERIAN_VERIFY_SSL", "true").lower() == "true"
    
    @property
    def is_configured(self) -> bool:
        return bool(self.SIBERIAN_API_BASE_URL) and bool(self.SIBERIAN_API_TOKEN)
        
    def safe_status(self) -> dict:
        return {
            "has_base_url": bool(self.SIBERIAN_API_BASE_URL),
            "has_token": bool(self.SIBERIAN_API_TOKEN),
            "mode": self.SIBERIAN_API_MODE,
            "write_enabled": self.SIBERIAN_WRITE_ENABLED,
            "token_masked": True
        }

settings = SiberianConfig()
