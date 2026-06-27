import os
import shutil
import subprocess
import base64
from pathlib import Path
from .safety import ensure_safe_path
from .config import QUARANTINE_DIR, WORKSPACE_DIR

def create_folder(folder_name: str) -> str:
    """Creates a folder inside the workspace."""
    target_path = ensure_safe_path(str(WORKSPACE_DIR / folder_name))
    target_path.mkdir(parents=True, exist_ok=True)
    return str(target_path)

def quarantine_folder(folder_name: str) -> str:
    """Moves a folder to the quarantine directory instead of deleting it."""
    source_path = ensure_safe_path(str(WORKSPACE_DIR / folder_name))
    
    if not source_path.exists():
        raise FileNotFoundError(f"Folder '{folder_name}' does not exist.")
        
    target_path = QUARANTINE_DIR / folder_name
    
    # Handle duplicates in quarantine
    counter = 1
    while target_path.exists():
        target_path = QUARANTINE_DIR / f"{folder_name}_{counter}"
        counter += 1
        
    shutil.move(str(source_path), str(target_path))
    return str(target_path)

def delete_item(item_name: str) -> str:
    """Moves an item inside the workspace to the macOS Trash."""
    target_path = ensure_safe_path(str(WORKSPACE_DIR / item_name))
    if not target_path.exists():
        raise FileNotFoundError(f"Item '{item_name}' does not exist.")
    subprocess.run(['osascript', '-e', f'tell app "Finder" to move POSIX file "{target_path}" to trash'], check=True)
    return str(target_path)

def write_text_file(filename: str, content: str) -> str:
    """Creates a text file inside the workspace."""
    target_path = ensure_safe_path(str(WORKSPACE_DIR / filename))
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return str(target_path)

def open_mac_app(app_name: str) -> str:
    """Opens a macOS application natively by name."""
    import Cocoa
    workspace = Cocoa.NSWorkspace.sharedWorkspace()
    success = workspace.launchApplication_(app_name)
    if not success:
        raise RuntimeError(f"Falha ao abrir o aplicativo '{app_name}'.")
    return app_name

def open_document(filename: str) -> str:
    """Opens a document natively inside the workspace."""
    import Cocoa
    target_path = ensure_safe_path(str(WORKSPACE_DIR / filename))
    if not target_path.exists():
        raise FileNotFoundError(f"Document '{filename}' does not exist.")
        
    workspace = Cocoa.NSWorkspace.sharedWorkspace()
    success = workspace.openFile_(str(target_path))
    if not success:
        raise RuntimeError(f"Falha ao abrir o documento '{filename}'.")
    return str(target_path)

def capture_screen_base64() -> str:
    """Takes a screenshot using macOS native APIs (PyObjC) and returns base64 encoded string."""
    import Quartz
    from AppKit import NSBitmapImageRep, NSPNGFileType
    import base64
    
    # Captura a imagem nativamente usando a API oficial do macOS
    # Isso garante que a permissão de Gravação de Tela do TokyoOS.app seja usada perfeitamente!
    image = Quartz.CGWindowListCreateImage(
        Quartz.CGRectInfinite,
        Quartz.kCGWindowListOptionOnScreenOnly,
        Quartz.kCGNullWindowID,
        Quartz.kCGWindowImageDefault
    )
    
    if not image:
        raise RuntimeError("Falha ao capturar a tela. Verifique as permissões de Gravação de Tela.")
        
    bitmap = NSBitmapImageRep.alloc().initWithCGImage_(image)
    data = bitmap.representationUsingType_properties_(NSPNGFileType, None)
    
    return base64.b64encode(data).decode('utf-8')

def execute_applescript(script: str) -> str:
    """Executes arbitrary AppleScript."""
    import subprocess
    proc = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"AppleScript error: {proc.stderr}")
    return proc.stdout.strip()

def keyboard_type(text: str) -> str:
    """Types text globally."""
    escaped_text = text.replace('"', '\\"')
    script = f'tell application "System Events" to keystroke "{escaped_text}"'
    execute_applescript(script)
    return text

def keyboard_shortcut(key: str, modifier: str = "command down") -> str:
    """Presses a keyboard shortcut."""
    script = f'tell application "System Events" to keystroke "{key}" using {modifier}'
    execute_applescript(script)
    return f"{modifier} + {key}"

def mouse_click(x: int, y: int, button: str = "left") -> str:
    import Quartz
    import time
    point = Quartz.CGPoint(x, y)
    
    # Move
    move_event = Quartz.CGEventCreateMouseEvent(None, Quartz.kCGEventMouseMoved, point, 0)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, move_event)
    time.sleep(0.05)
    
    if button == "right":
        down = Quartz.kCGEventRightMouseDown
        up = Quartz.kCGEventRightMouseUp
        btn = Quartz.kCGMouseButtonRight
    else:
        down = Quartz.kCGEventLeftMouseDown
        up = Quartz.kCGEventLeftMouseUp
        btn = Quartz.kCGMouseButtonLeft
        
    down_event = Quartz.CGEventCreateMouseEvent(None, down, point, btn)
    up_event = Quartz.CGEventCreateMouseEvent(None, up, point, btn)
    
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, down_event)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, up_event)
    
    return f"Clicked {button} at {x}, {y}"

def extract_ui_semantics() -> str:
    """Extrai a estrutura de texto da tela atual (Modo X9)."""
    script = '''
    tell application "System Events"
        set frontApp to first application process whose frontmost is true
        set uiText to "App: " & name of frontApp & " | Elementos visiveis na tela atual: "
        
        try
            set win to front window of frontApp
            set allElems to entire contents of win
            repeat with el in allElems
                try
                    if name of el is not missing value then
                        set uiText to uiText & " [NOME: " & name of el & "] "
                    end if
                    if value of el is not missing value then
                        set uiText to uiText & " [VALOR: " & (value of el as string) & "] "
                    end if
                end try
            end repeat
        end try
        return uiText
    end tell
    '''
    return execute_applescript(script)
