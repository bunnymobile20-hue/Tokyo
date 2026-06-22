"""
Tokyo Voice Agent Worker
Registers as LiveKit worker, handles dispatched jobs, connects to rooms.

Pattern matches existing agent.py — runs via livekit.agents.cli.
"""
import os
import sys
import logging
import asyncio
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, ChatContext, AutoSubscribe
from livekit.plugins import noise_cancellation, google
from tokyo_voice_agent.config import AGENT_VOICE, AGENT_MODE
from tokyo_voice_agent.gemini_realtime import AGENT_INSTRUCTION
from tokyo_voice_agent.status import update as agent_update, log_event

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tokyo.agent.worker")

# Load project prompts if available
try:
    from prompts import AGENT_INSTRUCTION as ORIG_INSTRUCTION, SESSION_INSTRUCTION
    instruction = ORIG_INSTRUCTION + "\n\n# Modo Seguro\nVoce esta em modo seguro (" + AGENT_MODE + "). Nao executa acoes reais, nao altera dados, nao conecta ERP. Responda em portugues do Brasil, de forma clara e breve."
except ImportError:
    instruction = AGENT_INSTRUCTION


class TokyoAssistant(Agent):
    def __init__(self, chat_ctx=None):
        super().__init__(
            instructions=instruction,
            llm=google.beta.realtime.RealtimeModel(
                voice=AGENT_VOICE,
                temperature=0.6,
            ),
            chat_ctx=chat_ctx,
        )


async def entrypoint(ctx: agents.JobContext):
    agent_update(worker_running=True)
    log_event("agent_worker_started", {"room": ctx.room.name if hasattr(ctx.room, 'name') else 'unknown'})

    logger.info(f"Tokyo Voice Agent starting... room={ctx.room.name if hasattr(ctx.room, 'name') else 'dispatched'}, mode={AGENT_MODE}")

    await ctx.connect()

    session = AgentSession()
    agent = TokyoAssistant()

    await session.start(
        room=ctx.room,
        agent=agent,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC() if noise_cancellation else None,
        ),
    )

    agent_update(room_joined=True, last_event="room_connected")
    log_event("agent_joined_room", {"room": ctx.room.name if hasattr(ctx.room, 'name') else 'dispatched'})

    await session.generate_reply(
        instructions=instruction + "\nCumprimente o usuario brevemente em portugues e informe que a sessao de voz esta ativa."
    )

    agent_update(last_event="gemini_response_started")
    log_event("gemini_response_completed", {})

    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass

    agent_update(worker_running=False, room_joined=False)
    log_event("agent_worker_stopped", {})


def main():
    parser = argparse.ArgumentParser(description="Tokyo Voice Agent Worker")
    parser.add_argument("--room", help="Room name (handled by LiveKit dispatch)")
    parser.add_argument("mode", nargs="?", default="start", choices=["start", "dev", "connect"],
                        help="Worker mode: start (production), dev (development), connect (specific room)")
    args, unknown = parser.parse_known_args()

    logger.info(f"Starting Tokyo Voice Agent worker... mode={AGENT_MODE}, voice={AGENT_VOICE}")
    logger.info(f"Worker will handle dispatched jobs from LiveKit server.")

    # agents.cli.run_app expects subcommands via sys.argv
    # Force the mode as the first argument
    import sys as _sys
    _sys.argv = [_sys.argv[0], args.mode] + unknown
    agents.cli.run_app(agents.WorkerOptions(
        entrypoint_fnc=entrypoint,
        agent_name="tokyo-agent",
        port=0,
    ))


if __name__ == "__main__":
    main()
