from fastapi import APIRouter
from .bridge_service import MacBridgeService
from .schemas import OpenUrlRequest, OpenFileRequest, RevealFolderRequest, ShowNotificationRequest, WriteSharedFileRequest
from .smb_mount import list_shared_files, write_shared_file, read_shared_file

router = APIRouter()
svc = MacBridgeService()

@router.get("/tokyo/mac-bridge/status")
async def get_status():
    return svc.get_status()

@router.post("/tokyo/mac-bridge/test-ssh")
async def test_ssh():
    return svc.test_ssh()

@router.post("/tokyo/mac-bridge/open-url")
async def open_url(req: OpenUrlRequest):
    return svc.process_command("open_url", {"url": req.url, "browser": req.browser})

@router.post("/tokyo/mac-bridge/open-file")
async def open_file(req: OpenFileRequest):
    return svc.process_command("open_file", {"path": req.path})

@router.post("/tokyo/mac-bridge/reveal-folder")
async def reveal_folder(req: RevealFolderRequest):
    return svc.process_command("reveal_folder", {"path": req.path})

@router.post("/tokyo/mac-bridge/show-notification")
async def show_notification(req: ShowNotificationRequest):
    return svc.process_command("show_notification", {"text": req.text})

@router.get("/tokyo/mac-bridge/jobs")
async def get_jobs():
    return {"jobs": svc.get_jobs(), "token_exposed": False}

@router.get("/tokyo/mac-bridge/shared-files")
async def get_shared_files():
    return list_shared_files()

@router.post("/tokyo/mac-bridge/shared-files/write")
async def write_shared(req: WriteSharedFileRequest):
    return write_shared_file(req.filename, req.content)

@router.get("/tokyo/mac-bridge/shared-files/read")
async def read_shared(filename: str):
    return read_shared_file(filename)
