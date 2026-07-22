import requests
import base64
from typing import Dict, Any, Optional, List
from ..utils.logger import Logger


class OllamaClient:
    """Cliente para se comunicar com a API do Ollama."""
    
    def __init__(self, host: str = "http://localhost:11434", model: str = "qwen2-vl:7b"):
        """
        Inicializa o cliente Ollama.
        
        Args:
            host: URL do servidor Ollama
            model: Nome do modelo a ser usado
        """
        self.host = host
        self.model = model
        self.logger = Logger("OllamaClient")
        self.logger.info(f"OllamaClient inicializado com host={host}, model={model}")
    
    def check_connection(self) -> bool:
        """
        Verifica se o servidor Ollama está disponível.
        
        Returns:
            True se conectado, False caso contrário
        """
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                self.logger.info("Conexão com Ollama estabelecida com sucesso")
                return True
            else:
                self.logger.error(f"Erro na conexão: Status {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"Erro ao conectar com Ollama: {str(e)}")
            return False
    
    def generate_text(self, prompt: str, system: Optional[str] = None) -> str:
        """
        Gera texto usando o modelo.
        
        Args:
            prompt: Prompt para o modelo
            system: Instrução de sistema (opcional)
            
        Returns:
            Texto gerado pelo modelo
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            if system:
                payload["system"] = system
            
            response = requests.post(f"{self.host}/api/generate", json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            generated_text = result.get("response", "")
            
            self.logger.info(f"Texto gerado com sucesso ({len(generated_text)} caracteres)")
            return generated_text
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar texto: {str(e)}")
            return ""
    
    def analyze_image(self, image_path: str, prompt: str) -> str:
        """
        Analisa uma imagem usando o modelo multimodal.
        
        Args:
            image_path: Caminho da imagem
            prompt: Prompt para análise da imagem
            
        Returns:
            Resposta do modelo sobre a imagem
        """
        try:
            # Lê a imagem e converte para base64
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "images": [image_data],
                "stream": False
            }
            
            response = requests.post(f"{self.host}/api/generate", json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            analysis = result.get("response", "")
            
            self.logger.info(f"Imagem analisada com sucesso: {image_path}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar imagem {image_path}: {str(e)}")
            return ""
    
    def get_available_models(self) -> List[str]:
        """
        Lista os modelos disponíveis no servidor Ollama.
        
        Returns:
            Lista de nomes de modelos
        """
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            response.raise_for_status()
            
            result = response.json()
            models = [model["name"] for model in result.get("models", [])]
            
            self.logger.info(f"Modelos disponíveis: {len(models)}")
            return models
            
        except Exception as e:
            self.logger.error(f"Erro ao listar modelos: {str(e)}")
            return []
