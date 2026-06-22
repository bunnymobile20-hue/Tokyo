"""
Tokyo Voice Agent — Configuration
All secrets loaded from environment only. Never printed.
"""
import os

LIVEKIT_URL = os.getenv("LIVEKIT_URL", "")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

AGENT_ENABLED = os.getenv("TOKYO_VOICE_AGENT_ENABLED", "false").lower() in ("true", "1", "yes")
AGENT_MODE = os.getenv("TOKYO_VOICE_AGENT_MODE", "safe")
AGENT_NAME = os.getenv("TOKYO_VOICE_AGENT_NAME", "Tokyo IA")
AGENT_VOICE = os.getenv("TOKYO_VOICE_AGENT_VOICE", "Charon")
AGENT_LANGUAGE = os.getenv("TOKYO_VOICE_AGENT_LANGUAGE", "pt-BR")

ROOM_STRATEGY = os.getenv("LIVEKIT_ROOM_STRATEGY", "any_room")


def is_configured():
    return bool(LIVEKIT_URL and LIVEKIT_API_KEY and LIVEKIT_API_SECRET and GEMINI_API_KEY)


def check_config():
    return {
        "livekit_url": bool(LIVEKIT_URL),
        "livekit_api_key": bool(LIVEKIT_API_KEY),
        "livekit_api_secret": bool(LIVEKIT_API_SECRET),
        "gemini_api_key": bool(GEMINI_API_KEY),
        "gemini_model": GEMINI_MODEL,
        "configured": is_configured(),
        "mode": AGENT_MODE,
        "safe_mode": AGENT_MODE == "safe",
        "voice": AGENT_VOICE,
        "language": AGENT_LANGUAGE,
    }
