from datetime import datetime

def handle_get_datetime() -> dict:
    """
    Obtém a data e hora atuais e as retorna em múltiplos formatos.
    Esta é a "lógica de negócio" da ferramenta de data/hora. Ela não sabe
    nada sobre APIs ou HTTP, apenas executa sua tarefa específica.
    """
    now = datetime.now()
    
    # Retornamos um dicionário com diferentes formatos,
    # o que torna a ferramenta mais flexível para quem a consome.
    return {
        "current_datetime_iso": now.isoformat(),
        "data_formatada": now.strftime("%d de %B de %Y"),
        "hora_formatada": now.strftime("%H:%M:%S")
    }