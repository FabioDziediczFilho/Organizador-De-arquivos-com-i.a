import logging
import os
from datetime import datetime
from typing import Optional

class Logger:
    """Classe para gerenciar logs do sistema de organização de arquivos."""
    
    def __init__(self, name: str = "FileOrganizer", log_dir: str = "logs", level: int = logging.INFO):
        """
        Inicializa o logger.
        
        Args:
            name: Nome do logger
            log_dir: Diretório onde os logs serão salvos
            level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.name = name
        self.log_dir = log_dir
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Cria o diretório de logs se não existir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Configura o formatador dos logs
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Configura handler para arquivo
        log_file = os.path.join(log_dir, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        
        # Configura handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        
        # Adiciona os handlers se ainda não existirem
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def info(self, message: str):
        """Log de informação"""
        self.logger.info(message)

    def error(self, message: str):
        """Log de erro"""
        self.logger.error(message)

    def warning(self, message: str):
        """Log de aviso"""
        self.logger.warning(message)

    def debug(self, message: str):
        """Log de debug"""
        self.logger.debug(message)

    def critical(self, message: str):
        """Log de critico"""
        self.logger.critical(message)