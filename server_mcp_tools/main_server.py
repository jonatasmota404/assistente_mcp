from fastapi import FastAPI, HTTPException, Body, Query
from pathlib import Path
import uvicorn

# --- Importando todos os nossos módulos ---

# Importando a lógica de cada ferramenta
from .tools_logic import system_info_logic, task_logic, file_system_logic

# Importando os modelos Pydantic para validação
from .models_pydantic import (
    AddTaskRequest, UpdateTaskStatusRequest, TaskActionResponse,
    FileListResponse, TaskResponse
)

# Importando o gerenciador de banco de dados para a inicialização
from .data_storage import db_manager

# --- Configuração Inicial da Aplicação FastAPI ---

app = FastAPI(
    title="Servidor de Ferramentas Locais MCP",
    description="Expõe ferramentas de utilitários locais (tarefas, arquivos, sistema) via uma API RESTful.",
    version="1.0.0",
)

# Define o caminho absoluto e seguro para o nosso workspace de arquivos.
# Path(__file__).resolve().parent garante que o caminho é sempre relativo
# à localização deste arquivo.
SAFE_WORKSPACE_PATH = Path(__file__).resolve().parent / "data_storage" / "mcp_workspace_demo"

# --- Eventos de Ciclo de Vida do Servidor ---

@app.on_event("startup")
def on_startup():
    """
    Função executada uma única vez quando o servidor FastAPI inicia.
    Ideal para configurações iniciais.
    """
    # Garante que o diretório de workspace exista. Se não existir, ele é criado.
    SAFE_WORKSPACE_PATH.mkdir(exist_ok=True)
    print(f"Workspace seguro garantido em: {SAFE_WORKSPACE_PATH}")
    
    # Chama a função para inicializar o banco de dados e criar a tabela de tarefas.
    db_manager.initialize_db() #

# --- Funções Auxiliares de Segurança ---

def resolve_safe_path(subfolder: str | None) -> Path:
    """
    Resolve um caminho de subpasta de forma segura, garantindo que ele esteja
    contido DENTRO do nosso SAFE_WORKSPACE_PATH.
    """
    if not subfolder:
        return SAFE_WORKSPACE_PATH
    
    # resolve() remove '..' e normaliza o caminho
    resolved_path = (SAFE_WORKSPACE_PATH / subfolder).resolve()

    # A verificação de segurança crucial: o caminho resolvido ainda está
    # dentro do nosso diretório seguro?
    if SAFE_WORKSPACE_PATH in resolved_path.parents or resolved_path == SAFE_WORKSPACE_PATH:
        return resolved_path
    
    # Se a verificação falhar, o usuário tentou acessar um local proibido.
    raise HTTPException(status_code=400, detail="Acesso a caminho fora do workspace não é permitido.")

# --- Endpoints da API ---

@app.get("/", summary="Endpoint raiz da API")
def read_root():
    """Endpoint principal que apenas retorna uma mensagem de boas-vindas."""
    return {"message": "Bem-vindo ao Servidor de Ferramentas Locais MCP!"}

# -- Endpoints de Ferramentas do Sistema --

@app.get("/tools/system/datetime", summary="Obtém a data e hora atuais")
def get_current_datetime():
    """Retorna a data e hora atuais do servidor, chamando a lógica correspondente."""
    return system_info_logic.handle_get_datetime()

# -- Endpoints de Ferramentas de Tarefas --

@app.post("/tools/tasks/add", response_model=TaskActionResponse, summary="Adiciona uma nova tarefa")
def add_task(task_request: AddTaskRequest):
    """
    Cria uma nova tarefa. O FastAPI valida o corpo da requisição
    automaticamente usando o modelo AddTaskRequest.
    """
    result = task_logic.handle_add_task(task_request.description, task_request.due_date)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@app.get("/tools/tasks/list", response_model=list[TaskResponse], summary="Lista tarefas existentes")
def list_tasks(status: str | None = Query(None, description="Filtre as tarefas por status (ex: 'pendente', 'concluída')")):
    """
    Retorna uma lista de tarefas. O parâmetro 'status' é opcional e vem da URL.
    """
    return task_logic.handle_list_tasks(status)

@app.post("/tools/tasks/{task_id}/update_status", response_model=TaskActionResponse, summary="Atualiza o status de uma tarefa")
def update_task_status(task_id: int, request_body: UpdateTaskStatusRequest):
    """
    Atualiza o status de uma tarefa específica. O ID vem do caminho da URL
    e o novo status vem do corpo da requisição.
    """
    result = task_logic.handle_update_task_status(task_id, request_body.new_status)
    if not result["success"]:
        if "não encontrada" in result["message"]:
            raise HTTPException(status_code=404, detail=result["message"])
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    return result

# -- Endpoints de Ferramentas de Arquivos --

@app.get("/tools/files/list_workspace", response_model=FileListResponse, summary="Lista arquivos no workspace seguro")
def list_workspace_files(
    subfolder: str | None = Query(None, description="Subpasta dentro do workspace para listar."),
    extension_filter: str | None = Query(None, description="Filtra arquivos por extensão (ex: '.txt').")
):
    """Lista arquivos dentro de uma subpasta segura do workspace."""
    try:
        # Primeiro, valida o caminho para garantir a segurança
        safe_target_path = resolve_safe_path(subfolder)
        # Depois, chama a lógica para listar os arquivos
        return file_system_logic.handle_list_files(safe_target_path, extension_filter)
    except HTTPException as e:
        raise e # Repassa a exceção de caminho inválido
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao listar arquivos: {e}")

# --- Ponto de Execução do Servidor (para Debug) ---
if __name__ == "__main__":
    print("Iniciando o servidor Uvicorn para desenvolvimento...")
    # Permite rodar o servidor diretamente com 'python main_server.py'
    uvicorn.run(app, host="127.0.0.1", port=8000)