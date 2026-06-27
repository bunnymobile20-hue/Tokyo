import httpx
from .config import SERVER_URL, WORKSPACE_DIR
from .schemas import TaskMessage, TaskResult
from .logs import get_logger

logger = get_logger()

class TokyoClient:
    def __init__(self):
        self.base_url = f"{SERVER_URL}/tokyo/desktop-agent"
        
    async def register(self) -> bool:
        """Registers the agent with the server."""
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    f"{self.base_url}/register",
                    json={
                        "workspace": str(WORKSPACE_DIR),
                        "capabilities": {
                            "browser": True,
                            "file_system": True
                        }
                    },
                    timeout=5.0
                )
                res.raise_for_status()
                logger.info("Successfully registered with TokyoOS server.")
                return True
        except Exception as e:
            logger.error(f"Failed to register with server: {e}")
            return False
            
    async def heartbeat(self):
        """Sends a heartbeat to the server."""
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{self.base_url}/heartbeat",
                    json={"status": "online"},
                    timeout=5.0
                )
        except Exception as e:
            logger.debug(f"Heartbeat failed: {e}")
            
    async def get_next_task(self) -> TaskMessage | None:
        """Polls for the next pending task."""
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(f"{self.base_url}/tasks/next", timeout=5.0)
                res.raise_for_status()
                data = res.json()
                if data.get("has_task"):
                    task_data = data["task"]
                    return TaskMessage(**task_data)
                return None
        except Exception as e:
            logger.debug(f"Failed to fetch tasks: {e}")
            return None
            
    async def submit_result(self, result: TaskResult):
        """Submits the result of a completed task."""
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    f"{self.base_url}/tasks/result",
                    json=result.model_dump(),
                    timeout=5.0
                )
                res.raise_for_status()
                logger.info(f"Successfully submitted result for task {result.task_id}")
        except Exception as e:
            logger.error(f"Failed to submit task result: {e}")
