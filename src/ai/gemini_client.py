import base64
import os
from typing import Optional, Dict, Any, List
from google import genai
from ..utils.logger import Logger


class GeminiClient:
    """Cliente para comunicação com a API do Google Gemini AI."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-3.5-flash"):
        """
        Inicializa o cliente Gemini.
        
        Args:
            api_key: Chave de API do Google AI Studio (se None, tenta da variável de ambiente)
            model: Modelo do Gemini a usar (padrão: gemini-3.5-flash)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("API key do Gemini não fornecida. Defina GEMINI_API_KEY ou passe como parâmetro.")
        
        self.model_name = model
        self.client = genai.Client(api_key=self.api_key)
        self.logger = Logger("GeminiClient")
        self.logger.info(f"GeminiClient inicializado com modelo: {model}")
    
    def check_connection(self) -> bool:
        """
        Verifica se a conexão com a API está funcionando.
        
        Returns:
            True se conexão estiver OK, False caso contrário
        """
        try:
            # Tenta uma requisição simples
            response = self.client.interactions.create(
                model=self.model_name,
                input="Hello"
            )
            if response and response.output_text:
                self.logger.info("Conexão com Gemini verificada com sucesso")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Erro ao verificar conexão com Gemini: {str(e)}")
            return False
    
    def generate_text(self, prompt: str, **kwargs) -> Optional[str]:
        """
        Gera texto a partir de um prompt.
        
        Args:
            prompt: Texto do prompt
            **kwargs: Parâmetros adicionais (temperature, max_tokens, etc.)
            
        Returns:
            Texto gerado ou None em caso de erro
        """
        try:
            response = self.client.interactions.create(
                model=self.model_name,
                input=prompt,
                config=genai.GenerateContentConfig(
                    temperature=kwargs.get('temperature', 0.7),
                    max_output_tokens=kwargs.get('max_tokens', 1024),
                )
            )
            
            if response and response.output_text:
                self.logger.info(f"Texto gerado com sucesso (tamanho: {len(response.output_text)} caracteres)")
                return response.output_text
            return None
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar texto: {str(e)}")
            return None
    
    def analyze_image(self, image_path: str, prompt: str) -> Optional[str]:
        """
        Analisa uma imagem com o Gemini.
        
        Args:
            image_path: Caminho da imagem
            prompt: Prompt para análise
            
        Returns:
            Resposta da análise ou None em caso de erro
        """
        try:
            # Carrega a imagem
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Imagem não encontrada: {image_path}")
            
            # Carrega a imagem como bytes
            with open(image_path, "rb") as image_file:
                image_bytes = image_file.read()
            
            # Converte para base64
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")
            
            # Determina o MIME type
            mime_type = "image/jpeg"
            if image_path.lower().endswith('.png'):
                mime_type = "image/png"
            elif image_path.lower().endswith('.webp'):
                mime_type = "image/webp"
            elif image_path.lower().endswith('.jpeg'):
                mime_type = "image/jpeg"
            
            # Gera conteúdo com imagem usando interactions.create
            response = self.client.interactions.create(
                model=self.model_name,
                input=[
                    {"type": "text", "text": prompt},
                    {"type": "image", "data": image_b64, "mime_type": mime_type}
                ]
            )
            
            if response and response.output_text:
                self.logger.info(f"Imagem analisada com sucesso: {image_path}")
                return response.output_text
            return None
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar imagem {image_path}: {str(e)}")
            return None
    
    def analyze_image_for_file_organization(self, image_path: str) -> Dict[str, Any]:
        """
        Analisa uma imagem para fins de organização de arquivos.
        
        Args:
            image_path: Caminho da imagem
            
        Returns:
            Dicionário com contexto, sugestão de nome e categoria
        """
        prompt = """
        Analise esta imagem e forneça:
        1. Um breve contexto sobre o que está na imagem (máximo 20 palavras)
        2. Uma sugestão de nome descritivo para o arquivo (sem extensão, máximo 3 palavras)
        3. Uma categoria simples (ex: paisagem, retrato, documento, produto, animal, etc.)
        
        Responda APENAS no formato JSON, sem markdown:
        {
            "context": "contexto da imagem",
            "suggested_name": "nome sugerido",
            "category": "categoria"
        }
        """
        
        try:
            response = self.analyze_image(image_path, prompt)
            
            if response:
                # Tenta extrair JSON da resposta
                import json
                # Remove markdown code blocks se existirem
                response_text = response.strip()
                if response_text.startswith("```"):
                    response_text = response_text.split("```")[1]
                    if response_text.startswith("json"):
                        response_text = response_text[4:]
                
                result = json.loads(response_text.strip())
                
                self.logger.info(f"Análise de organização concluída para {image_path}")
                return result
            else:
                # Retorna valores padrão se falhar
                return {
                    "context": "Não foi possível analisar",
                    "suggested_name": os.path.splitext(os.path.basename(image_path))[0],
                    "category": "desconhecido"
                }
                
        except Exception as e:
            self.logger.error(f"Erro ao analisar imagem para organização: {str(e)}")
            return {
                "context": "Erro na análise",
                "suggested_name": os.path.splitext(os.path.basename(image_path))[0],
                "category": "desconhecido"
            }
    
    def classify_batch(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Classifica múltiplas imagens em lote.
        
        Args:
            image_paths: Lista de caminhos de imagens
            
        Returns:
            Lista de resultados de classificação
        """
        results = []
        
        for image_path in image_paths:
            try:
                result = self.analyze_image_for_file_organization(image_path)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Erro ao classificar {image_path}: {str(e)}")
                results.append({
                    "context": "Erro",
                    "suggested_name": os.path.splitext(os.path.basename(image_path))[0],
                    "category": "erro"
                })
        
        self.logger.info(f"Classificação em lote concluída: {len(results)} imagens")
        return results
    
    def list_models(self) -> List[str]:
        """
        Lista os modelos disponíveis.
        
        Returns:
            Lista de nomes de modelos
        """
        try:
            models = self.client.models.list()
            model_names = [model.name for model in models]
            self.logger.info(f"Modelos disponíveis: {len(model_names)}")
            return model_names
        except Exception as e:
            self.logger.error(f"Erro ao listar modelos: {str(e)}")
            return []
