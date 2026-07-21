import os 
import shutil
from typing import List, Dict, Any
from .file_scanner import FileInfo, format_size
from .extensions import get_file_category


class FileOrganizer:
    """Classe Responsavel por organizar arquivos em diretorios"""

    def __init__(self, base_directory: str):
        """
        Inicializa o organizador de arquivos
        
        Args:
            base_directory: Diretorio base onde os arquivos serao organizados
        """
        self.base_directory = base_directory
        self.operations_log = []
    
    def create_category_directory(self, category: str) -> str:
        """
        Cria um diretorio para uma categoria especifica
        
        Args:
            category: Nome da categoria
            
        Returns:
            Caminho do diretorio criado
        """
        category_directory = os.path.join(self.base_directory, category)
        os.makedirs(category_directory, exist_ok=True)
        self.operations_log.append(f"Criado diretorio: {category_directory}")
        return category_directory

    def move_file_to_category(self, file_info: FileInfo, new_name: str = None) -> str:
        """
        Move um arquivo para o diretório da sua categoria.
        
        Args:
            file_info: Objeto FileInfo com informações do arquivo
            new_name: Novo nome para o arquivo (opcional)
            
        Returns:
            Caminho de destino do arquivo movido
        """
        # Cria o diretório da categoria se não existir
        category_dir = self.create_category_directory(file_info.category)
        
        # Define o nome do arquivo (usa o novo nome se fornecido)
        filename = new_name if new_name else file_info.name
        destination = os.path.join(category_dir, filename)
        
        # Verifica se o arquivo de destino já existe
        if os.path.exists(destination):
            # Adiciona um número ao nome para evitar sobrescrita
            base_name = os.path.splitext(filename)[0]
            extension = file_info.extension
            counter = 1
            while os.path.exists(destination):
                new_filename = f"{base_name}_{counter}{extension}"
                destination = os.path.join(category_dir, new_filename)
                counter += 1
        
        # Move o arquivo
        shutil.move(file_info.path, destination)
        
        # Registra a operação no log
        self.operations_log.append(f"Movido: {file_info.path} -> {destination}")
        
        return destination
