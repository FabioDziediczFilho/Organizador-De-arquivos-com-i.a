import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from typing import Optional


class ImagePreview:
    """Visualizador de imagens integrado na GUI."""
    
    def __init__(self, parent: tk.Widget):
        """
        Inicializa o visualizador de imagens.
        
        Args:
            parent: Widget pai onde o preview será exibido
        """
        self.parent = parent
        self.current_image = None
        self.image_label = None
        self.info_label = None
        self.frame = None
        
    def create_preview_frame(self) -> ttk.Frame:
        """
        Cria o frame do visualizador de imagens.
        
        Returns:
            Frame com o visualizador
        """
        self.frame = ttk.Frame(self.parent, padding=16, style="Card.TFrame")
        
        # Label para mostrar a imagem
        self.image_label = tk.Label(
            self.frame,
            text="Nenhuma imagem selecionada",
            width=40,
            height=12,
            anchor="center",
            fg="#5b6b7a",
            bg="#ffffff",
            font=("Arial", 11),
        )
        self.image_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 8))
        
        # Label com informações da imagem
        self.info_label = tk.Label(self.frame, text="", fg="#5b6b7a", bg="#ffffff", font=("Arial", 10))
        self.info_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # Configura grid
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        
        return self.frame
    
    def load_image(self, image_path: str, max_width: int = 420, max_height: int = 320):
        """
        Carrega e exibe uma imagem.
        
        Args:
            image_path: Caminho da imagem
            max_width: Largura máxima do preview
            max_height: Altura máxima do preview
        """
        try:
            if not os.path.exists(image_path):
                self.image_label.config(text="Arquivo não encontrado")
                self.info_label.config(text="")
                return
            
            # Abre a imagem
            image = Image.open(image_path)
            
            # Redimensiona mantendo proporção
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Converte para PhotoTk
            self.current_image = ImageTk.PhotoImage(image)
            
            # Exibe a imagem
            self.image_label.config(image=self.current_image, text="")
            
            # Mostra informações
            file_size = os.path.getsize(image_path)
            size_str = self._format_size(file_size)
            dimensions = f"{image.width}x{image.height}"
            
            info_text = f"{os.path.basename(image_path)} | {dimensions} | {size_str}"
            self.info_label.config(text=info_text)
            
        except Exception as e:
            self.image_label.config(text=f"Erro ao carregar imagem: {str(e)}")
            self.info_label.config(text="")
    
    def clear_preview(self):
        """Limpa o visualizador."""
        self.image_label.config(image="", text="Nenhuma imagem selecionada")
        self.info_label.config(text="")
        self.current_image = None
    
    def _format_size(self, size_bytes: int) -> str:
        """Formata tamanho em bytes para string legível."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
