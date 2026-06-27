import asyncio
from typing import Dict, Any
from .config import POLL_INTERVAL_SECONDS, HEARTBEAT_INTERVAL_SECONDS
from .client import TokyoClient
from .schemas import TaskMessage, TaskResult
from .logs import get_logger
from .safety import validate_action, SafetyViolation
from .os_actions import create_folder, quarantine_folder, delete_item, write_text_file, open_mac_app, open_document, capture_screen_base64, execute_applescript, keyboard_type, keyboard_shortcut, mouse_click, extract_ui_semantics
from .browser_actions import open_url, extract_text

logger = get_logger()

class DesktopAgent:
    def __init__(self):
        self.client = TokyoClient()
        self.running = False
        
    async def process_task(self, task: TaskMessage):
        """Processes a single task safely."""
        logger.info(f"Processing task {task.task_id}: {task.command}")
        
        success = False
        result_data = {}
        logs = []
        
        def log_msg(msg: str):
            logs.append(msg)
            logger.info(f"[{task.task_id}] {msg}")
            
        try:
            # 1. Validate action
            validate_action(task.action_type)
            
            # 2. Execute action
            if task.action_type == "create_folder":
                folder_name = task.payload.get("folder_name")
                if not folder_name:
                    raise ValueError("folder_name missing in payload")
                path = create_folder(folder_name)
                result_data = {"path": path}
                log_msg(f"Created folder at: {path}")
                success = True
                
            elif task.action_type == "quarantine_folder":
                folder_name = task.payload.get("folder_name")
                if not folder_name:
                    raise ValueError("folder_name missing in payload")
                path = quarantine_folder(folder_name)
                result_data = {"path": path}
                log_msg(f"Moved folder to quarantine: {path}")
                success = True
                
            elif task.action_type == "open_url":
                url = task.payload.get("url")
                if not url:
                    raise ValueError("url missing in payload")
                title = await open_url(url, headless=False) # Headed to show the user
                result_data = {"title": title}
                log_msg(f"Opened URL {url}, title: {title}")
                success = True
                
            elif task.action_type == "extract_text":
                url = task.payload.get("url")
                if not url:
                    raise ValueError("url missing in payload")
                data = await extract_text(url, headless=True)
                result_data = data
                log_msg(f"Extracted text from {url}")
                success = True
                
            elif task.action_type == "delete_item":
                item_name = task.payload.get("item_name")
                if not item_name:
                    raise ValueError("item_name missing in payload")
                path = delete_item(item_name)
                result_data = {"path": path}
                log_msg(f"Moved item to trash: {path}")
                success = True

            elif task.action_type == "open_notepad":
                app = open_mac_app("TextEdit")
                result_data = {"app": app}
                log_msg(f"Opened app: {app}")
                success = True

            elif task.action_type == "write_text":
                filename = task.payload.get("filename")
                content = task.payload.get("content")
                if not filename or not content:
                    raise ValueError("filename or content missing in payload")
                path = write_text_file(filename, content)
                # After writing, we open it so the user can see it
                open_document(filename)
                result_data = {"path": path}
                log_msg(f"Wrote text and opened file: {path}")
                success = True

            elif task.action_type == "open_calendar":
                app = open_mac_app("Calendar")
                result_data = {"app": app}
                log_msg(f"Opened app: {app}")
                success = True

            elif task.action_type == "open_reminders":
                app = open_mac_app("Reminders")
                result_data = {"app": app}
                log_msg(f"Opened app: {app}")
                success = True

            elif task.action_type == "open_document":
                filename = task.payload.get("filename")
                if not filename:
                    raise ValueError("filename missing in payload")
                path = open_document(filename)
                result_data = {"path": path}
                log_msg(f"Opened document: {path}")
                success = True
                
            elif task.action_type == "read_screen":
                log_msg("Capturing screen...")
                image_base64 = capture_screen_base64()
                result_data = {"image_base64": image_base64}
                log_msg("Screen captured successfully.")
                success = True
                
            elif task.action_type == "read_screen_semantics":
                log_msg("Extracting UI semantics (X9 mode)...")
                semantics = extract_ui_semantics()
                result_data = {"ui_semantics": semantics}
                log_msg("Semantics extracted successfully.")
                success = True
                
            elif task.action_type == "mouse_click":
                x = int(task.payload.get("x", 0))
                y = int(task.payload.get("y", 0))
                button = task.payload.get("button", "left")
                msg = mouse_click(x, y, button)
                result_data = {"message": msg}
                log_msg(msg)
                success = True
                
            elif task.action_type == "keyboard_type":
                text = task.payload.get("text", "")
                msg = keyboard_type(text)
                result_data = {"message": "Typed text"}
                log_msg(f"Typed text: {msg}")
                success = True
                
            elif task.action_type == "keyboard_shortcut":
                key = task.payload.get("key", "")
                modifier = task.payload.get("modifier", "command down")
                msg = keyboard_shortcut(key, modifier)
                result_data = {"message": msg}
                log_msg(f"Pressed shortcut: {msg}")
                success = True
                
            elif task.action_type == "execute_applescript":
                script = task.payload.get("script", "")
                output = execute_applescript(script)
                result_data = {"output": output}
                log_msg(f"Executed AppleScript. Output: {output}")
                success = True
                
            elif task.action_type == "status":
                result_data = {"status": "online, ready"}
                log_msg("Status check passed")
                success = True
                
        except SafetyViolation as e:
            log_msg(f"SAFETY VIOLATION BLOCKED: {e}")
        except Exception as e:
            log_msg(f"Error executing task: {e}")
            
        # 3. Submit Result
        result = TaskResult(
            task_id=task.task_id,
            success=success,
            result=result_data,
            logs=logs
        )
        await self.client.submit_result(result)
        
    async def heartbeat_loop(self):
        while self.running:
            await self.client.heartbeat()
            await asyncio.sleep(HEARTBEAT_INTERVAL_SECONDS)
            
    async def run(self):
        logger.info("Starting Tokyo Desktop Agent for MacBook...")
        if not await self.client.register():
            logger.error("Failed to register. Exiting.")
            return
            
        self.running = True
        
        # Start heartbeat task
        heartbeat_task = asyncio.create_task(self.heartbeat_loop())
        
        try:
            while self.running:
                task = await self.client.get_next_task()
                if task:
                    # Process synchronously to avoid overlapping browser instances for MVP
                    await self.process_task(task)
                else:
                    await asyncio.sleep(POLL_INTERVAL_SECONDS)
        except asyncio.CancelledError:
            self.running = False
        finally:
            heartbeat_task.cancel()
            logger.info("Agent stopped.")
