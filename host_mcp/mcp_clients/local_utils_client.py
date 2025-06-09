import requests
import json

# A URL base do nosso servidor. Se você rodar em outra porta, altere aqui.
SERVER_BASE_URL = "http://localhost:8000"

def call_get_datetime():
    """Chama o endpoint para obter a data e hora do servidor."""
    try:
        response = requests.get(f"{SERVER_BASE_URL}/tools/system/datetime")
        response.raise_for_status() # Lança um erro para status 4xx/5xx
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Erro de conexão com o servidor: {e}"}

def call_add_task(description: str, due_date: str | None = None):
    """Chama o endpoint para adicionar uma nova tarefa."""
    try:
        payload = {"description": description, "due_date": due_date}
        response = requests.post(f"{SERVER_BASE_URL}/tools/tasks/add", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Erro de conexão com o servidor: {e}"}

def call_list_tasks(status: str | None = None):
    """Chama o endpoint para listar tarefas, com um filtro opcional."""
    try:
        params = {}
        if status:
            params['status'] = status
        
        response = requests.get(f"{SERVER_BASE_URL}/tools/tasks/list", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Erro de conexão com o servidor: {e}"}

def call_update_task_status(task_id: int, new_status: str):
    """Chama o endpoint para atualizar o status de uma tarefa."""
    try:
        payload = {"new_status": new_status}
        response = requests.post(f"{SERVER_BASE_URL}/tools/tasks/{task_id}/update_status", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Erro de conexão com o servidor: {e}"}

def call_list_files(subfolder: str | None = None, extension_filter: str | None = None):
    """Chama o endpoint para listar arquivos, com filtros opcionais."""
    try:
        params = {}
        if subfolder:
            params['subfolder'] = subfolder
        if extension_filter:
            params['extension_filter'] = extension_filter

        response = requests.get(f"{SERVER_BASE_URL}/tools/files/list_workspace", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Erro de conexão com o servidor: {e}"}


def call_complete_task_by_description(description_hint: str):
    """Chama o endpoint para completar uma tarefa por descrição."""
    try:
        payload = {"description_hint": description_hint}
        response = requests.post(f"{SERVER_BASE_URL}/tools/tasks/complete_by_description", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Erro de conexão com o servidor: {e}"}