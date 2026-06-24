import os
import pytest
import sys
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tokyo_plugins.hermes_bridge.browser_provider import _is_safe_url, detect_browser_provider, browser_health, open_url
from tokyo_plugins.hermes_bridge.firecrawl_provider import detect_firecrawl, firecrawl_health
from tokyo_plugins.hermes_bridge.hermes_executor import HermesAPIExecutor

def test_safe_url():
    assert _is_safe_url("https://example.com") == True
    assert _is_safe_url("http://example.com") == True
    assert _is_safe_url("ftp://example.com") == False
    assert _is_safe_url("file:///etc/passwd") == False
    assert _is_safe_url("http://localhost:8788") == False
    assert _is_safe_url("http://127.0.0.1:8080") == False
    assert _is_safe_url("http://192.168.1.173") == False
    assert _is_safe_url("http://10.0.0.1") == False

def test_browser_provider_detection():
    provider = detect_browser_provider()
    # It should at least be requests_fallback
    assert provider in ["playwright", "requests_fallback", "missing_dependency"]

def test_firecrawl_detection():
    # Because there's no base_url set in config locally without proper setup
    provider = detect_firecrawl()
    assert provider == "not_configured"
    
def test_hermes_executor_masks_token():
    executor = HermesAPIExecutor()
    executor.api_key = "abcdefgh12345678"
    health = executor.hermes_health()
    assert health["auth_masked"] == "Bearer tkos_****5678"
    
def test_hermes_executor_empty_token():
    executor = HermesAPIExecutor()
    executor.api_key = ""
    health = executor.hermes_health()
    assert health["auth_masked"] == "Bearer pending"

def test_fallback_browser_open_url():
    # Only if playwright is missing and requests fallback is used
    if detect_browser_provider() == "requests_fallback":
        res = open_url("https://example.com")
        assert res["ok"] == True
        assert "Example Domain" in res["title"]
