from PySide6.QtCore import QObject, Signal, QThread
from typing import List, Optional
from src.utils.logger import Logger
from src.models.file_model import FileItem, FileListModel
from src.core.file_scanner import scan_directory, get_scan_summary, format_size
from src.core.file_organizer import FileOrganizer
from src.core.batch_renamer import BatchRenamer
import os


class FileScanWorker(QThread):
    """Worker thread para escaneamento de arquivos."""
    
    finished = Signal(list)  # List[FileItem]
    error = Signal(str)
    progress = Signal(int, int)  # current, total
    
    def __init__(self, directory: str):
        super().__init__()
        self.directory = directory
        self.logger = Logger("FileScanWorker")
    
    def run(self):
        """Executa o escaneamento."""
        try:
            file_infos = scan_directory(self.directory)
            self.logger.info(f"Escaneando {len(file_infos)} arquivos")
            
            # Usar dicionários para transferência entre threads (evita problemas de QObject)
            file_data = []
            for file_info in file_infos:
                file_ext = os.path.splitext(file_info.path)[1].lower()
                file_type = "Imagem" if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'] else "Outro"
                
                file_dict = {
                    'name': file_info.name,
                    'path': file_info.path,
                    'size': file_info.size,
                    'category': file_info.category,
                    'file_type': file_type
                }
                file_data.append(file_dict)
            
            self.logger.info(f"Criados {len(file_data)} dicionários de arquivo")
            
            # Emitir lista de dicionários
            self.finished.emit(file_data)
            
        except Exception as e:
            self.logger.error(f"Erro no escaneamento: {e}")
            self.error.emit(str(e))


class FileOperationWorker(QThread):
    """Worker thread para operações de arquivos."""
    
    finished = Signal(bool, str)  # success, message
    error = Signal(str)
    progress = Signal(int, int)  # current, total
    
    def __init__(self, operation: str, **kwargs):
        super().__init__()
        self.operation = operation
        self.kwargs = kwargs
    
    def run(self):
        """Executa a operação de arquivo."""
        try:
            if self.operation == "organize":
                self._organize()
            elif self.operation == "rename":
                self._rename()
            elif self.operation == "move":
                self._move()
            
        except Exception as e:
            self.error.emit(str(e))
    
    def _organize(self):
        """Organiza arquivos por categoria."""
        directory = self.kwargs.get('directory')
        file_paths = self.kwargs.get('file_paths', [])
        
        organizer = FileOrganizer(directory)
        
        for i, file_path in enumerate(file_paths):
            self.progress.emit(i + 1, len(file_paths))
            organizer.organize_file(file_path)
        
        self.finished.emit(True, f"{len(file_paths)} arquivos organizados")
    
    def _rename(self):
        """Renomeia arquivos."""
        directory = self.kwargs.get('directory')
        rename_map = self.kwargs.get('rename_map', {})  # {old_path: new_name}
        
        renamer = BatchRenamer(directory)
        renamed_count = 0
        
        for i, (old_path, new_name) in enumerate(rename_map.items()):
            self.progress.emit(i + 1, len(rename_map))
            extension = os.path.splitext(old_path)[1]
            new_path = renamer.rename_file(old_path, new_name + extension)
            if new_path:
                renamed_count += 1
        
        self.finished.emit(True, f"{renamed_count} arquivos renomeados")
    
    def _move(self):
        """Move arquivos para pasta personalizada."""
        file_paths = self.kwargs.get('file_paths', [])
        target_folder = self.kwargs.get('target_folder')
        
        moved_count = 0
        for i, file_path in enumerate(file_paths):
            self.progress.emit(i + 1, len(file_paths))
            
            filename = os.path.basename(file_path)
            target_path = os.path.join(target_folder, filename)
            
            # Verifica se já existe
            if os.path.exists(target_path):
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(os.path.join(target_folder, f"{base}_{counter}{ext}")):
                    counter += 1
                target_path = os.path.join(target_folder, f"{base}_{counter}{ext}")
            
            os.rename(file_path, target_path)
            moved_count += 1
        
        self.finished.emit(True, f"{moved_count} arquivos movidos")


class FileController(QObject):
    """Controller para operações de arquivos."""
    
    # Signals
    files_scanned = Signal(list)  # List[FileItem]
    scan_error = Signal(str)
    operation_finished = Signal(bool, str)  # success, message
    operation_error = Signal(str)
    progress_updated = Signal(int, int)  # current, total
    status_changed = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.logger = Logger("FileController")
        self._scan_worker: Optional[FileScanWorker] = None
        self._operation_worker: Optional[FileOperationWorker] = None
        self._history: List[dict] = []  # Histórico de operações para undo
    
    def scan_directory(self, directory: str):
        """Escaneia um diretório."""
        try:
            self.status_changed.emit("Escaneando...")
            
            self._scan_worker = FileScanWorker(directory)
            self._scan_worker.finished.connect(self._on_scan_finished)
            self._scan_worker.error.connect(self._on_scan_error)
            self._scan_worker.start()
            
        except Exception as e:
            self.scan_error.emit(str(e))
            self.logger.error(f"Erro ao iniciar escaneamento: {str(e)}")
    
    def _on_scan_finished(self, file_items: List[FileItem]):
        """Callback quando escaneamento termina."""
        self.files_scanned.emit(file_items)
        self.status_changed.emit(f"{len(file_items)} arquivos encontrados")
        self.logger.info(f"Escaneamento concluído: {len(file_items)} arquivos")
    
    def _on_scan_error(self, error: str):
        """Callback quando escaneamento falha."""
        self.scan_error.emit(error)
        self.status_changed.emit("Erro no escaneamento")
        self.logger.error(f"Erro no escaneamento: {error}")
    
    def organize_files(self, directory: str, file_paths: List[str]):
        """Organiza arquivos por categoria."""
        try:
            self.status_changed.emit("Organizando arquivos...")
            
            # Salvar no histórico
            self._add_to_history("organize", directory=directory, file_paths=file_paths)
            
            self._operation_worker = FileOperationWorker("organize", directory=directory, file_paths=file_paths)
            self._operation_worker.finished.connect(self._on_operation_finished)
            self._operation_worker.error.connect(self._on_operation_error)
            self._operation_worker.progress.connect(self.progress_updated.emit)
            self._operation_worker.start()
            
        except Exception as e:
            self.operation_error.emit(str(e))
            self.logger.error(f"Erro ao iniciar organização: {str(e)}")
    
    def rename_files(self, directory: str, rename_map: dict):
        """Renomeia arquivos."""
        try:
            self.status_changed.emit("Renomeando arquivos...")
            
            # Salvar no histórico
            self._add_to_history("rename", directory=directory, rename_map=rename_map)
            
            self._operation_worker = FileOperationWorker("rename", directory=directory, rename_map=rename_map)
            self._operation_worker.finished.connect(self._on_operation_finished)
            self._operation_worker.error.connect(self._on_operation_error)
            self._operation_worker.progress.connect(self.progress_updated.emit)
            self._operation_worker.start()
            
        except Exception as e:
            self.operation_error.emit(str(e))
            self.logger.error(f"Erro ao iniciar renomeamento: {str(e)}")
    
    def move_files(self, file_paths: List[str], target_folder: str):
        """Move arquivos para pasta personalizada."""
        try:
            self.status_changed.emit("Movendo arquivos...")
            
            # Salvar no histórico
            self._add_to_history("move", file_paths=file_paths, target_folder=target_folder)
            
            self._operation_worker = FileOperationWorker("move", file_paths=file_paths, target_folder=target_folder)
            self._operation_worker.finished.connect(self._on_operation_finished)
            self._operation_worker.error.connect(self._on_operation_error)
            self._operation_worker.progress.connect(self.progress_updated.emit)
            self._operation_worker.start()
            
        except Exception as e:
            self.operation_error.emit(str(e))
            self.logger.error(f"Erro ao iniciar movimento: {str(e)}")
    
    def _on_operation_finished(self, success: bool, message: str):
        """Callback quando operação termina."""
        self.operation_finished.emit(success, message)
        self.status_changed.emit("Operação concluída")
        self.logger.info(f"Operação concluída: {message}")
    
    def _on_operation_error(self, error: str):
        """Callback quando operação falha."""
        self.operation_error.emit(error)
        self.status_changed.emit("Erro na operação")
        self.logger.error(f"Erro na operação: {error}")
    
    def _add_to_history(self, operation: str, **kwargs):
        """Adiciona operação ao histórico."""
        history_item = {
            'operation': operation,
            'kwargs': kwargs,
            'timestamp': None  # TODO: Adicionar timestamp
        }
        self._history.append(history_item)
        self.logger.info(f"Operação adicionada ao histórico: {operation}")
    
    def undo_last_operation(self) -> bool:
        """Desfaz a última operação."""
        if not self._history:
            return False
        
        try:
            history_item = self._history.pop()
            operation = history_item['operation']
            kwargs = history_item['kwargs']
            
            # Implementar undo para cada operação
            if operation == "rename":
                # TODO: Implementar undo de renomeamento
                pass
            elif operation == "move":
                # TODO: Implementar undo de movimento
                pass
            elif operation == "organize":
                # TODO: Implementar undo de organização
                pass
            
            self.logger.info(f"Operação desfeita: {operation}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao desfazer operação: {str(e)}")
            return False
    
    def get_history(self) -> List[dict]:
        """Retorna o histórico de operações."""
        return self._history.copy()
    
    def clear_history(self):
        """Limpa o histórico."""
        self._history.clear()
        self.logger.info("Histórico limpo")
    
    def cancel(self):
        """Cancela operação em andamento."""
        if self._scan_worker and self._scan_worker.isRunning():
            self._scan_worker.terminate()
            self._scan_worker.wait()
            self.status_changed.emit("Escaneamento cancelado")
            self.logger.info("Escaneamento cancelado")
        
        if self._operation_worker and self._operation_worker.isRunning():
            self._operation_worker.terminate()
            self._operation_worker.wait()
            self.status_changed.emit("Operação cancelada")
            self.logger.info("Operação cancelada")
