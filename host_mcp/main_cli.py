import sys
from llm_processor import get_intent_and_params
from mcp_clients import local_utils_client

# --- Funções Auxiliares para Impressão ---

def print_tasks(tasks):
    """Imprime uma lista de tarefas de forma formatada."""
    if not isinstance(tasks, list):
        print("\n[Assistente] Resposta inesperada do servidor ao listar tarefas.")
        return
        
    if not tasks:
        print("\n[Assistente] Nenhuma tarefa encontrada.")
        return
        
    print("\n--- Suas Tarefas ---")
    for task in tasks:
        status_icon = "✅" if task.get('status') == 'concluída' else "⏳"
        due_date = f" (Vencimento: {task.get('due_date')})" if task.get('due_date') else ""
        print(f"{status_icon} ID {task.get('id')}: {task.get('description')}{due_date}")
    print("--------------------")

def print_files(response):
    """Imprime uma lista de arquivos de forma formatada."""
    if not response.get("success"):
        print(f"\n[Assistente] Erro ao listar arquivos: {response.get('path_queried')}")
        return

    files = response.get("files", [])
    if not files:
        print(f"\n[Assistente] Nenhum arquivo encontrado em '{response.get('path_queried')}'.")
        return
    
    print(f"\n--- Arquivos em '{response.get('path_queried')}' ---")
    for file_name in files:
        print(f"📄 {file_name}")
    print("---------------------------------")

# --- Função Principal ---

def main():
    """Loop principal da interface de linha de comando (CLI)."""
    print("--- Assistente Local de Organização e Utilitários ---")
    print("Digite seu comando ou 'sair' para terminar.")

    while True:
        try:
            command = input("\n[Você] > ")
            if command.lower() in ["sair", "exit", "quit"]:
                print("[Assistente] Até logo!")
                break

            # 1. Obter intenção e parâmetros do LLM
            intent_data = get_intent_and_params(command)

            if "error" in intent_data:
                print(f"[Assistente] Erro no processamento do comando: {intent_data['error']}")
                continue

            intent = intent_data.get("intent")
            params = intent_data.get("parameters", {})
            
            print(f"🧠 (Debug: Intenção='{intent}', Parâmetros={params})") # Mensagem de debug

            # 2. Roteador de Intenções: Chamar a ferramenta apropriada
            response = None
            if intent == "ADD_TASK":
                response = local_utils_client.call_add_task(**params)
                if response and response.get("success"):
                    print(f"\n[Assistente] ✅ Tarefa '{response['task']['description']}' adicionada com sucesso!")
                else:
                    print(f"\n[Assistente] ❌ Erro ao adicionar tarefa: {response.get('message')}")

            elif intent == "LIST_TASKS":
                response = local_utils_client.call_list_tasks(**params)
                print_tasks(response)

            elif intent == "COMPLETE_TASK":
                task_id = params.get("task_id")
                if task_id:
                    response = local_utils_client.call_update_task_status(task_id, "concluída")
                    if response and response.get("success"):
                        print(f"\n[Assistente] ✅ Tarefa {task_id} marcada como concluída!")
                    else:
                        print(f"\n[Assistente] ❌ Erro: {response.get('message') or response.get('error')}")
                else:
                    print("[Assistente] Por favor, especifique o ID da tarefa que deseja concluir.")
            
            elif intent == "COMPLETE_TASK_BY_DESCRIPTION":
                response = local_utils_client.call_complete_task_by_description(**params)
                if response and response.get("success"):
                    print(f"\n[Assistente] ✅ Tarefa '{response['task']['description']}' marcada como concluída!")
                else:
                    print(f"\n[Assistente] ❌ Erro: {response.get('message') or response.get('error')}")

            elif intent == "LIST_FILES":
                response = local_utils_client.call_list_files(**params)
                print_files(response)

            elif intent == "GET_DATETIME":
                response = local_utils_client.call_get_datetime()
                if response and not response.get("error"):
                    print(f"\n[Assistente] 🗓️  Hoje é {response.get('data_formatada')}, {response.get('hora_formatada')}.")
                else:
                     print(f"\n[Assistente] ❌ Erro ao obter a data: {response.get('error')}")

            elif intent == "UNKNOWN":
                print("[Assistente] Desculpe, não entendi o que você quis dizer. Tente um comando relacionado a tarefas ou arquivos.")

            else:
                print(f"[Assistente] A intenção '{intent}' não é reconhecida pelo sistema.")

        except (KeyboardInterrupt, EOFError):
            print("\n[Assistente] Encerrando de forma forçada. Até logo!")
            sys.exit(0)
        except Exception as e:
            print(f"\n[Assistente] Ocorreu um erro inesperado: {e}")


if __name__ == "__main__":
    main()