from typing import Dict, Any, List
from .image_analyzer import ImageAnalyzer
from ..utils.logger import Logger


class ContextClassifier:
    """Classificador de contexto para organizar arquivos por categoria semântica."""
    
    # Categorias de contexto predefinidas
    CONTEXT_CATEGORIES = {
        "viagem": ["praia", "montanha", "cidade", "turismo", "hotel", "aeroporto", "paisagem"],
        "trabalho": ["escritório", "reunião", "apresentação", "documento", "computador", "reunião"],
        "casa": ["cozinha", "sala", "quarto", "jardim", "família", "pet"],
        "evento": ["festa", "casamento", "aniversário", "conferência", "show", "concerto"],
        "natureza": ["flor", "árvore", "animal", "céu", "sol", "chuva", "rio"],
        "comida": ["prato", "restaurante", "cozinha", "bebida", "fruta", "legume"],
        "pessoa": ["retrato", "selfie", "grupo", "família", "amigos", "criança"],
        "outros": []
    }
    
    def __init__(self, image_analyzer: ImageAnalyzer = None):
        """
        Inicializa o classificador de contexto.
        
        Args:
            image_analyzer: Analisador de imagens (cria um novo se não fornecido)
        """
        self.analyzer = image_analyzer or ImageAnalyzer()
        self.logger = Logger("ContextClassifier")
        self.logger.info("ContextClassifier inicializado")
    
    def classify_context(self, image_context: Dict[str, Any]) -> str:
        """
        Classifica o contexto de uma imagem em categorias predefinidas.
        
        Args:
            image_context: Dicionário com contexto da imagem do ImageAnalyzer
            
        Returns:
            Categoria de contexto (viagem, trabalho, casa, evento, natureza, comida, pessoa, outros)
        """
        try:
            keywords = image_context.get("keywords", [])
            description = image_context.get("description", "").lower()
            context = image_context.get("context", "").lower()
            
            # Combina keywords, descrição e contexto para análise
            text_to_analyze = " ".join(keywords + [description, context])
            
            # Verifica cada categoria
            for category, category_keywords in self.CONTEXT_CATEGORIES.items():
                if category == "outros":
                    continue
                    
                for keyword in category_keywords:
                    if keyword in text_to_analyze:
                        self.logger.info(f"Imagem classificada como: {category}")
                        return category
            
            # Se não encontrou correspondência, usa o contexto fornecido pela IA
            if context and context != "desconhecido":
                # Mapeia contextos comuns para categorias
                context_mapping = {
                    "viagem": "viagem",
                    "trabalho": "trabalho",
                    "casa": "casa",
                    "evento": "evento",
                    "outdoor": "natureza",
                    "restaurante": "comida"
                }
                
                for key, value in context_mapping.items():
                    if key in context:
                        self.logger.info(f"Imagem classificada como: {value} (via contexto)")
                        return value
            
            self.logger.info("Imagem classificada como: outros")
            return "outros"
            
        except Exception as e:
            self.logger.error(f"Erro ao classificar contexto: {str(e)}")
            return "outros"
    
    def classify_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analisa e classifica uma imagem completa.
        
        Args:
            image_path: Caminho da imagem
            
        Returns:
            Dicionário com contexto completo e classificação
        """
        # Analisa a imagem
        image_context = self.analyzer.analyze_image_context(image_path)
        
        # Classifica o contexto
        category = self.classify_context(image_context)
        
        # Retorna resultado completo
        result = {
            "image_path": image_path,
            "context": image_context,
            "classification": category,
            "suggested_folder": category
        }
        
        self.logger.info(f"Imagem {image_path} classificada como {category}")
        return result
    
    def batch_classify(self, image_paths: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Classifica múltiplas imagens em lote.
        
        Args:
            image_paths: Lista de caminhos de imagens
            
        Returns:
            Dicionário com caminho -> classificação de cada imagem
        """
        results = {}
        
        for image_path in image_paths:
            classification = self.classify_image(image_path)
            results[image_path] = classification
        
        self.logger.info(f"Classificação em lote concluída: {len(results)} imagens")
        return results
    
    def get_classification_summary(self, classifications: Dict[str, Dict[str, Any]]) -> Dict[str, int]:
        """
        Gera um resumo das classificações.
        
        Args:
            classifications: Dicionário de classificações
            
        Returns:
            Dicionário com contagem por categoria
        """
        summary = {}
        
        for image_path, classification in classifications.items():
            category = classification.get("classification", "outros")
            summary[category] = summary.get(category, 0) + 1
        
        self.logger.info(f"Resumo de classificações: {summary}")
        return summary
