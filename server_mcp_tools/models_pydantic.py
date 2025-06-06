from pydantic import BaseModel, Field
from typing import List, Optional

# BaseModel é a classe base do Pydantic da qual todos os modelos herdam.
# Field nos permite adicionar mais informações aos campos, como descrições e valores padrão.

# --- Modelos para a Ferramenta de Tarefas ---

class AddTaskRequest(BaseModel):
    """
    Define a estrutura esperada no corpo de uma requisição para adicionar uma tarefa.
    """
    description: str = Field(..., description="A descrição detalhada da tarefa a ser criada.")
    due_date: Optional[str] = Field(None, description="Data de vencimento opcional (formato sugerido: AAAA-MM-DD).")

class UpdateTaskStatusRequest(BaseModel):
    """

    Define a estrutura para atualizar o status de uma tarefa.
    """
    new_status: str = Field(..., description="O novo status da tarefa (ex: 'concluída', 'em andamento').")

class TaskResponse(BaseModel):
    """
    Define a estrutura padrão para retornar informações de uma tarefa.
    Isso garante que as respostas da API sejam sempre consistentes.
    """
    id: int
    description: str
    due_date: Optional[str]
    status: str

class TaskActionResponse(BaseModel):
    """
    Uma resposta genérica para ações de tarefa (criar, atualizar), indicando o resultado.
    """
    success: bool
    message: str
    task: Optional[TaskResponse] = None # Retorna o objeto da tarefa se a ação for bem-sucedida

# --- Modelos para a Ferramenta de Sistema de Arquivos ---

class FileListResponse(BaseModel):
    """
    Define a estrutura para a resposta da listagem de arquivos.
    """
    success: bool
    path_queried: str
    files: List[str]

class FileOperationResponse(BaseModel):
    """
    Uma resposta genérica para outras operações de arquivo que possamos adicionar no futuro.
    """
    success: bool
    message: str
    details: Optional[str] = None

# --- Modelo para a Ferramenta de Informações do Sistema ---
# (Poderíamos criar modelos aqui, mas para obter a data e hora,
# a resposta pode ser um dicionário simples, então não é estritamente necessário agora)