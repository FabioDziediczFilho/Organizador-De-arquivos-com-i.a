from PySide6.QtCore import QObject, Signal, Property
from typing import Optional, Dict, Any


class AIResponse(QObject):
    """Modelo de resposta da IA com signals Qt."""
    
    data_changed = Signal()
    
    def __init__(self, text: str = "", context: str = "", category: str = "", suggested_name: str = ""):
        super().__init__()
        self.text = text
        self.context = context
        self.category = category
        self.suggested_name = suggested_name
        self.is_error = False
        self.error_message = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "text": self.text,
            "context": self.context,
            "category": self.category,
            "suggested_name": self.suggested_name,
            "is_error": self.is_error,
            "error_message": self.error_message
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'AIResponse':
        """Cria AIResponse a partir de dicionário."""
        response = AIResponse(
            text=data.get("text", ""),
            context=data.get("context", ""),
            category=data.get("category", ""),
            suggested_name=data.get("suggested_name", "")
        )
        response.is_error = data.get("is_error", False)
        response.error_message = data.get("error_message", "")
        return response


class AIStatus(QObject):
    """Modelo de status da IA com signals Qt."""
    
    status_changed = Signal()
    
    def __init__(self):
        super().__init__()
        self.is_connected = False
        self.is_processing = False
        self.provider = "ollama"
        self.model = ""
        self.last_error = ""
    
    def reset(self):
        """Reseta o status."""
        self.is_connected = False
        self.is_processing = False
        self.last_error = ""
