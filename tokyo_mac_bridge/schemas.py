from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class MacBridgeConfigSchema(BaseModel):
    enabled: bool
    mode: str
    mac_name: str
    mac_host: str
    mac_user: str
    ssh_port: int
    ssh_key_path: str
    default_browser: str
    shared_folder_local: str
    shared_folder_remote: str
    allow_open_url: bool
    allow_open_file: bool
    allow_finder: bool
    allow_screenshot: bool
    allow_shell: bool
    allow_destructive: bool

class OpenUrlRequest(BaseModel):
    url: str
    browser: Optional[str] = None

class OpenFileRequest(BaseModel):
    path: str

class RevealFolderRequest(BaseModel):
    path: str

class ShowNotificationRequest(BaseModel):
    text: str

class WriteSharedFileRequest(BaseModel):
    filename: str
    content: str
