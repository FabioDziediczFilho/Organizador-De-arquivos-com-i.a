from typing import Dict, Any, Optional
from .ollama_client import OllamaClient
from ..utils.logger import Logger


class ImageAnalyzer:
    """Analisador de imagens usando IA para extrair contexto."""
    
    def __init__(self, ollama_client: Optional[OllamaClient] = None):
        """
        Inicializa o analisador de imagens.
        
        Args:
            ollama_client: Cliente Ollama (cria um novo se não fornecido)
        """
        self.client = ollama_client or OllamaClient()
        self.logger = Logger("ImageAnalyzer")
        self.logger.info("ImageAnalyzer inicializado")
    
    def analyze_image_context(self, image_path: str) -> Dict[str, Any]:
        """
        Analisa uma imagem para determinar seu contexto.
        
        Args:
            image_path: Caminho da imagem
            
        Returns:
            Dicionário com contexto da imagem (categoria, descrição, etc.)
        """
        prompt = """
        Analise esta imagem e responda em formato JSON com as seguintes informações:
        {
            "category": "categoria principal (ex: paisagem, retrato, comida, animal, documento, outro)",
            "description": "descrição breve da imagem em português",
            "keywords": ["palavra1", "palavra2", "palavra3"],
            "context": "contexto onde a foto foi tirada (ex: viagem, trabalho, casa, evento, outro)",
            "confidence": "nivel de confiança da análise (alto, medio, baixo)"
        }
        
        Responda apenas com o JSON, sem texto adicional.
        """
        
        try:
            response = self.client.analyze_image(image_path, prompt)
            
            # Tenta extrair JSON da resposta
            import json
            import re
            
            # Procura por JSON na resposta
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                context = json.loads(json_str)
                
                self.logger.info(f"Contexto extraído para {image_path}: {context.get('category', 'desconhecido')}")
                return context
            else:
                # Se não encontrou JSON, retorna resposta bruta
                self.logger.warning(f"Não foi possível extrair JSON da resposta para {image_path}")
                return {
                    "category": "desconhecido",
                    "description": response,
                    "keywords": [],
                    "context": "desconhecido",
                    "confidence": "baixo"
                }
                
        except Exception as e:
            self.logger.error(f"Erro ao analisar contexto da imagem {image_path}: {str(e)}")
            return {
                "category": "erro",
                "description": f"Erro na análise: {str(e)}",
                "keywords": [],
                "context": "erro",
                "confidence": "baixo"
            }
    
    def suggest_filename(self, image_path: str) -> str:
        """
        Sugere um nome de arquivo baseado no conteúdo da imagem.
        
        Args:
            image_path: Caminho da imagem
            
        Returns:
            Nome de arquivo sugerido
        """
        prompt = """
        Analise esta imagem e sugira um nome de arquivo descritivo em português.
        O nome deve:
        - Ser curto (máximo 30 caracteres)
        - Usar apenas letras, números e underscores
        - Ser em minúsculas
        - Descrever o conteúdo principal da imagem
        
        Responda apenas com o nome do arquivo, sem extensão e sem texto adicional.
        """
        
        try:
            response = self.client.analyze_image(image_path, prompt)
            
            # Limpa a resposta
            suggested_name = response.strip().lower()
            suggested_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in suggested_name)
            suggested_name = suggested_name[:30]  # Limita a 30 caracteres
            
            self.logger.info(f"Nome sugerido para {image_path}: {suggested_name}")
            return suggested_name
            
        except Exception as e:
            self.logger.error(f"Erro ao sugerir nome para {image_path}: {str(e)}")
            return "imagem_analisada"
    
    def batch_analyze(self, image_paths: list) -> Dict[str, Dict[str, Any]]:
        """
        Analisa múltiplas imagens em lote.
        
        Args:
            image_paths: Lista de caminhos de imagens
            
        Returns:
            Dicionário com caminho -> contexto de cada imagem
        """
        results = {}
        
        for image_path in image_paths:
            context = self.analyze_image_context(image_path)
            results[image_path] = context
        
        self.logger.info(f"Análise em lote concluída: {len(results)} imagens")
        return results
