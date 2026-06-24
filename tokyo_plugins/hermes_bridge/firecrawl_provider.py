import os
import requests
from .config import HermesConfig

def detect_firecrawl() -> str:
    base_url = HermesConfig.get("firecrawl_base_url")
    if base_url:
        return "available"
    return "not_configured"

def firecrawl_health() -> dict:
    status = detect_firecrawl()
    return {
        "status": "connected" if status == "available" else "missing",
        "provider": status
    }

def firecrawl_capabilities() -> dict:
    return {
        "scrape": True,
        "crawl": True
    }

def scrape_url(url: str) -> dict:
    base_url = HermesConfig.get("firecrawl_base_url")
    if not base_url:
        return {"ok": False, "error": "Firecrawl não está configurado."}
    
    api_key = os.environ.get("FIRECRAWL_API_KEY", "")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
        
    try:
        res = requests.post(f"{base_url}/v1/scrape", json={"url": url}, headers=headers, timeout=30)
        res.raise_for_status()
        data = res.json()
        if data.get("success"):
            return {
                "ok": True,
                "title": data.get("data", {}).get("metadata", {}).get("title", ""),
                "text": data.get("data", {}).get("markdown", "")
            }
        return {"ok": False, "error": data.get("error", "Erro no scrape")}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def crawl_url(url: str) -> dict:
    base_url = HermesConfig.get("firecrawl_base_url")
    if not base_url:
        return {"ok": False, "error": "Firecrawl não está configurado."}
    
    api_key = os.environ.get("FIRECRAWL_API_KEY", "")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
        
    try:
        res = requests.post(f"{base_url}/v1/crawl", json={"url": url}, headers=headers, timeout=30)
        res.raise_for_status()
        return {"ok": True, "job_id": res.json().get("id", "")}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def summarize_crawl(url: str, model="qwen2.5:32b-instruct") -> dict:
    res = scrape_url(url)
    if not res.get("ok"):
        return res
        
    text = res.get("text", "")
    if not text:
        return {"ok": False, "error": "Nenhum texto retornado pelo Firecrawl."}
        
    # Use Ollama for summary
    ollama_url = HermesConfig.get("ollama_base_url", "http://127.0.0.1:11434")
    prompt = f"Resuma o conteúdo abaixo em português brasileiro, com objetividade:\n\n{text[:5000]}"
    try:
        ollama_res = requests.post(f"{ollama_url}/api/generate", json={
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
