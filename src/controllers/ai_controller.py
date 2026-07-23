from PySide6.QtCore import QObject, Signal, QThread
from typing import Optional, List, Dict, Any
from src.utils.logger import Logger
from src.models.ai_model import AIResponse, AIStatus
from src.ai.gemini_client import GeminiClient
from src.ai.image_analyzer import ImageAnalyzer
from src.ai.context_classifier import ContextClassifier


class AIWorker(QThread):
    """Worker thread para operações de IA."""
    
    finished = Signal(object)  # AIResponse ou lista de AIResponse
    error = Signal(str)
    progress = Signal(int, int)  # current, total
    
    def __init__(self, operation: str, **kwargs):
        super().__init__()
        self.operation = operation
        self.kwargs = kwargs
    
    def run(self):
        """Executa a operação de IA."""
        try:
            if self.operation == "analyze_image":
                self._analyze_image()
            elif self.operation == "classify_batch":
                self._classify_batch()
            elif self.operation == "chat":
                self._chat()
            
        except Exception as e:
            self.error.emit(str(e))
    
    def _analyze_image(self):
        """Analisa uma imagem."""
        file_path = self.kwargs.get('file_path')
        provider = self.kwargs.get('provider', 'ollama')
        
        if provider == 'gemini':
            api_key = self.kwargs.get('api_key')
            model = self.kwargs.get('model', 'gemini-3.5-flash')
            client = GeminiClient(api_key, model)
            result = client.analyze_image_for_file_organization(file_path)
        else:
            host = self.kwargs.get('host', 'http://localhost:11434')
            model = self.kwargs.get('model', 'qwen2-vl:7b')
            analyzer = ImageAnalyzer(host, model)
            result = analyzer.analyze_image(file_path)
        
        response = AIResponse()
        if result:
            response.text = result.get('description', '')
            response.context = result.get('context', '')
            response.category = result.get('category', '')
            response.suggested_name = result.get('suggested_name', '')
        else:
            response.is_error = True
            response.error_message = "Falha na análise"
        
        self.finished.emit(response)
    
    def _classify_batch(self):
        """Classifica imagens em lote."""
        file_paths = self.kwargs.get('file_paths', [])
        provider = self.kwargs.get('provider', 'ollama')
        
        results = []
        for i, file_path in enumerate(file_paths):
            self.progress.emit(i + 1, len(file_paths))
            
            if provider == 'gemini':
                api_key = self.kwargs.get('api_key')
                model = self.kwargs.get('model', 'gemini-3.5-flash')
                client = GeminiClient(api_key, model)
                result = client.classify_batch([file_path])
                if result:
                    results.append(result[0])
            else:
                host = self.kwargs.get('host', 'http://localhost:11434')
                model = self.kwargs.get('model', 'qwen2-vl:7b')
                classifier = ContextClassifier(host, model)
                result = classifier.classify_batch([file_path])
                if result:
                    results.append(result[0])
        
        self.finished.emit(results)
    
    def _chat(self):
        """Chat com IA."""
        message = self.kwargs.get('message')
        provider = self.kwargs.get('provider', 'ollama')
        image_path = self.kwargs.get('image_path')
        
        response = AIResponse()
        
        if provider == 'gemini':
            api_key = self.kwargs.get('api_key')
            model = self.kwargs.get('model', 'gemini-3.5-flash')
            client = GeminiClient(api_key, model)
            
            if image_path:
                result = client.analyze_image_for_file_organization(image_path)
                if result:
                    response.text = result.get('description', '')
            else:
                # Chat simples com texto
                response.text = "Chat com Gemini não implementado ainda"
        else:
            # Ollama chat
            response.text = "Chat com Ollama não implementado ainda"
        
        self.finished.emit(response)


class AIController(QObject):
    """Controller para operações de IA."""
    
    # Signals
    response_received = Signal(object)  # AIResponse
    batch_response_received = Signal(list)  # List[AIResponse]
    error_occurred = Signal(str)
    status_changed = Signal(str)
    progress_updated = Signal(int, int)  # current, total
    
    def __init__(self):
        super().__init__()
        self.logger = Logger("AIController")
        self.ai_status = AIStatus()
        self._worker: Optional[AIWorker] = None
        self._cache: Dict[str, AIResponse] = {}
    
    def check_connection(self, provider: str, **kwargs) -> bool:
        """Verifica conexão com o provedor de IA."""
        try:
            self.ai_status.is_processing = True
            self.status_changed.emit("Verificando conexão...")
            
            if provider == 'gemini':
                api_key = kwargs.get('api_key')
                model = kwargs.get('model', 'gemini-3.5-flash')
                client = GeminiClient(api_key, model)
                connected = client.check_connection()
            else:
                # Ollama connection check
                host = kwargs.get('host', 'http://localhost:11434')
                # Simple connection check
                import requests
                response = requests.get(f"{host}/api/tags", timeout=5)
                connected = response.status_code == 200
            
            self.ai_status.is_connected = connected
            self.ai_status.is_processing = False
            self.ai_status.provider = provider
            
            if connected:
                self.status_changed.emit("Conectado")
                self.logger.info(f"Conexão estabelecida com {provider}")
            else:
                self.status_changed.emit("Falha na conexão")
                self.logger.warning(f"Falha na conexão com {provider}")
            
            return connected
            
        except Exception as e:
            self.ai_status.is_connected = False
            self.ai_status.is_processing = False
            self.ai_status.last_error = str(e)
            self.error_occurred.emit(str(e))
            self.logger.error(f"Erro ao verificar conexão: {str(e)}")
            return False
    
    def analyze_image(self, file_path: str, provider: str, **kwargs):
        """Analisa uma imagem."""
        try:
            self.ai_status.is_processing = True
            self.status_changed.emit("Analisando imagem...")
            
            # Check cache
            cache_key = f"{provider}:{file_path}"
            if cache_key in self._cache:
                self.response_received.emit(self._cache[cache_key])
                self.ai_status.is_processing = False
                return
            
            self._worker = AIWorker("analyze_image", file_path=file_path, provider=provider, **kwargs)
            self._worker.finished.connect(self._on_analyze_finished)
            self._worker.error.connect(self._on_error)
            self._worker.start()
            
        except Exception as e:
            self.ai_status.is_processing = False
            self.error_occurred.emit(str(e))
            self.logger.error(f"Erro ao iniciar análise: {str(e)}")
    
    def _on_analyze_finished(self, response: AIResponse):
        """Callback quando análise termina."""
        self._cache[f"{self.ai_status.provider}:{self.kwargs.get('file_path')}"] = response
        self.response_received.emit(response)
        self.ai_status.is_processing = False
        self.status_changed.emit("Análise concluída")
    
    def classify_batch(self, file_paths: List[str], provider: str, **kwargs):
        """Classifica imagens em lote."""
        try:
            self.ai_status.is_processing = True
            self.status_changed.emit(f"Classificando {len(file_paths)} imagens...")
            
            self._worker = AIWorker("classify_batch", file_paths=file_paths, provider=provider, **kwargs)
            self._worker.finished.connect(self._on_batch_finished)
            self._worker.error.connect(self._on_error)
            self._worker.progress.connect(self.progress_updated.emit)
            self._worker.start()
            
        except Exception as e:
            self.ai_status.is_processing = False
            self.error_occurred.emit(str(e))
            self.logger.error(f"Erro ao iniciar classificação: {str(e)}")
    
    def _on_batch_finished(self, responses: List[AIResponse]):
        """Callback quando classificação em lote termina."""
        self.batch_response_received.emit(responses)
        self.ai_status.is_processing = False
        self.status_changed.emit("Classificação concluída")
    
    def chat(self, message: str, provider: str, image_path: Optional[str] = None, **kwargs):
        """Chat com IA."""
        try:
            self.ai_status.is_processing = True
            self.status_changed.emit("Enviando mensagem...")
            
            self._worker = AIWorker("chat", message=message, provider=provider, image_path=image_path, **kwargs)
            self._worker.finished.connect(self._on_chat_finished)
            self._worker.error.connect(self._on_error)
            self._worker.start()
            
        except Exception as e:
            self.ai_status.is_processing = False
            self.error_occurred.emit(str(e))
            self.logger.error(f"Erro ao iniciar chat: {str(e)}")
    
    def _on_chat_finished(self, response: AIResponse):
        """Callback quando chat termina."""
        self.response_received.emit(response)
        self.ai_status.is_processing = False
        self.status_changed.emit("Pronto")
    
    def _on_error(self, error: str):
        """Callback quando ocorre erro."""
        self.ai_status.is_processing = False
        self.ai_status.last_error = error
        self.error_occurred.emit(error)
        self.status_changed.emit("Erro")
        self.logger.error(f"Erro na operação de IA: {error}")
    
    def cancel(self):
        """Cancela operação em andamento."""
        if self._worker and self._worker.isRunning():
            self._worker.terminate()
            self._worker.wait()
            self.ai_status.is_processing = False
            self.status_changed.emit("Cancelado")
            self.logger.info("Operação cancelada")
    
    def get_status(self) -> AIStatus:
        """Retorna o status da IA."""
        return self.ai_status
    
    def clear_cache(self):
        """Limpa o cache de respostas."""
        self._cache.clear()
        self.logger.info("Cache limpo")
