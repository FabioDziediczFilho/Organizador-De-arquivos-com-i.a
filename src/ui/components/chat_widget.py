from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QScrollArea
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QTextCursor, QColor, QFont
from typing import Optional, List
from datetime import datetime
from .styled_widgets import FluentButton, FluentLineEdit


class ChatMessage:
    """Representa uma mensagem no chat."""
    
    def __init__(self, text: str, is_user: bool = True, timestamp: Optional[datetime] = None):
        self.text = text
        self.is_user = is_user
        self.timestamp = timestamp or datetime.now()
    
    def to_html(self) -> str:
        """Converte mensagem para HTML."""
        bg_color = "#0078D4" if self.is_user else "#3D3D3D"
        text_color = "#FFFFFF"
        align = "right" if self.is_user else "left"
        
        time_str = self.timestamp.strftime("%H:%M")
        
        html = f"""
        <div style="margin: 8px; text-align: {align};">
            <div style="display: inline-block; background-color: {bg_color}; color: {text_color}; 
                        padding: 10px 15px; border-radius: 8px; max-width: 70%; text-align: left;">
                {self.text}
            </div>
            <div style="font-size: 8pt; color: #888888; margin-top: 4px;">{time_str}</div>
        </div>
        """
        return html


class ChatWidget(QWidget):
    """Widget de chat com IA."""
    
    # Signals
    message_sent = Signal(str)  # message
    message_received = Signal(str)  # message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._messages: List[ChatMessage] = []
        self._is_processing = False
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura a UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Área de mensagens
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: none;
                padding: 10px;
            }
        """)
        layout.addWidget(self.chat_area)
        
        # Área de input
        input_layout = QVBoxLayout()
        
        self.input_field = FluentLineEdit("Digite sua mensagem...")
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        
        # Botão enviar
        self.send_button = FluentButton("Enviar")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
    
    def send_message(self):
        """Envia uma mensagem."""
        if self._is_processing:
            return
        
        message = self.input_field.text().strip()
        if not message:
            return
        
        # Adicionar mensagem do usuário
        self.add_message(message, is_user=True)
        self.message_sent.emit(message)
        
        # Limpar input
        self.input_field.clear()
        
        # Marcar como processando
        self._is_processing = True
        self.send_button.setEnabled(False)
        self.send_button.setText("Enviando...")
    
    def add_message(self, text: str, is_user: bool = True):
        """Adiciona uma mensagem ao chat."""
        message = ChatMessage(text, is_user)
        self._messages.append(message)
        
        # Adicionar ao chat
        self.chat_area.insertHtml(message.to_html())
        
        # Scroll para o final
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_area.setTextCursor(cursor)
        
        # Notificar se não for usuário
        if not is_user:
            self.message_received.emit(text)
    
    def add_system_message(self, text: str):
        """Adiciona uma mensagem do sistema."""
        html = f"""
        <div style="margin: 8px; text-align: center;">
            <span style="color: #888888; font-style: italic;">{text}</span>
        </div>
        """
        self.chat_area.insertHtml(html)
        
        # Scroll para o final
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_area.setTextCursor(cursor)
    
    def set_processing(self, processing: bool):
        """Define estado de processamento."""
        self._is_processing = processing
        self.send_button.setEnabled(not processing)
        
        if processing:
            self.send_button.setText("Processando...")
            self.add_system_message("IA está processando...")
        else:
            self.send_button.setText("Enviar")
    
    def clear(self):
        """Limpa o chat."""
        self._messages.clear()
        self.chat_area.clear()
        self._is_processing = False
        self.send_button.setEnabled(True)
        self.send_button.setText("Enviar")
    
    def get_messages(self) -> List[ChatMessage]:
        """Retorna todas as mensagens."""
        return self._messages.copy()
