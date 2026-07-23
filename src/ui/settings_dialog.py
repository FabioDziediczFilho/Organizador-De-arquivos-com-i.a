from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, 
    QLineEdit, QComboBox, QCheckBox, QSpinBox, QDoubleSpinBox,
    QPushButton, QLabel, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt, Signal
from typing import Optional

from src.utils.config_manager import ConfigManager
from src.utils.logger import Logger
from .components.styled_widgets import (
    FluentButton, FluentLineEdit, FluentComboBox, FluentCheckBox, 
    FluentSpinBox, FluentDoubleSpinBox, FluentGroupBox, FluentLabel
)


class SettingsDialog(QDialog):
    """Dialog de configurações com PySide6 e Fluent Design."""
    
    # Signal para notificar mudanças
    settings_changed = Signal()
    
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        
        self.config_manager = config_manager
        self.logger = Logger("SettingsDialog")
        
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Configura a UI do dialog."""
        self.setWindowTitle("Configurações")
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # TabWidget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Aba Ollama
        self.ollama_tab = self._create_ollama_tab()
        self.tab_widget.addTab(self.ollama_tab, "Ollama")
        
        # Aba Gemini
        self.gemini_tab = self._create_gemini_tab()
        self.tab_widget.addTab(self.gemini_tab, "Gemini")
        
        # Aba Geral
        self.general_tab = self._create_general_tab()
        self.tab_widget.addTab(self.general_tab, "Geral")
        
        # Botões
        button_layout = QHBoxLayout()
        
        save_btn = FluentButton("Salvar")
        save_btn.clicked.connect(self.save_settings)
        
        cancel_btn = FluentButton("Cancelar", secondary=True)
        cancel_btn.clicked.connect(self.reject)
        
        restore_btn = FluentButton("Restaurar Padrões", secondary=True)
        restore_btn.clicked.connect(self.restore_defaults)
        
        button_layout.addWidget(restore_btn)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _create_ollama_tab(self) -> QWidget:
        """Cria a aba de configurações do Ollama."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Grupo de conexão
        conn_group = FluentGroupBox("Conexão")
        conn_layout = QFormLayout(conn_group)
        
        self.ollama_host = FluentLineEdit()
        conn_layout.addRow("Host:", self.ollama_host)
        
        self.ollama_model = FluentLineEdit()
        conn_layout.addRow("Modelo:", self.ollama_model)
        
        layout.addWidget(conn_group)
        
        # Grupo de configurações
        config_group = FluentGroupBox("Configurações")
        config_layout = QFormLayout(config_group)
        
        self.ollama_timeout = FluentSpinBox()
        self.ollama_timeout.setMinimum(5)
        self.ollama_timeout.setMaximum(300)
        config_layout.addRow("Timeout (s):", self.ollama_timeout)
        
        layout.addWidget(config_group)
        
        layout.addStretch()
        
        return tab
    
    def _create_gemini_tab(self) -> QWidget:
        """Cria a aba de configurações do Gemini."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Grupo de conexão
        conn_group = FluentGroupBox("Conexão")
        conn_layout = QFormLayout(conn_group)
        
        self.gemini_api_key = FluentLineEdit()
        self.gemini_api_key.setEchoMode(QLineEdit.Password)
        conn_layout.addRow("API Key:", self.gemini_api_key)
        
        self.gemini_model = FluentComboBox()
        self.gemini_model.addItems([
            "gemini-3.5-flash",
            "gemini-3.1-flash-lite",
            "gemini-2.0-flash"
        ])
        conn_layout.addRow("Modelo:", self.gemini_model)
        
        layout.addWidget(conn_group)
        
        # Grupo de configurações
        config_group = FluentGroupBox("Configurações")
        config_layout = QFormLayout(config_group)
        
        self.gemini_enabled = FluentCheckBox("Habilitar Gemini AI")
        config_layout.addRow("", self.gemini_enabled)
        
        self.gemini_timeout = FluentSpinBox()
        self.gemini_timeout.setMinimum(5)
        self.gemini_timeout.setMaximum(300)
        config_layout.addRow("Timeout (s):", self.gemini_timeout)
        
        layout.addWidget(config_group)
        
        layout.addStretch()
        
        return tab
    
    def _create_general_tab(self) -> QWidget:
        """Cria a aba de configurações gerais."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Grupo de provedor de IA
        ai_group = FluentGroupBox("Provedor de IA")
        ai_layout = QFormLayout(ai_group)
        
        self.ai_provider = FluentComboBox()
        self.ai_provider.addItems(["ollama", "gemini"])
        ai_layout.addRow("Provedor:", self.ai_provider)
        
        layout.addWidget(ai_group)
        
        # Grupo de interface
        ui_group = FluentGroupBox("Interface")
        ui_layout = QFormLayout(ui_group)
        
        self.show_preview = FluentCheckBox("Mostrar preview de imagens")
        self.show_preview.setChecked(True)
        ui_layout.addRow("", self.show_preview)
        
        self.auto_scan = FluentCheckBox("Auto scan ao selecionar diretório")
        self.auto_scan.setChecked(True)
        ui_layout.addRow("", self.auto_scan)
        
        layout.addWidget(ui_group)
        
        # Grupo de logging
        log_group = FluentGroupBox("Logging")
        log_layout = QFormLayout(log_group)
        
        self.log_level = FluentComboBox()
        self.log_level.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level.setCurrentText("INFO")
        log_layout.addRow("Nível de Log:", self.log_level)
        
        layout.addWidget(log_group)
        
        layout.addStretch()
        
        return tab
    
    def _load_settings(self):
        """Carrega as configurações do ConfigManager."""
        try:
            # Ollama
            self.ollama_host.setText(self.config_manager.get('ollama.host', 'http://localhost:11434'))
            self.ollama_model.setText(self.config_manager.get('ollama.model', 'qwen2-vl:7b'))
            self.ollama_timeout.setValue(self.config_manager.get('ollama.timeout', 30))
            
            # Gemini
            self.gemini_api_key.setText(self.config_manager.get('gemini.api_key', ''))
            self.gemini_model.setCurrentText(self.config_manager.get('gemini.model', 'gemini-3.5-flash'))
            self.gemini_enabled.setChecked(self.config_manager.get('gemini.enabled', False))
            self.gemini_timeout.setValue(self.config_manager.get('gemini.timeout', 30))
            
            # Geral
            self.ai_provider.setCurrentText(self.config_manager.get('ai_provider.selected', 'ollama'))
            self.show_preview.setChecked(self.config_manager.get('ui.show_preview', True))
            self.auto_scan.setChecked(self.config_manager.get('ui.auto_scan', True))
            self.log_level.setCurrentText(self.config_manager.get('logging.level', 'INFO'))
            
            self.logger.info("Configurações carregadas com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações: {str(e)}")
    
    def save_settings(self):
        """Salva as configurações no ConfigManager."""
        try:
            # Ollama
            self.config_manager.set('ollama.host', self.ollama_host.text())
            self.config_manager.set('ollama.model', self.ollama_model.text())
            self.config_manager.set('ollama.timeout', self.ollama_timeout.value())
            
            # Gemini
            self.config_manager.set('gemini.api_key', self.gemini_api_key.text())
            self.config_manager.set('gemini.model', self.gemini_model.currentText())
            self.config_manager.set('gemini.enabled', self.gemini_enabled.isChecked())
            self.config_manager.set('gemini.timeout', self.gemini_timeout.value())
            
            # Geral
            self.config_manager.set('ai_provider.selected', self.ai_provider.currentText())
            self.config_manager.set('ui.show_preview', self.show_preview.isChecked())
            self.config_manager.set('ui.auto_scan', self.auto_scan.isChecked())
            self.config_manager.set('logging.level', self.log_level.currentText())
            
            self.config_manager.save()
            
            self.settings_changed.emit()
            self.logger.info("Configurações salvas com sucesso")
            
            self.accept()
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar configurações: {str(e)}")
    
    def restore_defaults(self):
        """Restaura as configurações padrão."""
        try:
            # Ollama
            self.ollama_host.setText('http://localhost:11434')
            self.ollama_model.setText('qwen2-vl:7b')
            self.ollama_timeout.setValue(30)
            
            # Gemini
            self.gemini_api_key.setText('')
            self.gemini_model.setCurrentText('gemini-3.5-flash')
            self.gemini_enabled.setChecked(False)
            self.gemini_timeout.setValue(30)
            
            # Geral
            self.ai_provider.setCurrentText('ollama')
            self.show_preview.setChecked(True)
            self.auto_scan.setChecked(True)
            self.log_level.setCurrentText('INFO')
            
            self.logger.info("Configurações restauradas para padrão")
            
        except Exception as e:
            self.logger.error(f"Erro ao restaurar padrões: {str(e)}")
