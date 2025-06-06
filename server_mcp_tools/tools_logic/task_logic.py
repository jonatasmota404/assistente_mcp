# A sintaxe com '..' é uma importação relativa. Significa: "volte um diretório
# a partir da minha localização atual (tool_logic) e, a partir de lá,
# encontre a pasta 'data_storage' e importe o módulo 'db_manager'".
from ..data_storage import db_manager

def handle_add_task(description: str, due_date: str | None) -> dict:
    """
    Lida com a lógica de negócio para adicionar uma nova tarefa.

    Retorna:
        Um dicionário indicando o sucesso e a tarefa criada.
    """
    try:
        # Chama a função do db_manager para inserir a tarefa no banco
        task_id = db_manager.add_task_db(description, due_date)
        
        # Após criar, busca a tarefa completa para retorná-la na resposta
        all_tasks = db_manager.get_tasks_db()
        # Encontra a tarefa recém-criada na lista
        new_task = next((task for task in all_tasks if task['id'] == task_id), None)
        
        if new_task:
            return {"success": True, "message": "Tarefa adicionada com sucesso.", "task": new_task}
        else:
            # Isso seria um caso muito raro, mas é bom ter uma segurança
            return {"success": False, "message": "Erro ao recuperar a tarefa após a criação.", "task": None}
    except Exception as e:
        # Captura qualquer erro que possa ocorrer no nível do banco de dados
        return {"success": False, "message": f"Erro ao adicionar tarefa: {e}", "task": None}

def handle_list_tasks(status: str | None) -> list[dict]:
    """
    Lida com a lógica de negócio para listar tarefas.
    Neste caso, é um simples repasse para a função do db_manager.
    """
    return db_manager.get_tasks_db(status=status)

def handle_update_task_status(task_id: int, new_status: str) -> dict:
    """
    Lida com a lógica de negócio para atualizar o status de uma tarefa.

    Retorna:
        Um dicionário indicando o sucesso e a tarefa atualizada.
    """
    # Chama a função de atualização do db_manager
    updated_task = db_manager.update_task_status_db(task_id, new_status)
    
    # Verifica o resultado para construir uma resposta amigável
    if updated_task:
        return {"success": True, "message": f"Tarefa {task_id} atualizada para '{new_status}'.", "task": updated_task}
    else:
        return {"success": False, "message": f"Tarefa com ID {task_id} não encontrada.", "task": None}
    

def handle_complete_task_by_description(description_hint: str) -> dict:
    """
    Encontra uma tarefa pendente que corresponda a uma descrição e a marca como concluída.
    """
    pending_tasks = db_manager.get_tasks_db(status='pendente')
    
    best_match = None
    # Lógica de correspondência simples: procura a primeira tarefa que contém a dica.
    for task in pending_tasks:
        if description_hint.lower() in task['description'].lower():
            best_match = task
            break # Encontramos uma, podemos parar
            
    if not best_match:
        return {"success": False, "message": f"Nenhuma tarefa pendente encontrada com a descrição parecida com '{description_hint}'.", "task": None}
        
    # Se encontramos, usamos a função de atualização existente
    task_id_to_complete = best_match['id']
    updated_task = db_manager.update_task_status_db(task_id_to_complete, "concluída")
    
    if updated_task:
        return {"success": True, "message": f"Tarefa '{updated_task['description']}' marcada como concluída.", "task": updated_task}
    else:
        # Caso raro, mas para segurança
        return {"success": False, "message": "Erro ao atualizar a tarefa encontrada.", "task": None}