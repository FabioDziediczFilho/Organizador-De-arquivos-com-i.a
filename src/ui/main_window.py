from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QSplitter, QFileDialog, QStatusBar, QMenuBar, QMenu
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction
from typing import Optional
import os

from src.controllers.main_controller import MainController
from src.controllers.ai_controller import AIController
from src.controllers.file_controller import FileController
from src.models.file_model import FileItem
from src.utils.logger import Logger
from src.utils.config_manager import ConfigManager

from .components.styled_widgets import FluentButton, FluentLineEdit, FluentLabel, FluentCard
from .components.file_tree import FileTreeWidget
from .components.image_preview import ImagePreviewWidget
from .components.chat_widget import ChatWidget
from .components.progress_dialog import ProgressDialog
from .settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    """Janela principal do Organizador de Arquivos com PySide6."""
    
    def __init__(self):
        super().__init__()
        
        self.logger = Logger("MainWindow")
        
        # Controllers
        self.main_controller = MainController()
        self.ai_controller = AIController()
        self.file_controller = FileController()
        
        # Configurações
        self.config_manager = ConfigManager()
        
        # Estado
        self._current_directory = ""
        
        # Setup UI
        self._setup_window()
        self._setup_menu()
        self._setup_status_bar()
        self._setup_ui()
        self._connect_signals()
        self._load_stylesheet()
        
        self.logger.info("Janela principal inicializada com sucesso")
    
    def _setup_window(self):
        """Configura a janela principal."""
        self.setWindowTitle("Organizador de Arquivos com IA")
        self.setMinimumSize(1200, 700)
        self.resize(1400, 900)
    
    def _setup_menu(self):
        """Configura o menu."""
        menubar = self.menuBar()
        
        # Menu Arquivo
        file_menu = menubar.addMenu("Arquivo")
        
        select_dir_action = QAction("Selecionar Diretório", self)
        select_dir_action.setShortcut("Ctrl+O")
        select_dir_action.triggered.connect(self.select_directory)
        file_menu.addAction(select_dir_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Sair", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Editar
        edit_menu = menubar.addMenu("Editar")
        
        settings_action = QAction("Configurações", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.open_settings)
        edit_menu.addAction(settings_action)
        
        # Menu IA
        ai_menu = menubar.addMenu("IA")
        
        check_connection_action = QAction("Verificar Conexão", self)
        check_connection_action.triggered.connect(self.check_ai_connection)
        ai_menu.addAction(check_connection_action)
        
        # Menu Ajuda
        help_menu = menubar.addMenu("Ajuda")
        
        about_action = QAction("Sobre", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def _setup_status_bar(self):
        """Configura a barra de status."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Pronto")
    
    def _setup_ui(self):
        """Configura a UI principal."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # TabWidget principal
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Aba Organização
        self.organization_tab = self._create_organization_tab()
        self.tab_widget.addTab(self.organization_tab, "Organização")
        
        # Aba IA
        self.ai_tab = self._create_ai_tab()
        self.tab_widget.addTab(self.ai_tab, "IA")
        
        # Aba Histórico
        self.history_tab = self._create_history_tab()
        self.tab_widget.addTab(self.history_tab, "Histórico")
    
    def _create_organization_tab(self) -> QWidget:
        """Cria a aba de organização."""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # Splitter horizontal
        splitter = QSplitter(Qt.Horizontal)
        
        # Painel esquerdo - File Tree
        left_panel = FluentCard()
        left_layout = QVBoxLayout(left_panel)
        
        # Controles de diretório
        dir_layout = QHBoxLayout()
        dir_label = FluentLabel("Diretório:")
        self.dir_entry = FluentLineEdit()
        select_btn = FluentButton("Selecionar", secondary=True)
        select_btn.clicked.connect(self.select_directory)
        
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.dir_entry, 1)
        dir_layout.addWidget(select_btn)
        left_layout.addLayout(dir_layout)
        
        # Botões de ação
        action_layout = QHBoxLayout()
        
        scan_btn = FluentButton("Escanear")
        scan_btn.clicked.connect(self.scan_files)
        
        organize_btn = FluentButton("Organizar por Categoria", secondary=True)
        organize_btn.clicked.connect(self.organize_files)
        
        move_btn = FluentButton("Mover para Pasta", secondary=True)
        move_btn.clicked.connect(self.move_to_folder)
        
        action_layout.addWidget(scan_btn)
        action_layout.addWidget(organize_btn)
        action_layout.addWidget(move_btn)
        left_layout.addLayout(action_layout)
        
        # File Tree
        self.file_tree = FileTreeWidget()
        left_layout.addWidget(self.file_tree)
        
        splitter.addWidget(left_panel)
        
        # Painel direito - Preview
        right_panel = FluentCard()
        right_layout = QVBoxLayout(right_panel)
        
        right_layout.addWidget(FluentLabel("Preview", heading=True))
        
        self.image_preview = ImagePreviewWidget()
        right_layout.addWidget(self.image_preview)
        
        splitter.addWidget(right_panel)
        
        # Configurar proporções
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)
        
        return tab
    
    def _create_ai_tab(self) -> QWidget:
        """Cria a aba de IA."""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # Splitter horizontal
        splitter = QSplitter(Qt.Horizontal)
        
        # Painel esquerdo - File Tree
        left_panel = FluentCard()
        left_layout = QVBoxLayout(left_panel)
        
        left_layout.addWidget(FluentLabel("Arquivos", heading=True))
        
        self.ai_file_tree = FileTreeWidget()
        left_layout.addWidget(self.ai_file_tree)
        
        splitter.addWidget(left_panel)
        
        # Painel central - Preview
        center_panel = FluentCard()
        center_layout = QVBoxLayout(center_panel)
        
        center_layout.addWidget(FluentLabel("Preview", heading=True))
        
        self.ai_image_preview = ImagePreviewWidget()
        center_layout.addWidget(self.ai_image_preview)
        
        splitter.addWidget(center_panel)
        
        # Painel direito - Chat
        right_panel = FluentCard()
        right_layout = QVBoxLayout(right_panel)
        
        right_layout.addWidget(FluentLabel("Chat com IA", heading=True))
        
        # Botões de ação IA
        ai_action_layout = QHBoxLayout()
        
        check_btn = FluentButton("Verificar Conexão", secondary=True)
        check_btn.clicked.connect(self.check_ai_connection)
        
        analyze_btn = FluentButton("Analisar Imagem")
        analyze_btn.clicked.connect(self.analyze_image)
        
        classify_btn = FluentButton("Classificar", secondary=True)
        classify_btn.clicked.connect(self.classify_files)
        
        ai_action_layout.addWidget(check_btn)
        ai_action_layout.addWidget(analyze_btn)
        ai_action_layout.addWidget(classify_btn)
        right_layout.addLayout(ai_action_layout)
        
        # Chat Widget
        self.chat_widget = ChatWidget()
        right_layout.addWidget(self.chat_widget)
        
        splitter.addWidget(right_panel)
        
        # Configurar proporções
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 1)
        
        layout.addWidget(splitter)
        
        return tab
    
    def _create_history_tab(self) -> QWidget:
        """Cria a aba de histórico."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        layout.addWidget(FluentLabel("Histórico de Operações", heading=True))
        
        # TODO: Implementar lista de histórico
        history_label = FluentLabel("Histórico de operações será implementado aqui.", subheading=True)
        history_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(history_label)
        
        return tab
    
    def _connect_signals(self):
        """Conecta os signals."""
        # Main Controller
        self.main_controller.directory_changed.connect(self._on_directory_changed)
        self.main_controller.files_scanned.connect(self._on_files_scanned)
        self.main_controller.status_changed.connect(self._on_status_changed)
        
        # File Controller
        self.file_controller.files_scanned.connect(self._on_files_scanned)
        self.file_controller.scan_error.connect(self._on_scan_error)
        self.file_controller.operation_finished.connect(self._on_operation_finished)
        self.file_controller.operation_error.connect(self._on_operation_error)
        self.file_controller.progress_updated.connect(self._on_progress_updated)
        self.file_controller.status_changed.connect(self._on_status_changed)
        
        # AI Controller
        self.ai_controller.response_received.connect(self._on_ai_response)
        self.ai_controller.batch_response_received.connect(self._on_ai_batch_response)
        self.ai_controller.error_occurred.connect(self._on_ai_error)
        self.ai_controller.status_changed.connect(self._on_status_changed)
        self.ai_controller.progress_updated.connect(self._on_progress_updated)
        
        # File Tree
        self.file_tree.file_selected.connect(self._on_file_selected)
        self.ai_file_tree.file_selected.connect(self._on_ai_file_selected)
        
        # Chat Widget
        self.chat_widget.message_sent.connect(self._on_chat_message)
    
    def _load_stylesheet(self):
        """Carrega o stylesheet Fluent Design."""
        try:
            style_path = os.path.join(
                os.path.dirname(__file__), 
                "styles", 
                "fluent_dark.qss"
            )
            
            if os.path.exists(style_path):
                with open(style_path, 'r', encoding='utf-8') as f:
                    self.setStyleSheet(f.read())
                self.logger.info("Stylesheet carregado com sucesso")
            else:
                self.logger.warning(f"Stylesheet não encontrado: {style_path}")
                
        except Exception as e:
            self.logger.error(f"Erro ao carregar stylesheet: {str(e)}")
    
    # Actions
    def select_directory(self):
        """Seleciona um diretório."""
        directory = QFileDialog.getExistingDirectory(self, "Selecione o diretório")
        if directory:
            self._current_directory = directory
            self.dir_entry.setText(directory)
            self.main_controller.set_directory(directory)
            self.scan_files()
    
    def scan_files(self):
        """Escaneia arquivos do diretório."""
        if not self._current_directory:
            self.status_bar.showMessage("Selecione um diretório primeiro")
            return
        
        self.file_controller.scan_directory(self._current_directory)
    
    def organize_files(self):
        """Organiza arquivos por categoria."""
        selected_files = self.file_tree.get_selected_files()
        if not selected_files:
            self.status_bar.showMessage("Selecione arquivos para organizar")
            return
        
        file_paths = [f.path for f in selected_files]
        self.file_controller.organize_files(self._current_directory, file_paths)
    
    def move_to_folder(self):
        """Move arquivos para pasta personalizada."""
        selected_files = self.file_tree.get_selected_files()
        if not selected_files:
            self.status_bar.showMessage("Selecione arquivos para mover")
            return
        
        target_folder = QFileDialog.getExistingDirectory(self, "Selecione a pasta de destino")
        if target_folder:
            file_paths = [f.path for f in selected_files]
            self.file_controller.move_files(file_paths, target_folder)
    
    def check_ai_connection(self):
        """Verifica conexão com IA."""
        provider = self.config_manager.get('ai_provider.selected', 'ollama')
        
        kwargs = {}
        if provider == 'gemini':
            kwargs['api_key'] = self.config_manager.get('gemini.api_key')
            kwargs['model'] = self.config_manager.get('gemini.model', 'gemini-3.5-flash')
        else:
            kwargs['host'] = self.config_manager.get('ollama.host', 'http://localhost:11434')
            kwargs['model'] = self.config_manager.get('ollama.model', 'qwen2-vl:7b')
        
        connected = self.ai_controller.check_connection(provider, **kwargs)
        
        if connected:
            self.chat_widget.add_system_message(f"Conectado ao {provider}")
        else:
            self.chat_widget.add_system_message(f"Falha na conexão com {provider}")
    
    def analyze_image(self):
        """Analisa imagem selecionada com IA."""
        file_item = self.ai_file_tree.get_selected_file()
        if not file_item or not file_item.is_image:
            self.chat_widget.add_system_message("Selecione uma imagem para analisar")
            return
        
        provider = self.config_manager.get('ai_provider.selected', 'ollama')
        
        kwargs = {}
        if provider == 'gemini':
            kwargs['api_key'] = self.config_manager.get('gemini.api_key')
            kwargs['model'] = self.config_manager.get('gemini.model', 'gemini-3.5-flash')
        else:
            kwargs['host'] = self.config_manager.get('ollama.host', 'http://localhost:11434')
            kwargs['model'] = self.config_manager.get('ollama.model', 'qwen2-vl:7b')
        
        self.ai_controller.analyze_image(file_item.path, provider, **kwargs)
    
    def classify_files(self):
        """Classifica arquivos selecionados com IA."""
        selected_files = self.ai_file_tree.get_selected_files()
        if not selected_files:
            self.chat_widget.add_system_message("Selecione arquivos para classificar")
            return
        
        file_paths = [f.path for f in selected_files if f.is_image]
        if not file_paths:
            self.chat_widget.add_system_message("Selecione imagens para classificar")
            return
        
        provider = self.config_manager.get('ai_provider.selected', 'ollama')
        
        kwargs = {}
        if provider == 'gemini':
            kwargs['api_key'] = self.config_manager.get('gemini.api_key')
            kwargs['model'] = self.config_manager.get('gemini.model', 'gemini-3.5-flash')
        else:
            kwargs['host'] = self.config_manager.get('ollama.host', 'http://localhost:11434')
            kwargs['model'] = self.config_manager.get('ollama.model', 'qwen2-vl:7b')
        
        self.ai_controller.classify_batch(file_paths, provider, **kwargs)
    
    def open_settings(self):
        """Abre janela de configurações."""
        settings_dialog = SettingsDialog(self.config_manager, self)
        settings_dialog.settings_changed.connect(self._on_settings_changed)
        settings_dialog.exec()
    
    def _on_settings_changed(self):
        """Callback quando configurações mudam."""
        self.chat_widget.add_system_message("Configurações atualizadas")
        self.logger.info("Configurações atualizadas")
    
    def show_about(self):
        """Mostra diálogo sobre."""
        # TODO: Implementar AboutDialog
        self.chat_widget.add_system_message("Sobre será implementado em breve")
    
    # Signal handlers
    def _on_directory_changed(self, directory: str):
        """Callback quando diretório muda."""
        self._current_directory = directory
        self.dir_entry.setText(directory)
    
    def _on_files_scanned(self, file_items):
        """Callback quando arquivos são escaneados."""
        self.file_tree.load_files(file_items)
        self.ai_file_tree.load_files(file_items)
        self.main_controller.get_file_model().clear()
        for file_item in file_items:
            self.main_controller.get_file_model().add_file(file_item)
    
    def _on_scan_error(self, error: str):
        """Callback quando escaneamento falha."""
        self.status_bar.showMessage(f"Erro: {error}")
    
    def _on_operation_finished(self, success: bool, message: str):
        """Callback quando operação termina."""
        if success:
            self.chat_widget.add_system_message(f"✅ {message}")
        else:
            self.chat_widget.add_system_message(f"❌ {message}")
    
    def _on_operation_error(self, error: str):
        """Callback quando operação falha."""
        self.chat_widget.add_system_message(f"❌ Erro: {error}")
    
    def _on_progress_updated(self, current: int, total: int):
        """Callback quando progresso é atualizado."""
        self.status_bar.showMessage(f"Progresso: {current}/{total}")
    
    def _on_status_changed(self, status: str):
        """Callback quando status muda."""
        self.status_bar.showMessage(status)
    
    def _on_file_selected(self, file_item: FileItem):
        """Callback quando seleção de arquivo muda."""
        print(f"[DEBUG] _on_file_selected chamado com file_item: {type(file_item)}")
        
        if file_item is None:
            print("[DEBUG] file_item é None, limpando preview")
            self.image_preview.clear()
            return
        
        try:
            print(f"[DEBUG] file_item.is_image: {file_item.is_image if hasattr(file_item, 'is_image') else 'N/A'}")
            if file_item.is_image:
                print(f"[DEBUG] Carregando imagem: {file_item.path if hasattr(file_item, 'path') else 'N/A'}")
                self.image_preview.load_image(file_item)
            else:
                print("[DEBUG] Não é imagem, limpando preview")
                self.image_preview.clear()
        except Exception as e:
            print(f"[ERROR] Erro ao carregar preview: {e}")
            import traceback
            traceback.print_exc()
            self.logger.error(f"Erro ao carregar preview: {e}")
            self.image_preview.clear()
    
    def _on_ai_file_selected(self, file_item: FileItem):
        """Callback quando seleção de arquivo na aba IA muda."""
        print(f"[DEBUG] _on_ai_file_selected chamado com file_item: {type(file_item)}")
        
        if file_item is None:
            print("[DEBUG] file_item é None, limpando preview IA")
            self.ai_image_preview.clear()
            return
        
        try:
            print(f"[DEBUG] file_item.is_image: {file_item.is_image if hasattr(file_item, 'is_image') else 'N/A'}")
            if file_item.is_image:
                print(f"[DEBUG] Carregando imagem IA: {file_item.path if hasattr(file_item, 'path') else 'N/A'}")
                self.ai_image_preview.load_image(file_item)
            else:
                print("[DEBUG] Não é imagem, limpando preview IA")
                self.ai_image_preview.clear()
        except Exception as e:
            print(f"[ERROR] Erro ao carregar preview IA: {e}")
            import traceback
            traceback.print_exc()
            self.logger.error(f"Erro ao carregar preview IA: {e}")
            self.ai_image_preview.clear()
    
    def _on_ai_response(self, response):
        """Callback quando resposta da IA é recebida."""
        if response.is_error:
            self.chat_widget.add_system_message(f"❌ Erro: {response.error_message}")
        else:
            self.chat_widget.add_message(response.text, is_user=False)
    
    def _on_ai_batch_response(self, responses):
        """Callback quando respostas em lote são recebidas."""
        for response in responses:
            if not response.is_error:
                self.chat_widget.add_system_message(f"Classificado: {response.category}")
    
    def _on_ai_error(self, error: str):
        """Callback quando erro de IA ocorre."""
        self.chat_widget.add_system_message(f"❌ Erro IA: {error}")
    
    def _on_chat_message(self, message: str):
        """Callback quando mensagem de chat é enviada."""
        provider = self.config_manager.get('ai_provider.selected', 'ollama')
        
        kwargs = {}
        if provider == 'gemini':
            kwargs['api_key'] = self.config_manager.get('gemini.api_key')
            kwargs['model'] = self.config_manager.get('gemini.model', 'gemini-3.5-flash')
        else:
            kwargs['host'] = self.config_manager.get('ollama.host', 'http://localhost:11434')
            kwargs['model'] = self.config_manager.get('ollama.model', 'qwen2-vl:7b')
        
        # Verificar se há imagem selecionada
        file_item = self.ai_file_tree.get_selected_file()
        image_path = file_item.path if file_item and file_item.is_image else None
        
        self.ai_controller.chat(message, provider, image_path=image_path, **kwargs)
