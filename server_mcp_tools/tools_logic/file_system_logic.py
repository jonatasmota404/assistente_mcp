import os
from pathlib import Path

def handle_list_files(target_path: Path, extension_filter: str | None) -> dict:
    """
    Lida com a listagem de arquivos em um diretório-alvo.

    Importante: Esta função assume que o 'target_path' já foi validado
    como um caminho seguro pela camada da API antes de ser passado para cá.

    Args:
        target_path: O caminho (objeto Path) do diretório a ser listado.
        extension_filter: Uma string para filtrar arquivos por extensão (ex: '.txt').

    Returns:
        Um dicionário com o resultado da operação.
    """
    # Verifica se o caminho realmente existe e é um diretório
    if not target_path.exists() or not target_path.is_dir():
        return {
            "success": False, 
            "path_queried": str(target_path), 
            "files": []
        }
    
    files_found = []
    # Itera sobre todos os itens no diretório-alvo
    for item in target_path.iterdir():
        # Verifica se o item é um arquivo
        if item.is_file():
            # Se um filtro de extensão foi fornecido...
            if extension_filter:
                # ...verifica se o nome do arquivo termina com o filtro.
                if item.name.lower().endswith(extension_filter.lower()):
                    files_found.append(item.name)
            else:
                # Se não há filtro, adiciona todos os arquivos.
                files_found.append(item.name)
    
    return {
        "success": True, 
        "path_queried": str(target_path), 
        "files": files_found
    }