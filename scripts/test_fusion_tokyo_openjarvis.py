#!/usr/bin/env python3
"""
Integrated Validation Script for TokyoOS & OpenJarvis Fusion.
Validates routes, SafetyGate, Agent Core registry, and business agents flows.
"""

import os
import sys
import unittest
from pathlib import Path

# Setup path so we can import TokyoOS and OpenJarvis correctly
sys.path.insert(0, str(Path(__file__).parent.parent))

# Force mock mode and safe mode for validation tests
os.environ["MOCK_DATA_ENABLED"] = "true"
os.environ["TOKYO_SAFE_MODE"] = "true"
os.environ["TOKYO_TOKEN_EXPOSED"] = "false"
os.environ["OPENJARVIS_HOME"] = str(Path(__file__).parent.parent / "data" / "openjarvis")

# Mock get_engine to prevent network/socket queries to localhost:11434 (Ollama) or external APIs
from unittest.mock import MagicMock
import openjarvis.engine._discovery

mock_engine = MagicMock()
mock_engine.health.return_value = True
mock_engine.list_models.return_value = ["mock-model"]
mock_engine.generate.return_value = {"content": "Análise Mock: O Lucro Operacional da Bunny Dreams MTD é saudável.", "usage": {}}

openjarvis.engine._discovery.get_engine = lambda config, engine_key=None, model=None: ("mock_engine", mock_engine)
openjarvis.engine._discovery.discover_engines = lambda config: [("mock_engine", mock_engine)]

from fastapi.testclient import TestClient
from app import app
from tokyo_orchestrator import route_command

class TestTokyoOSOpenJarvisFusion(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_ui_and_health_routes(self):
        """1. Assert UI and basic system health routes are active and respond with 200 OK."""
        # UI page
        resp = self.client.get("/ui")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("TokyoOS — GrupsBunny AI Hub", resp.text)

        # Health endpoint
        resp = self.client.get("/tokyo/system/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["health"], "ok")
        self.assertEqual(data["voice_preserved"], True)
        self.assertEqual(data["app_preserved"], True)

    def test_doctor_api(self):
        """2. Assert Tokyo Doctor API returns system integrations health, including Agent Core."""
        resp = self.client.get("/tokyo/doctor")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("checks", data)
        self.assertIn("agent_core", data["checks"])
        self.assertEqual(data["checks"]["agent_core"]["status"], "healthy")
        self.assertIn("rust_bridge", data["checks"])

    def test_agent_core_endpoints(self):
        """3. Assert Agent Core metadata endpoints return valid components from registries."""
        # Status
        resp = self.client.get("/tokyo/agent-core/status")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "active")

        # Registered agents
        resp = self.client.get("/tokyo/agent-core/agents")
        self.assertEqual(resp.status_code, 200)
        agents = resp.json()["agents"]
        agent_ids = [a["id"] for a in agents]
        self.assertIn("tokyo_cfo", agent_ids)
        self.assertIn("tokyo_coo", agent_ids)
        self.assertIn("tokyo_estoque", agent_ids)

        # Registered skills
        resp = self.client.get("/tokyo/agent-core/skills")
        self.assertEqual(resp.status_code, 200)
        skills = resp.json()["skills"]
        self.assertTrue(len(skills) > 0)

        # Registered tools
        resp = self.client.get("/tokyo/agent-core/tools")
        self.assertEqual(resp.status_code, 200)
        tools = resp.json()["tools"]
        tool_ids = [t["id"] for t in tools]
        self.assertIn("calculator", tool_ids)
        self.assertIn("web_search", tool_ids)

    def test_safety_gate_blocking(self):
        """4. Assert SafetyGate blocks unauthorized destructive commands."""
        # Direct gateway execute
        resp = self.client.post("/tokyo/action/execute", json={
            "command": "sudo rm -rf /app",
            "source": "ui_chat"
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "blocked")

        # Operator execute
        resp = self.client.post("/tokyo/operator/execute", json={
            "command": "rm -rf tokyoos_src",
            "mode": "company_operator"
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "failed")
        self.assertEqual(resp.json()["reason"], "blocked_project_protection")

    def test_cfo_mandatory_flow(self):
        """5. Assert CFO Agent analysis flow executes correctly with mock markers."""
        command = "Tokyo, analise a situação financeira da Bunny Dreams e diga o que preciso fazer hoje."
        
        # Test routing function directly
        res = route_command(command)
        self.assertEqual(res["ok"], True)
        self.assertEqual(res["status"], "completed")
        self.assertEqual(res["provider_used"], "tokyo_cfo")
        self.assertIn("[DEMO/MOCK DATA ACTIVE]", res["summary"])
        self.assertIn("Lucro Operacional", res["summary"])

        # Test gateway POST endpoint
        resp = self.client.post("/tokyo/action/execute", json={
            "command": command,
            "source": "ui_chat"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["ok"], True)
        self.assertEqual(data["status"], "completed")
        self.assertEqual(data["provider_used"], "tokyo_cfo")
        self.assertIn("[DEMO/MOCK DATA ACTIVE]", data["summary"])

if __name__ == "__main__":
    unittest.main()
