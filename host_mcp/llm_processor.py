import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env para a sessão atual
load_dotenv()

from datetime import datetime, timedelta

def get_intent_and_params(user_command: str) -> dict:
    """
    Usa a API do Gemini para extrair a intenção e os parâmetros de um comando de usuário.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "A chave da API do Gemini não foi encontrada. Verifique o arquivo .env."}

    try:
        genai.configure(api_key=api_key)

        generation_config = {
            "temperature": 0.2,
            "response_mime_type": "application/json",
        }

        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro-latest",
            generation_config=generation_config
        )
        
        # A MÁGICA ACONTECE AQUI: informamos a data atual para o modelo
        data_de_hoje = datetime.now().strftime('%Y-%m-%d')

        prompt = f"""
        Analise o comando do usuário e o traduza para uma estrutura JSON. Sua única saída deve ser um objeto JSON válido, sem nenhum texto ou explicação adicional.
        A data de hoje é {data_de_hoje}. Se o usuário mencionar uma data relativa (como "hoje", "amanhã" ou "depois de amanhã"), calcule a data correspondente no formato AAAA-MM-DD e a use no campo 'due_date'.

        As intenções (intent) e parâmetros (parameters) possíveis são:
        
        1. Adicionar uma tarefa:
            - intent: "ADD_TASK"
            - parameters: {{ "description": "string", "due_date": "string (opcional, formato AAAA-MM-DD)" }}

        2. Listar tarefas:
            - intent: "LIST_TASKS"
            - parameters: {{ "status": "string (opcional, 'pendente' ou 'concluída')" }}

        3. Concluir uma tarefa por ID:
            - intent: "COMPLETE_TASK"
            - parameters: {{ "task_id": "integer" }}

        4. Listar arquivos:
            - intent: "LIST_FILES"
            - parameters: {{ "subfolder": "string (opcional)", "extension_filter": "string (opcional, ex: '.txt')" }}

        5. Obter data e hora:
            - intent: "GET_DATETIME"
            - parameters: {{}}

        6. Intenção desconhecida (saudações, perguntas gerais, etc.):
            - intent: "UNKNOWN"
            - parameters: {{}}
        
        7. Concluir uma tarefa por descrição:
            - intent: "COMPLETE_TASK_BY_DESCRIPTION"
            - parameters: {{ "description_hint": "string" }}

        Exemplos de Tradução (considerando hoje={data_de_hoje}):
        - Usuário: "amanhã tenho que pintar um quadro" -> {{"intent": "ADD_TASK", "parameters": {{"description": "pintar um quadro", "due_date": "{(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')}"}}}}
        - Usuário: "finalizar tarefa 2" -> {{"intent": "COMPLETE_TASK", "parameters": {{"task_id": 2}}}}
        - Usuário: "já terminei de comprar pão" -> {{"intent": "COMPLETE_TASK_BY_DESCRIPTION", "parameters": {{"description_hint": "comprar pão"}}}}
       
        Comando do Usuário para analisar:
        "{user_command}"
        """

        response = model.generate_content(prompt)
        json_response = json.loads(response.text)
        return json_response

    except json.JSONDecodeError:
        return {"error": f"O modelo não retornou um JSON válido. Resposta: {response.text}"}
    except Exception as e:
        return {"error": f"Ocorreu um erro ao chamar a API do Gemini: {e}"}