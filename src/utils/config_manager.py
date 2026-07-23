import json
import os
from typing import Dict, Any, Optional
from ..utils.logger import Logger


class ConfigManager:
    """Gerenciador de configurações do aplicativo."""
    
    def __init__(self, config_file: str = "config.json"):
        """
        Inicializa o gerenciador de configurações.
        
        Args:
            config_file: Nome do arquivo de configuração
        """
        self.config_file = config_file
        self.config_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.config_dir, "..", "..", config_file)
        self.logger = Logger("ConfigManager")
        
        # Configurações padrão
        self.default_config = {
            "ollama": {
                "host": "http://localhost:11434",
                "model": "qwen2-vl:7b",
                "enabled": False
            },
            "gemini": {
                "api_key": "",
                "model": "gemini-3.5-flash",
                "enabled": False
            },
            "ai_provider": {
                "selected": "ollama"  # "ollama" ou "gemini"
            },
            "organization": {
                "create_backup": True,
                "confirm_actions": True,
                "auto_rename": False
            },
            "preview": {
                "max_width": 400,
                "max_height": 300,
                "auto_load": True
            },
            "logging": {
                "level": "INFO",
                "save_logs": True,
                "log_dir": "logs"
            },
            "ui": {
                "theme": "default",
                "language": "pt-BR",
                "window_width": 1200,
                "window_height": 700
            }
        }
        
        # Carrega configurações
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        Carrega as configurações do arquivo.
        
        Returns:
            Dicionário com as configurações
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Mescla com configurações padrão
                    config = self._merge_config(self.default_config, loaded_config)
                    self.logger.info(f"Configurações carregadas de {self.config_path}")
                    return config
            else:
                self.logger.info("Arquivo de configuração não encontrado, usando padrões")
                return self.default_config.copy()
        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações: {str(e)}")
            return self.default_config.copy()
    
    def save_config(self) -> bool:
        """
        Salva as configurações no arquivo.
        
        Returns:
            True se salvo com sucesso, False caso contrário
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            self.logger.info(f"Configurações salvas em {self.config_path}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar configurações: {str(e)}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtém um valor de configuração.
        
        Args:
            key: Chave da configuração (ex: "ollama.host")
            default: Valor padrão se não encontrado
            
        Returns:
            Valor da configuração
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> bool:
        """
        Define um valor de configuração.
        
        Args:
            key: Chave da configuração (ex: "ollama.host")
            value: Valor a definir
            
        Returns:
            True se definido com sucesso, False caso contrário
        """
        try:
            keys = key.split('.')
            config = self.config
            
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            config[keys[-1]] = value
            self.logger.info(f"Configuração atualizada: {key} = {value}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao definir configuração {key}: {str(e)}")
            return False
    
    def reset_to_default(self) -> bool:
        """
        Reseta todas as configurações para os valores padrão.
        
        Returns:
            True se resetado com sucesso, False caso contrário
        """
        try:
            self.config = self.default_config.copy()
            self.logger.info("Configurações resetadas para os valores padrão")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao resetar configurações: {str(e)}")
            return False
    
    def _merge_config(self, default: Dict, loaded: Dict) -> Dict:
        """
        Mescla configurações carregadas com as padrão.
        
        Args:
            default: Configurações padrão
            loaded: Configurações carregadas
            
        Returns:
            Configurações mescladas
        """
        result = default.copy()
        
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get_all(self) -> Dict[str, Any]:
        """
        Retorna todas as configurações.
        
        Returns:
            Dicionário com todas as configurações
        """
        return self.config.copy()
