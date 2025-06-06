import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env para a sessão atual
load_dotenv()

def get_intent_and_params(user_command: str) -> dict:
    """
    Usa a API do Gemini para extrair a intenção e os parâmetros de um comando de usuário.

    Args:
        user_command: O comando em linguagem natural digitado pelo usuário.

    Returns:
        Um dicionário com a "intent" e os "parameters", ou um dicionário de erro.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "A chave da API do Gemini não foi encontrada. Verifique o arquivo .env."}

    try:
        genai.configure(api_key=api_key)

        generation_config = {
            "temperature": 0.2,
            "response_mime_type": "application/json", # Pede ao Gemini para forçar uma saída JSON
        }

        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro-latest",
            generation_config=generation_config
        )

        # O prompt é a parte mais importante. Ele é a instrução detalhada
        # que ensina o modelo a se comportar como nosso tradutor.
        prompt = f"""
        Analise o comando do usuário e o traduza para uma estrutura JSON. Sua única saída deve ser um objeto JSON válido, sem nenhum texto ou explicação adicional.

        As intenções (intent) e parâmetros (parameters) possíveis são:

        1.  Adicionar uma tarefa:
            - intent: "ADD_TASK"
            - parameters: {{ "description": "string", "due_date": "string (opcional, formato AAAA-MM-DD)" }}

        2.  Listar tarefas:
            - intent: "LIST_TASKS"
            - parameters: {{ "status": "string (opcional, 'pendente' ou 'concluída')" }}

        3.  Concluir uma tarefa:
            - intent: "COMPLETE_TASK"
            - parameters: {{ "task_id": "integer" }}

        4.  Listar arquivos:
            - intent: "LIST_FILES"
            - parameters: {{ "subfolder": "string (opcional)", "extension_filter": "string (opcional, ex: '.txt')" }}

        5.  Obter data e hora:
            - intent: "GET_DATETIME"
            - parameters: {{}}

        6.  Intenção desconhecida (saudações, perguntas gerais, etc.):
            - intent: "UNKNOWN"
            - parameters: {{}}

        Exemplos de Tradução:
        - Usuário: "Preciso comprar leite" -> {{"intent": "ADD_TASK", "parameters": {{"description": "comprar leite", "due_date": null}}}}
        - Usuário: "o que eu tenho que fazer?" -> {{"intent": "LIST_TASKS", "parameters": {{}}}}
        - Usuário: "finalizar tarefa 2" -> {{"intent": "COMPLETE_TASK", "parameters": {{"task_id": 2}}}}
        - Usuário: "me mostre os arquivos na pasta docs" -> {{"intent": "LIST_FILES", "parameters": {{"subfolder": "docs", "extension_filter": null}}}}
        - Usuário: "que horas são?" -> {{"intent": "GET_DATETIME", "parameters": {{}}}}
        - Usuário: "bom dia" -> {{"intent": "UNKNOWN", "parameters": {{}}}}

        Comando do Usuário para analisar:
        "{user_command}"
        """

        response = model.generate_content(prompt)
        
        # A API do Gemini, quando instruída a retornar JSON, o coloca em response.text
        json_response = json.loads(response.text)
        
        return json_response

    except json.JSONDecodeError:
        return {"error": f"O modelo não retornou um JSON válido. Resposta: {response.text}"}
    except Exception as e:
        return {"error": f"Ocorreu um erro ao chamar a API do Gemini: {e}"}