import os
import subprocess
import requests
import logging
from typing import Dict, List, Optional

logger = logging.getLogger("tokyoos.llm_manager")

class LLMManager:
    """
    Gestão de Modelos LLM (Ollama) e Detecção de Hardware.
    """
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.agent_models: Dict[str, str] = {
            "tokyo_cfo": os.getenv("TOKYO_CFO_MODEL", "llama3"),
            "tokyo_coo": os.getenv("TOKYO_COO_MODEL", "llama3"),
            "tokyo_estoque": os.getenv("TOKYO_ESTOQUE_MODEL", "llama3"),
        }
        
    def detect_hardware(self) -> Dict[str, str]:
        """Detecta o hardware para recomendar ou limitar modelos."""
        hardware_info = {"type": "CPU", "details": "Unknown"}
        
        # Check Apple Silicon
        try:
            mac_info = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"], stderr=subprocess.DEVNULL).decode().strip()
            if "Apple" in mac_info:
                hardware_info = {"type": "Apple Silicon (MPS)", "details": mac_info}
                return hardware_info
        except Exception:
            pass
            
        # Check NVIDIA
        try:
            nvidia_info = subprocess.check_output(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], stderr=subprocess.DEVNULL).decode().strip()
            if nvidia_info:
                hardware_info = {"type": "NVIDIA GPU (CUDA)", "details": nvidia_info.split('\n')[0]}
                return hardware_info
        except Exception:
            pass
            
        return hardware_info

    def list_local_models(self) -> List[str]:
        """Lista os modelos disponíveis no Ollama."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [m.get("name") for m in data.get("models", [])]
        except Exception as e:
            logger.error(f"Erro ao conectar com Ollama: {e}")
        return []

    def pull_model(self, model_name: str) -> bool:
        """Faz o pull de um modelo diretamente do Ollama."""
        logger.info(f"Iniciando download do modelo {model_name}...")
        try:
            # Em modo streaming, pode demorar, faremos síncrono para simplificar (timeout longo)
            response = requests.post(
                f"{self.ollama_url}/api/pull", 
                json={"name": model_name, "stream": False},
                timeout=600 # 10 minutos
            )
            if response.status_code == 200:
                logger.info(f"Modelo {model_name} baixado com sucesso.")
                return True
            else:
                logger.error(f"Erro ao baixar modelo {model_name}: {response.text}")
        except Exception as e:
            logger.error(f"Exceção ao puxar o modelo {model_name}: {e}")
        return False

    def get_model_for_agent(self, agent_id: str) -> str:
        """Retorna o modelo configurado para o agente específico."""
        return self.agent_models.get(agent_id, os.getenv("TOKYO_LLM_MODEL", "llama3"))

    def set_model_for_agent(self, agent_id: str, model_name: str):
        """Atualiza o modelo de um agente."""
        self.agent_models[agent_id] = model_name
        logger.info(f"Agente {agent_id} agora usará o modelo {model_name}.")

# Instância global Singleton
llm_manager = LLMManager()
