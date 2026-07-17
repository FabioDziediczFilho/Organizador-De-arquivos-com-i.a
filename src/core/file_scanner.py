import os 
from typing import List, Dict, Any
from pathlib import Path
from .extensions import is_supported, get_file_category

class FileInfo:
    """Classe para armazenar informações sobre um arquivo."""
    
    def __init__(self, path: str, size: int, category: str):
        self.path = path
        self.size = size
        self.category = category
        self.name = os.path.basename(path)
        self.extension = Path(path).suffix.lower()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "size": self.size,
            "category": self.category,
            "name": self.name,
            "extension": self.extension
        }
    
    def __repr__(self):
        return f"FileInfo(path='{self.path}', category='{self.category}', size={self.size})"

def scan_directory(directory: str, recursive: bool = True) -> List[FileInfo]:
    """
    Escaneia um diretório e retorna todos os arquivos suportados.
    
    Args:
        directory: Caminho do diretório para escanear
        recursive: Se True, escaneia subdiretórios também
        
    Returns:
        Lista de objetos FileInfo com os arquivos encontrados
    """
    if not os.path.isdir(directory):
        raise ValueError(f"Diretório não existe: {directory}")
    
    supported_files = []
    
    if recursive:
        # Escaneia recursivamente (inclui subpastas)
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if is_supported(file_path):
                    file_info = FileInfo(file_path, os.path.getsize(file_path), get_file_category(file_path))
                    supported_files.append(file_info)
    else:
        # Escaneia apenas o diretório raiz
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path) and is_supported(file_path):
                file_info = FileInfo(file_path, os.path.getsize(file_path), get_file_category(file_path))
                supported_files.append(file_info)
    
    return supported_files