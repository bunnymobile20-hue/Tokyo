import os
from .config import load_config
from pathlib import Path

def get_shared_folder_path() -> str:
    cfg = load_config()
    return cfg.shared_folder_local

def list_shared_files() -> dict:
    try:
        folder = get_shared_folder_path()
        if not os.path.exists(folder):
            return {"ok": False, "error": f"Local SMB mount path {folder} does not exist."}
        
        files = []
        for f in os.listdir(folder):
            path = os.path.join(folder, f)
            if os.path.isfile(path):
                files.append({
                    "name": f,
                    "size_bytes": os.path.getsize(path)
                })
        return {"ok": True, "files": files}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def write_shared_file(filename: str, content: str) -> dict:
    try:
        folder = get_shared_folder_path()
        clean_name = Path(filename).name
        if not clean_name:
            return {"ok": False, "error": "Invalid filename"}
            
        path = os.path.join(folder, clean_name)
        os.makedirs(folder, exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return {"ok": True, "path": path}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def read_shared_file(filename: str) -> dict:
    try:
        folder = get_shared_folder_path()
        clean_name = Path(filename).name
        if not clean_name:
            return {"ok": False, "error": "Invalid filename"}
            
        path = os.path.join(folder, clean_name)
        if not os.path.exists(path):
            return {"ok": False, "error": "File not found"}
            
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            
        return {"ok": True, "content": content}
    except Exception as e:
        return {"ok": False, "error": str(e)}
