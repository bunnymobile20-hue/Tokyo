"""
Tokyo Voice Agent — Explicit LiveKit Agent Dispatch
Uses LiveKit Server API to dispatch agent to a specific room.
"""
import os
import logging
from datetime import datetime, timezone

logger = logging.getLogger("tokyo.agent.dispatch")

LIVEKIT_URL = os.getenv("LIVEKIT_URL", "")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "")

_last_dispatch = {"room": None, "agent_name": None, "dispatch_id": None, "status": None, "error": None, "at": None}


def check_capability():
    try:
        from livekit.api import CreateAgentDispatchRequest, LiveKitAPI
        return {"supported": True, "method": "agent_dispatch_api", "agent_name_required": True}
    except ImportError:
        return {"supported": False, "method": "not_supported", "reason": "LiveKit SDK does not support AgentDispatch"}


async def create_dispatch(room, agent_name="tokyo-agent"):
    global _last_dispatch
    if not LIVEKIT_URL or not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
        return {"success": False, "status": "not_configured", "dispatch_id": None,
                "reason": "LiveKit not configured"}

    try:
        from livekit.api import LiveKitAPI, CreateAgentDispatchRequest
        async with LiveKitAPI(LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET) as api:
            req = CreateAgentDispatchRequest(room=room, agent_name=agent_name)
            resp = await api.agent_dispatch.create_dispatch(req)

            d_id = getattr(resp, 'id', None) or getattr(resp, 'dispatch_id', None) or str(resp)
            _last_dispatch = {"room": room, "agent_name": agent_name, "dispatch_id": d_id,
                              "status": "dispatched", "error": None, "at": datetime.now(timezone.utc).isoformat()}

            logger.info(f"Agent dispatch created — room={room}, agent={agent_name}, id={d_id}")
            return {"success": True, "status": "dispatched", "dispatch_id": d_id,
                    "room": room, "agent_name": agent_name, "method": "agent_dispatch_api"}

    except Exception as e:
        _last_dispatch = {"room": room, "agent_name": agent_name, "dispatch_id": None,
                          "status": "error", "error": str(e), "at": datetime.now(timezone.utc).isoformat()}
        logger.warning(f"Agent dispatch failed — room={room}, error={str(e)}")
        return {"success": False, "status": "error", "dispatch_id": None,
                "room": room, "agent_name": agent_name, "method": "agent_dispatch_api",
                "error": str(e)[:200]}


def get_last_dispatch():
    return dict(_last_dispatch)


async def create_session_with_dispatch(identity, agent_name="tokyo-agent"):
    room = f"tokyo-voice-{__import__('uuid').uuid4().hex[:8]}"

    from livekit.api import AccessToken, VideoGrants
    token = AccessToken(api_key=LIVEKIT_API_KEY, api_secret=LIVEKIT_API_SECRET)
    token.with_identity(identity).with_name(identity)
    token.with_grants(VideoGrants(room_join=True, room=room))

    # Create agent dispatch
    dispatch_result = await create_dispatch(room, agent_name)

    ws_url = LIVEKIT_URL.replace("wss://", "").replace("ws://", "").rstrip("/")
    return {
        "success": True,
        "status": "session_ready",
        "room": room,
        "identity": identity,
        "ws_url": ws_url,
        "access_token": token.to_jwt(),
        "token_ttl_seconds": 600,
        "agent_dispatch_requested": dispatch_result["success"],
        "dispatch_status": dispatch_result["status"],
        "dispatch_method": dispatch_result["method"],
        "dispatch_id": dispatch_result.get("dispatch_id"),
        "dispatch_error": dispatch_result.get("error"),
    }
