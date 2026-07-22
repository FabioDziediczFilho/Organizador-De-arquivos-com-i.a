import os
import re
import shutil
from typing import Dict, List, Tuple
from collections import defaultdict
from ..utils.logger import Logger


class BatchRenamer:
    """Sistema de renomeamento e organização em lote por padrão de nome."""
    
    def __init__(self, base_directory: str):
        """
        Inicializa o renomeador em lote.
        
        Args:
            base_directory: Diretório base para operações
        """
        self.base_directory = base_directory
        self.logger = Logger("BatchRenamer")
        self.logger.info(f"BatchRenamer inicializado em {base_directory}")
    
    def group_files_by_pattern(self, file_paths: List[str]) -> Dict[str, List[str]]:
        """
        Agrupa arquivos por padrão de nome similar.
        
        Args:
            file_paths: Lista de caminhos de arquivos
            
        Returns:
            Dicionário com padrão -> lista de arquivos
        """
        groups = defaultdict(list)
        
        for file_path in file_paths:
            filename = os.path.basename(file_path)
            # Remove extensão
            name_without_ext = os.path.splitext(filename)[0]
            
            # Extrai padrão base (remove números e caracteres especiais no final)
            pattern = self._extract_pattern(name_without_ext)
            
            if pattern:
                groups[pattern].append(file_path)
            else:
                groups["outros"].append(file_path)
        
        self.logger.info(f"Arquivos agrupados em {len(groups)} padrões")
        return dict(groups)
    
    def _extract_pattern(self, filename: str) -> str:
        """
        Extrai o padrão base do nome do arquivo.
        
        Args:
            filename: Nome do arquivo sem extensão
            
        Returns:
            Padrão base do nome
        """
        # Remove números no final (ex: "foto123" -> "foto")
        pattern = re.sub(r'\d+$', '', filename)
        
        # Remove caracteres especiais no final
        pattern = re.sub(r'[_\-\.]+$', '', pattern)
        
        # Remove espaços extras
        pattern = pattern.strip()
        
        # Se o padrão ficar muito curto, usa o nome original
        if len(pattern) < 3:
            return filename
        
        return pattern.lower()
    
    def suggest_folder_name(self, pattern: str) -> str:
        """
        Sugere um nome de pasta baseado no padrão.
        
        Args:
            pattern: Padrão do nome do arquivo
            
        Returns:
            Nome sugerido para a pasta
        """
        # Converte para formato de pasta (primeira letra maiúscula)
        folder_name = pattern.capitalize()
        
        # Substitui underscores por espaços
        folder_name = folder_name.replace('_', ' ')
        
        # Remove espaços extras
        folder_name = ' '.join(folder_name.split())
        
        return folder_name
    
    def organize_by_pattern(self, file_paths: List[str], dry_run: bool = False) -> Dict[str, any]:
        """
        Organiza arquivos por padrão de nome em pastas separadas.
        
        Args:
            file_paths: Lista de caminhos de arquivos
            dry_run: Se True, apenas simula sem mover arquivos
            
        Returns:
            Dicionário com resultado da operação
        """
        results = {
            'groups': {},
            'moved': [],
            'errors': [],
            'dry_run': dry_run
        }
        
        # Agrupa arquivos por padrão
        groups = self.group_files_by_pattern(file_paths)
        
        for pattern, files in groups.items():
            if pattern == "outros":
                continue
            
            # Sugere nome da pasta
            folder_name = self.suggest_folder_name(pattern)
            folder_path = os.path.join(self.base_directory, folder_name)
            
            results['groups'][folder_name] = {
                'pattern': pattern,
                'count': len(files),
                'files': files
            }
            
            # Cria a pasta se não for dry run
            if not dry_run:
                try:
                    os.makedirs(folder_path, exist_ok=True)
                    self.logger.info(f"Pasta criada: {folder_path}")
                except Exception as e:
                    self.logger.error(f"Erro ao criar pasta {folder_path}: {str(e)}")
                    continue
            
            # Move os arquivos
            for file_path in files:
                try:
                    filename = os.path.basename(file_path)
                    destination = os.path.join(folder_path, filename)
                    
                    # Trata duplicatas
                    if os.path.exists(destination):
                        base_name = os.path.splitext(filename)[0]
                        extension = os.path.splitext(filename)[1]
                        counter = 1
                        while os.path.exists(destination):
                            new_filename = f"{base_name}_{counter}{extension}"
                            destination = os.path.join(folder_path, new_filename)
                            counter += 1
                    
                    if not dry_run:
                        shutil.move(file_path, destination)
                        self.logger.info(f"Movido: {file_path} -> {destination}")
                    
                    results['moved'].append({
                        'original': file_path,
                        'destination': destination,
                        'folder': folder_name
                    })
                    
                except Exception as e:
                    error_msg = f"Erro ao mover {file_path}: {str(e)}"
                    self.logger.error(error_msg)
                    results['errors'].append({
                        'file': file_path,
                        'error': str(e)
                    })
        
        self.logger.info(f"Organização concluída: {len(results['moved'])} arquivos movidos, {len(results['errors'])} erros")
        return results
    
    def rename_file(self, file_path: str, new_name: str) -> str:
        """
        Renomeia um arquivo individualmente.
        
        Args:
            file_path: Caminho do arquivo
            new_name: Novo nome (com ou sem extensão)
            
        Returns:
            Novo caminho do arquivo
        """
        try:
            directory = os.path.dirname(file_path)
            extension = os.path.splitext(file_path)[1]
            
            # Se o novo nome não tem extensão, usa a original
            if not new_name.endswith(extension):
                new_name = new_name + extension
            
            new_path = os.path.join(directory, new_name)
            
            # Trata duplicatas
            if os.path.exists(new_path):
                base_name = os.path.splitext(new_name)[0]
                counter = 1
                while os.path.exists(new_path):
                    new_name = f"{base_name}_{counter}{extension}"
                    new_path = os.path.join(directory, new_name)
                    counter += 1
            
            os.rename(file_path, new_path)
            self.logger.info(f"Renomeado: {file_path} -> {new_path}")
            
            return new_path
            
        except Exception as e:
            self.logger.error(f"Erro ao renomear {file_path}: {str(e)}")
            raise
    
    def batch_rename(self, file_mappings: Dict[str, str]) -> Dict[str, any]:
        """
        Renomeia múltiplos arquivos de uma vez.
        
        Args:
            file_mappings: Dicionário com caminho_original -> novo_nome
            
        Returns:
            Dicionário com resultado da operação
        """
        results = {
            'renamed': [],
            'errors': []
        }
        
        for original_path, new_name in file_mappings.items():
            try:
                new_path = self.rename_file(original_path, new_name)
                results['renamed'].append({
                    'original': original_path,
                    'new': new_path
                })
            except Exception as e:
                results['errors'].append({
                    'file': original_path,
                    'error': str(e)
                })
        
        self.logger.info(f"Renomeamento em lote concluído: {len(results['renamed'])} arquivos, {len(results['errors'])} erros")
        return results
