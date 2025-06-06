import sqlite3
from pathlib import Path

# Define o caminho para o nosso arquivo de banco de dados.
# Path(__file__).parent aponta para a pasta atual (data_storage), garantindo que
# o caminho esteja sempre correto, não importa de onde o script seja chamado.
DB_FILE = Path(__file__).parent / "local_assistant_data.db"

def get_db_connection():
    """
    Cria e retorna uma conexão com o banco de dados SQLite.
    A conexão é configurada para retornar linhas como dicionários.
    """
    conn = sqlite3.connect(DB_FILE)
    # Com 'row_factory', podemos acessar os dados por nome da coluna (ex: task['description'])
    # em vez de por índice (ex: task[1]), o que deixa o código mais legível.
    conn.row_factory = sqlite3.Row 
    return conn

def initialize_db():
    """
    Inicializa o banco de dados. Cria a tabela 'tasks' se ela não existir.
    Esta função será chamada uma única vez, quando o servidor FastAPI iniciar.
    """
    print(f"Verificando e inicializando o banco de dados em: {DB_FILE}")
    conn = get_db_connection()
    cursor = conn.cursor()
    # Usamos "IF NOT EXISTS" para que o comando não dê erro se a tabela já existir.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            due_date TEXT,
            status TEXT NOT NULL DEFAULT 'pendente'
        );
    """)
    conn.commit()
    conn.close()
    print("Banco de dados pronto para uso.")

# --- Funções CRUD (Create, Read, Update, Delete) para Tarefas ---

def add_task_db(description: str, due_date: str | None) -> int:
    """
    Adiciona uma nova tarefa ao banco de dados e retorna o ID da nova tarefa.

    Args:
        description: A descrição da tarefa.
        due_date: A data de vencimento (opcional).

    Returns:
        O ID da tarefa que foi recém-criada.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    # Usamos '?' para evitar injeção de SQL, uma prática de segurança essencial.
    cursor.execute(
        "INSERT INTO tasks (description, due_date) VALUES (?, ?)",
        (description, due_date)
    )
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def get_tasks_db(status: str | None = None) -> list[dict]:
    """
    Busca tarefas no banco de dados.

    Args:
        status: Se fornecido, filtra as tarefas por este status (ex: 'pendente').

    Returns:
        Uma lista de dicionários, onde cada dicionário representa uma tarefa.
    """
    conn = get_db_connection()
    query = "SELECT id, description, due_date, status FROM tasks"
    params = []
    if status:
        query += " WHERE status = ?"
        params.append(status)
    
    tasks_rows = conn.execute(query, tuple(params)).fetchall()
    conn.close()
    # Converte a lista de objetos 'Row' em uma lista de dicionários padrão.
    return [dict(task) for task in tasks_rows]

def update_task_status_db(task_id: int, new_status: str) -> dict | None:
    """
    Atualiza o status de uma tarefa específica.

    Args:
        task_id: O ID da tarefa a ser atualizada.
        new_status: O novo status para a tarefa (ex: 'concluída').

    Returns:
        Um dicionário representando a tarefa atualizada, ou None se a tarefa não for encontrada.
    """
    conn = get_db_connection()
    
    # Primeiro, executa o UPDATE
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET status = ? WHERE id = ?",
        (new_status, task_id)
    )
    conn.commit()
    
    # Verifica se alguma linha foi de fato alterada
    if cursor.rowcount == 0:
        conn.close()
        return None # Tarefa não encontrada

    # Se foi alterada, busca a tarefa atualizada para retorná-la
    updated_task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    
    return dict(updated_task) if updated_task else None