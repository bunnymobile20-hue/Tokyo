import json
import logging
import httpx
import asyncio
import base64
from google import genai
from google.genai import types
from livekit.agents import llm
import httpx
from livekit.agents import llm

logger = logging.getLogger("tokyo.agent.tools")

@llm.function_tool(description="Cria uma nova pasta na área de trabalho (workspace) do MacBook do usuário.")
async def create_folder_on_macbook(
    folder_name: str,
) -> str:
    """Cria uma nova pasta no MacBook."""
    logger.info(f"Tool called: create_folder_on_macbook(folder_name='{folder_name}')")
    
    payload = {
        "command": f"Criar pasta {folder_name}",
        "action_type": "create_folder",
        "payload": {
            "folder_name": folder_name
        }
    }
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post("http://localhost:8788/tokyo/desktop-agent-operator/execute", json=payload)
            if resp.status_code == 200:
                data = resp.json()
                task_id = data.get("task_id", "unknown")
                return f"O comando para criar a pasta '{folder_name}' foi enviado ao MacBook com sucesso! ID da tarefa: {task_id}. O desktop agent irá executá-la em breve."
            else:
                return f"Falha ao enviar comando para o MacBook. Status: {resp.status_code}"
    except Exception as e:
        logger.error(f"Error in create_folder_on_macbook: {e}")
        return f"Erro de comunicação com o servidor interno: {str(e)}"

@llm.function_tool(description="Abre uma página web no navegador do MacBook do usuário.")
async def open_website_on_macbook(
    url: str,
) -> str:
    """Abre uma URL no MacBook."""
    logger.info(f"Tool called: open_website_on_macbook(url='{url}')")
    
    payload = {
        "command": f"Abrir site {url}",
        "action_type": "open_url",
        "payload": {
            "url": url
        }
    }
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post("http://localhost:8788/tokyo/desktop-agent-operator/execute", json=payload)
            if resp.status_code == 200:
                return f"O comando para abrir o site '{url}' foi enviado ao MacBook com sucesso!"
            else:
                return f"Falha ao enviar comando para o MacBook. Status: {resp.status_code}"
    except Exception as e:
        logger.error(f"Error in open_website_on_macbook: {e}")
        return f"Erro de comunicação: {str(e)}"

@llm.function_tool(description="Exclui um arquivo ou pasta na área de trabalho (workspace) do MacBook do usuário, enviando para a Lixeira.")
async def delete_item_on_macbook(
    item_name: str,
) -> str:
    """Exclui (move para a lixeira) um item no MacBook."""
    logger.info(f"Tool called: delete_item_on_macbook(item_name='{item_name}')")
    
    payload = {
        "command": f"Excluir {item_name}",
        "action_type": "delete_item",
        "payload": {
            "item_name": item_name
        }
    }
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post("http://localhost:8788/tokyo/desktop-agent-operator/execute", json=payload)
            if resp.status_code == 200:
                return f"O comando para excluir '{item_name}' foi enviado ao MacBook com sucesso!"
            else:
                return f"Falha ao enviar comando para o MacBook. Status: {resp.status_code}"
    except Exception as e:
        logger.error(f"Error in delete_item_on_macbook: {e}")
        return f"Erro de comunicação: {str(e)}"

@llm.function_tool(description="Abre o aplicativo Bloco de Notas (TextEdit) no MacBook do usuário.")
async def open_notepad_on_macbook() -> str:
    """Abre o TextEdit no MacBook."""
    logger.info("Tool called: open_notepad_on_macbook()")
    
    payload = {
        "command": "Abrir Bloco de Notas",
        "action_type": "open_notepad",
        "payload": {}
    }
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post("http://localhost:8788/tokyo/desktop-agent-operator/execute", json=payload)
            if resp.status_code == 200:
                return "O comando para abrir o Bloco de Notas foi enviado ao MacBook com sucesso!"
            else:
                return f"Falha ao enviar comando. Status: {resp.status_code}"
    except Exception as e:
        logger.error(f"Error in open_notepad_on_macbook: {e}")
        return f"Erro de comunicação: {str(e)}"

@llm.function_tool(description="Cria e escreve texto em um arquivo na área de trabalho do MacBook, abrindo-o logo em seguida para o usuário.")
async def write_text_on_macbook(
    filename: str,
    content: str,
) -> str:
    """Escreve um texto em um arquivo e o abre no MacBook."""
    logger.info(f"Tool called: write_text_on_macbook(filename='{filename}')")
    
    payload = {
        "command": f"Escrever em {filename}",
        "action_type": "write_text",
        "payload": {
            "filename": filename,
            "content": content
        }
    }
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post("http://localhost:8788/tokyo/desktop-agent-operator/execute", json=payload)
            if resp.status_code == 200:
                return f"O comando para escrever o arquivo '{filename}' foi enviado ao MacBook com sucesso!"
            else:
                return f"Falha ao enviar comando. Status: {resp.status_code}"
    except Exception as e:
        logger.error(f"Error in write_text_on_macbook: {e}")
        return f"Erro de comunicação: {str(e)}"

@llm.function_tool(description="Abre o aplicativo Calendário no MacBook do usuário.")
async def open_calendar_on_macbook() -> str:
    """Abre o Calendário no MacBook."""
    logger.info("Tool called: open_calendar_on_macbook()")
    
    payload = {
        "command": "Abrir Calendário",
        "action_type": "open_calendar",
        "payload": {}
    }
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post("http://localhost:8788/tokyo/desktop-agent-operator/execute", json=payload)
            if resp.status_code == 200:
                return "O comando para abrir o Calendário foi enviado ao MacBook com sucesso!"
            else:
                return f"Falha ao enviar comando. Status: {resp.status_code}"
    except Exception as e:
        logger.error(f"Error in open_calendar_on_macbook: {e}")
        return f"Erro de comunicação: {str(e)}"

@llm.function_tool(description="Abre o aplicativo de Lembretes/Tarefas no MacBook do usuário.")
async def open_reminders_on_macbook() -> str:
    """Abre Lembretes (Tarefas) no MacBook."""
    logger.info("Tool called: open_reminders_on_macbook()")
    
    payload = {
        "command": "Abrir Tarefas",
        "action_type": "open_reminders",
        "payload": {}
    }
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post("http://localhost:8788/tokyo/desktop-agent-operator/execute", json=payload)
            if resp.status_code == 200:
                return "O comando para abrir o Tarefas (Lembretes) foi enviado ao MacBook com sucesso!"
            else:
                return f"Falha ao enviar comando. Status: {resp.status_code}"
    except Exception as e:
        logger.error(f"Error in open_reminders_on_macbook: {e}")
        return f"Erro de comunicação: {str(e)}"

@llm.function_tool(description="Abre um documento (arquivo) específico na área de trabalho do MacBook do usuário.")
async def open_document_on_macbook(
    filename: str,
) -> str:
    """Abre um documento no MacBook."""
    logger.info(f"Tool called: open_document_on_macbook(filename='{filename}')")
    
    payload = {
        "command": f"Abrir documento {filename}",
        "action_type": "open_document",
        "payload": {
            "filename": filename
        }
    }
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post("http://localhost:8788/tokyo/desktop-agent-operator/execute", json=payload)
            if resp.status_code == 200:
                return f"O comando para abrir o documento '{filename}' foi enviado ao MacBook com sucesso!"
            else:
                return f"Falha ao enviar comando. Status: {resp.status_code}"
    except Exception as e:
        logger.error(f"Error in open_document_on_macbook: {e}")
        return f"Erro de comunicação: {str(e)}"

@llm.function_tool(description="Captura a tela atual do MacBook do usuário e usa IA visual para ler e descrever o conteúdo, retornando os textos e janelas abertas.")
async def read_macbook_screen() -> str:
    """Tira um print da tela do MacBook e lê seu conteúdo."""
    logger.info("Tool called: read_macbook_screen()")
    
    payload = {
        "command": "Ler tela do computador",
        "action_type": "read_screen",
        "payload": {}
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 1. Dispatch Task
            resp = await client.post("http://localhost:8788/tokyo/desktop-agent-operator/execute", json=payload)
            if resp.status_code != 200:
                return f"Falha ao solicitar leitura da tela. Status: {resp.status_code}"
                
            data = resp.json()
            task_id = data.get("task_id")
            if not task_id:
                return "Falha ao obter ID da tarefa da tela."
                
            # 2. Poll for completion
            logger.info(f"Polling for read_screen task {task_id} completion...")
            max_attempts = 15
            for attempt in range(max_attempts):
                await asyncio.sleep(2) # Wait 2 seconds between polls
                tasks_resp = await client.get("http://localhost:8788/tokyo/desktop-agent/tasks")
                if tasks_resp.status_code == 200:
                    tasks_data = tasks_resp.json()
                    
                    # Check if failed in running or completed
                    completed = tasks_data.get("completed", [])
                    for t in completed:
                        if t.get("task_id") == task_id:
                            if t.get("status") == "completed":
                                image_base64 = t.get("result", {}).get("image_base64")
                                if not image_base64:
                                    return "A tela foi capturada, mas a imagem estava vazia."
                                    
                                # 3. Process with Gemini
                                logger.info("Image received from Mac, analyzing with Gemini...")
                                try:
                                    image_bytes = base64.b64decode(image_base64)
                                    gemini_client = genai.Client()
                                    prompt = "Você está olhando para a tela do MacBook do usuário. Descreva detalhadamente as janelas abertas e leia os textos importantes visíveis. Foque na produtividade e em dizer exatamente onde o usuário está navegando."
                                    
                                    response = gemini_client.models.generate_content(
                                        model='gemini-1.5-pro-latest',
                                        contents=[
                                            prompt,
                                            types.Part.from_bytes(data=image_bytes, mime_type='image/png')
                                        ]
                                    )
                                    return f"Conteúdo da tela lido com sucesso: {response.text}"
                                except Exception as img_e:
                                    logger.error(f"Gemini analysis failed: {img_e}")
                                    return f"Consegui capturar a tela, mas falhei ao analisá-la: {img_e}"
                            else:
                                return "Falha na captura de tela no MacBook."
            return "O MacBook demorou demais para enviar a tela."
    except Exception as e:
        logger.error(f"Error in read_macbook_screen: {e}")
        return f"Erro de comunicação: {str(e)}"
