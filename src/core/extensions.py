"""
Módulo de Extensões de Arquivos

Este módulo define as extensões de arquivo suportadas pelo organizador
e fornece funções para categorizar arquivos baseado em suas extensões.
"""

from typing import Dict, List

# Extensões suportadas e suas categorias
EXTENSIONS_MAP: Dict[str, str] = {
    # Imagens
    '.jpg': 'imagem',
    '.jpeg': 'imagem',
    '.png': 'imagem',
    # Vídeos
    '.mp4': 'video'
}

# Mapeamento reverso: categoria -> lista de extensões
CATEGORY_MAP: Dict[str, List[str]] = {
    'imagem': ['.jpg', '.jpeg', '.png'],
    'video': ['.mp4']
}


def get_file_category(file_path: str) -> str:
    """
    Retorna a categoria do arquivo baseado na extensão.
    
    Args:
        file_path: Caminho do arquivo (ex: 'foto.jpg')
        
    Returns:
        Categoria do arquivo ('imagem', 'video' ou 'desconhecido')
        
    Example:
        >>> get_file_category('foto.jpg')
        'imagem'
        >>> get_file_category('video.mp4')
        'video'
        >>> get_file_category('documento.pdf')
        'desconhecido'
    """
    import os
    
    # Extrai a extensão do arquivo
    _, ext = os.path.splitext(file_path)
    
    # Converte para minúsculo para garantir case-insensitive
    ext = ext.lower()
    
    # Retorna a categoria ou 'desconhecido' se não estiver no mapa
    return EXTENSIONS_MAP.get(ext, 'desconhecido')


def get_supported_extensions() -> List[str]:
    """
    Retorna lista de todas as extensões suportadas.
    
    Returns:
        Lista de extensões (ex: ['.jpg', '.jpeg', '.png', '.mp4'])
        
    Example:
        >>> get_supported_extensions()
        ['.jpg', '.jpeg', '.png', '.mp4']
    """
    return list(EXTENSIONS_MAP.keys())


def get_extensions_by_category(category: str) -> List[str]:
    """
    Retorna todas as extensões de uma categoria específica.
    
    Args:
        category: Categoria desejada ('imagem' ou 'video')
        
    Returns:
        Lista de extensões da categoria ou lista vazia se categoria não existir
        
    Example:
        >>> get_extensions_by_category('imagem')
        ['.jpg', '.jpeg', '.png']
        >>> get_extensions_by_category('video')
        ['.mp4']
    """
    return CATEGORY_MAP.get(category.lower(), [])


def is_supported(file_path: str) -> bool:
    """
    Verifica se um arquivo é suportado pelo organizador.
    
    Args:
        file_path: Caminho do arquivo
        
    Returns:
        True se a extensão é suportada, False caso contrário
        
    Example:
        >>> is_supported('foto.jpg')
        True
        >>> is_supported('documento.pdf')
        False
    """
    return get_file_category(file_path) != 'desconhecido'


def get_all_categories() -> List[str]:
    """
    Retorna todas as categorias disponíveis.
    
    Returns:
        Lista de categorias (ex: ['imagem', 'video'])
        
    Example:
        >>> get_all_categories()
        ['imagem', 'video']
    """
    return list(CATEGORY_MAP.keys())


if __name__ == "__main__":
    # Testes rápidos quando executado diretamente
    print("=== Testes do Módulo de Extensões ===")
    
    # Testar get_file_category
    print(f"\nget_file_category('foto.jpg'): {get_file_category('foto.jpg')}")
    print(f"get_file_category('video.mp4'): {get_file_category('video.mp4')}")
    print(f"get_file_category('doc.pdf'): {get_file_category('doc.pdf')}")
    
    # Testar get_supported_extensions
    print(f"\nget_supported_extensions(): {get_supported_extensions()}")
    
    # Testar get_extensions_by_category
    print(f"\nget_extensions_by_category('imagem'): {get_extensions_by_category('imagem')}")
    print(f"get_extensions_by_category('video'): {get_extensions_by_category('video')}")
    
    # Testar is_supported
    print(f"\nis_supported('foto.jpg'): {is_supported('foto.jpg')}")
    print(f"is_supported('doc.pdf'): {is_supported('doc.pdf')}")
    
    # Testar get_all_categories
    print(f"\nget_all_categories(): {get_all_categories()}")
