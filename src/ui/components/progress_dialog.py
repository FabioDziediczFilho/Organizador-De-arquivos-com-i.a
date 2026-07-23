from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton, QTextEdit, QCheckBox
from PySide6.QtCore import Qt, Signal
from typing import Optional
from .styled_widgets import FluentButton, FluentLabel


class ProgressDialog(QDialog):
    """Dialog de progresso com opção de cancelamento."""
    
    # Signals
    cancelled = Signal()
    
    def __init__(self, title: str = "Processando", parent=None):
        super().__init__(parent)
        
        self._title = title
        self._cancellable = True
        self._show_details = False
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura a UI."""
        self.setWindowTitle(self._title)
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # Label de status
        self.status_label = FluentLabel("Iniciando...", subheading=True)
        layout.addWidget(self.status_label)
        
        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Label de progresso (ex: 50/100)
        self.progress_label = FluentLabel("0/0")
        self.progress_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_label)
        
        # Checkbox para mostrar detalhes
        self.details_checkbox = QCheckBox("Mostrar detalhes")
        self.details_checkbox.stateChanged.connect(self._toggle_details)
        layout.addWidget(self.details_checkbox)
        
        # Área de detalhes (inicialmente oculta)
        self.details_area = QTextEdit()
        self.details_area.setReadOnly(True)
        self.details_area.setMaximumHeight(150)
        self.details_area.setVisible(False)
        self.details_area.setStyleSheet("""
            QTextEdit {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #4A4A4A;
                font-family: Consolas, monospace;
                font-size: 9pt;
            }
        """)
        layout.addWidget(self.details_area)
        
        # Botão cancelar
        self.cancel_button = FluentButton("Cancelar", secondary=True)
        self.cancel_button.clicked.connect(self._on_cancel)
        layout.addWidget(self.cancel_button)
    
    def _toggle_details(self, state):
        """Mostra/esconde detalhes."""
        self._show_details = (state == Qt.Checked)
        self.details_area.setVisible(self._show_details)
        self.adjustSize()
    
    def _on_cancel(self):
        """Callback quando cancelar é clicado."""
        if self._cancellable:
            self.cancelled.emit()
            self.close()
    
    def set_progress(self, current: int, total: int, message: str = ""):
        """Define o progresso."""
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)
            self.progress_label.setText(f"{current}/{total} ({percentage}%)")
        else:
            self.progress_bar.setValue(0)
            self.progress_label.setText(f"{current}/?")
        
        if message:
            self.status_label.setText(message)
    
    def add_detail(self, message: str):
        """Adiciona uma mensagem aos detalhes."""
        if self._show_details:
            self.details_area.append(message)
        else:
            # Armazenar mesmo se não estiver visível
            self.details_area.append(message)
    
    def set_cancellable(self, cancellable: bool):
        """Define se o diálogo pode ser cancelado."""
        self._cancellable = cancellable
        self.cancel_button.setEnabled(cancellable)
    
    def set_title(self, title: str):
        """Define o título do diálogo."""
        self.setWindowTitle(title)
        self._title = title
    
    def reset(self):
        """Reseta o diálogo."""
        self.progress_bar.setValue(0)
        self.progress_label.setText("0/0")
        self.status_label.setText("Iniciando...")
        self.details_area.clear()
        self.cancel_button.setEnabled(self._cancellable)
