import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import importlib.util
from .config import HermesConfig

def _is_safe_url(url: str) -> bool:
    if not url.startswith(("http://", "https://")):
        return False
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            return False
        # Block private IPs and localhost
        blocked = ["localhost", "127.0.0.1", "0.0.0.0", "192.168.", "10.", "172.16.", "172.17.", "172.18.", "172.19.", "172.20.", "172.21.", "172.22.", "172.23.", "172.24.", "172.25.", "172.26.", "172.27.", "172.28.", "172.29.", "172.30.", "172.31."]
        for b in blocked:
            if hostname == b or hostname.startswith(b):
                # allow explicitly configured ones (like firecrawl or hermes) but generally block
                # However, for the browser provider, we restrict it completely.
                return False
        return True
    except Exception:
        return False

def detect_browser_provider() -> str:
    if importlib.util.find_spec("playwright"):
        return "playwright"
    if importlib.util.find_spec("requests") and importlib.util.find_spec("bs4"):
        return "requests_fallback"
    return "missing_dependency"

def browser_health() -> dict:
    provider = detect_browser_provider()
    return {
        "status": "connected" if provider != "missing_dependency" else "missing",
        "provider": provider
    }

def browser_capabilities() -> dict:
    return {
        "extract_text": True,
        "extract_title": True,
        "summarize_url": True
    }

def _fallback_extract(url: str) -> dict:
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        title = soup.title.string if soup.title else "Sem Título"
        
        if "youtube.com" in url:
            return {"ok": True, "title": title, "text": "Youtube loaded partial. Video content extraction requires specific API.", "status": "youtube_loaded_partial"}
            
        for script in soup(["script", "style"]):
            script.extract()
            
        text = soup.get_text(separator=' ', strip=True)
        return {"ok": True, "title": title, "text": text}
    except Exception as e:
        if "youtube.com" in url:
            return {"ok": True, "title": "YouTube (Blocked/Error)", "text": f"youtube_loaded_partial: {str(e)}", "status": "youtube_loaded_partial"}
        return {"ok": False, "error": str(e)}

def _playwright_extract(url: str) -> dict:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=15000)
            title = page.title()
            text = page.evaluate("document.body.innerText")
            browser.close()
            return {"ok": True, "title": title, "text": text}
    except Exception as e:
        # Fallback to requests if playwright throws an error (like missing browsers)
        return _fallback_extract(url)

def open_url(url: str) -> dict:
    if not _is_safe_url(url):
        return {"ok": False, "error": "URL bloqueada por políticas de segurança."}
    
    provider = detect_browser_provider()
    if provider == "playwright":
        return _playwright_extract(url)
    elif provider == "requests_fallback":
        return _fallback_extract(url)
    else:
        return {"ok": False, "error": "Nenhum provider de browser disponível."}

def extract_title(url: str) -> dict:
    res = open_url(url)
    if res.get("ok"):
        return {"ok": True, "title": res.get("title")}
    return res

def extract_text(url: str) -> dict:
    res = open_url(url)
    if res.get("ok"):
        return {"ok": True, "text": res.get("text")}
    return res

def summarize_url(url: str, model="qwen2.5:32b-instruct") -> dict:
    res = open_url(url)
    if not res.get("ok"):
        return res
    
    text = res.get("text", "")
    if not text:
        return {"ok": False, "error": "Nenhum texto encontrado para resumir."}
    
    # Use Ollama for summary
    base_url = HermesConfig.get("ollama_base_url", "http://127.0.0.1:11434")
    prompt = f"Resuma o conteúdo abaixo em português brasileiro, com objetividade:\n\n{text[:5000]}"
    try:
        ollama_res = requests.post(f"{base_url}/api/generate", json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }, timeout=120)
        if ollama_res.status_code == 200:
            summary = ollama_res.json().get("response", "")
            return {"ok": True, "summary": summary, "title": res.get("title")}
        return {"ok": False, "error": f"Erro do Ollama: {ollama_res.status_code}"}
    except Exception as e:
        return {"ok": False, "error": f"Erro ao contatar Ollama: {str(e)}"}

def search_web(query: str) -> dict:
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        res = requests.get(f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}", headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        results = []
        for a in soup.find_all('a', class_='result__snippet'):
            results.append(a.text)
        
        if not results:
            return {"ok": True, "text": "Nenhum resultado claro encontrado."}
            
        return {"ok": True, "text": "\n".join(results[:5])}
    except Exception as e:
        return {"ok": False, "error": str(e)}
