from PySide6.QtCore import QObject, Signal
from typing import Optional
from src.utils.config_manager import ConfigManager
from src.utils.logger import Logger
from src.models.file_model import FileListModel
from src.models.ai_model import AIStatus


class MainController(QObject):
    """Controller principal que coordena UI e lógica de negócio."""

    # Signals para notificar a UI
    directory_changed = Signal(str)
    files_scanned = Signal(int)
    status_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.logger = Logger("MainController")
        self.config_manager = ConfigManager()

        # Modelos
        self.file_model = FileListModel()
        self.ai_status = AIStatus()

        # Estado
        self._current_directory = ""
        self._is_scanning = False

        # Carregar configurações
        self._load_configurations()

    def _load_configurations(self):
        """Carrega configurações iniciais."""
        try:
            provider = self.config_manager.get('ai_provider.selected', 'ollama')
            self.ai_status.provider = provider

            if provider == 'gemini':
                model = self.config_manager.get('gemini.model', 'gemini-3.5-flash')
            else:
                model = self.config_manager.get('ollama.model', 'qwen2-vl:7b')

            self.ai_status.model = model
            self.logger.info(f"Configurações carregadas: provider={provider}, model={model}")

        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações: {str(e)}")

    @property
    def current_directory(self) -> str:
        """Retorna o diretório atual."""
        return self._current_directory

    def set_directory(self, directory: str):
        """Define o diretório atual."""
        if self._current_directory != directory:
            self._current_directory = directory
            self.directory_changed.emit(directory)
            self.logger.info(f"Diretório alterado: {directory}")

    def is_scanning(self) -> bool:
        """Verifica se está escaneando."""
        return self._is_scanning

    def set_scanning(self, scanning: bool):
        """Define estado de escaneamento."""
        self._is_scanning = scanning
        if scanning:
            self.status_changed.emit("Escaneando...")
        else:
            self.status_changed.emit("Pronto")

    def get_config(self, key: str, default=None):
        """Retorna uma configuração."""
        return self.config_manager.get(key, default)

    def set_config(self, key: str, value):
        """Define uma configuração."""
        self.config_manager.set(key, value)
        self.config_manager.save()
        self.logger.info(f"Configuração alterada: {key}={value}")

    def save_config(self):
        """Salva configurações."""
        self.config_manager.save()
        self.logger.info("Configurações salvas")

    def update_ai_status(self, is_connected: bool = None, is_processing: bool = None,
                        last_error: str = None):
        """Atualiza status da IA."""
        if is_connected is not None:
            self.ai_status.is_connected = is_connected
        if is_processing is not None:
            self.ai_status.is_processing = is_processing
        if last_error is not None:
            self.ai_status.last_error = last_error

    def get_file_model(self) -> FileListModel:
        """Retorna o modelo de arquivos."""
        return self.file_model

    def get_ai_status(self) -> AIStatus:
        """Retorna o status da IA."""
        return self.ai_status
