import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from typing import List, Optional
import os
import shutil

from ..core.file_scanner import scan_directory, get_scan_summary, format_size
from ..core.file_organizer import FileOrganizer
from ..core.batch_renamer import BatchRenamer
from ..utils.logger import Logger
from ..utils.config_manager import ConfigManager
from .image_preview import ImagePreview
from .settings_window import SettingsWindow


class MainWindow:
    """Janela principal do organizador de arquivos."""
    
    def __init__(self, root: tk.Tk):
        """
        Inicializa a janela principal.
        
        Args:
            root: Janela raiz do tkinter
        """
        self.root = root
        self.root.title("Organizador de Arquivos com IA")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 650)
        self.root.configure(bg="#f4f7fb")
        self.root.option_add("*Font", "Arial 10")
        self.root.option_add("*Background", "#f4f7fb")
        self.root.option_add("*Foreground", "#22313f")

        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TFrame", background="#f4f7fb")
        style.configure("Card.TFrame", background="#ffffff")
        style.configure("TLabel", background="#f4f7fb", foreground="#22313f")
        style.configure("Accent.TButton", padding=(12, 8), background="#2563eb", foreground="#ffffff")
        style.map("Accent.TButton", background=[("active", "#1d4ed8"), ("pressed", "#1e40af")], foreground=[("!disabled", "#ffffff")])
        style.configure("Treeview", rowheight=26, fieldbackground="#ffffff", background="#ffffff")
        style.configure("Treeview.Heading", background="#eaf2ff")
        
        # Inicializa o logger
        self.logger = Logger("FileOrganizerGUI")
        
        # Inicializa o gerenciador de configurações
        self.config_manager = ConfigManager()
        
        # Variáveis
        self.selected_directory = tk.StringVar()
        self.scanned_files = []
        self.organizer = None
        self.batch_renamer = None
        self.image_preview = None
        self.settings_window = None
        
        # Cria a interface
        self.create_widgets()
        
        self.logger.info("GUI inicializada com sucesso")

    def create_widgets(self):
        """Cria todos os widgets da interface."""
        header_frame = ttk.Frame(self.root, padding=(24, 20, 24, 12), style="Card.TFrame")
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=16, pady=(16, 10))
        header_frame.columnconfigure(0, weight=1)

        tk.Label(
            header_frame,
            text="Organizador de Arquivos com IA",
            font=("Arial", 18, "bold"),
            fg="#1f4e79",
            bg="#ffffff",
        ).grid(row=0, column=0, sticky=tk.W)
        tk.Label(
            header_frame,
            text="Organize, renomeie e visualize seus arquivos com uma interface mais limpa e intuitiva.",
            font=("Arial", 10),
            fg="#5b6b7a",
            bg="#ffffff",
        ).grid(row=1, column=0, sticky=tk.W, pady=(4, 0))
        
        # Botão de configurações
        ttk.Button(
            header_frame,
            text="⚙️ Configurações",
            command=self.open_settings,
            style="Accent.TButton"
        ).grid(row=0, column=1, rowspan=2, sticky=tk.E, padx=(20, 0))

        # Cria área principal
        self.notebook = ttk.Notebook(self.root, padding=8)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=16, pady=(0, 8))
        
        # Configura grid principal
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        
        # Aba de organização
        self.create_organizer_tab()
        
        # Aba de IA
        self.create_ai_tab()
        
        # Label de status
        self.status_label = ttk.Label(self.root, text="Pronto", relief=tk.SUNKEN, padding=6)
        self.status_label.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=16, pady=(0, 12))
    
    def create_organizer_tab(self):
        """Cria a aba de organização de arquivos com preview embutido."""
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="Organização")
        
        # Frame principal
        main_frame = ttk.Frame(tab, style="Card.TFrame", padding=16)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configura grid
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=2)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        input_frame = ttk.Frame(main_frame, padding=(0, 0, 0, 10))
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 8))
        input_frame.columnconfigure(1, weight=1)

        tk.Label(input_frame, text="Diretório:", font=("Arial", 10, "bold"), bg="#ffffff").grid(row=0, column=0, sticky=tk.W, padx=(0, 8))
        ttk.Entry(input_frame, textvariable=self.selected_directory).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 8))
        ttk.Button(input_frame, text="Selecionar", command=self.select_directory, style="Accent.TButton").grid(row=0, column=2)
        
        # Botões de ação
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(4, 10), sticky=tk.W)
        
        ttk.Button(button_frame, text="Escanear Arquivos", command=self.scan_files, style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(button_frame, text="Organizar por Categoria", command=self.organize_files).pack(side=tk.LEFT, padx=6)
        ttk.Button(button_frame, text="Mover para Pasta", command=self.move_to_folder).pack(side=tk.LEFT, padx=6)
        ttk.Button(button_frame, text="Renomear Selecionado", command=self.rename_selected).pack(side=tk.LEFT, padx=6)
        
        # Área de conteúdo
        files_panel = ttk.Frame(main_frame, padding=(0, 0, 8, 0))
        files_panel.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        files_panel.columnconfigure(0, weight=1)
        files_panel.rowconfigure(1, weight=1)

        preview_panel = ttk.Frame(main_frame, style="Card.TFrame", padding=10)
        preview_panel.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(8, 0))
        preview_panel.columnconfigure(0, weight=1)
        preview_panel.rowconfigure(0, weight=1)

        tk.Label(files_panel, text="Arquivos encontrados:", font=("Arial", 10, "bold"), bg="#ffffff").grid(row=0, column=0, sticky=tk.W, pady=(0, 6))
        
        # Treeview para mostrar arquivos
        self.tree = ttk.Treeview(files_panel, columns=('name', 'category', 'size', 'path'), show='headings', height=12, selectmode='extended')
        self.tree.heading('name', text='Nome')
        self.tree.heading('category', text='Categoria')
        self.tree.heading('size', text='Tamanho')
        self.tree.heading('path', text='Caminho')
        self.tree.column('name', width=220)
        self.tree.column('category', width=100)
        self.tree.column('size', width=85)
        self.tree.column('path', width=0, stretch=False)
        self.tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(files_panel, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # Preview embutido
        tk.Label(preview_panel, text="Preview", font=("Arial", 10, "bold"), bg="#ffffff").grid(row=0, column=0, sticky=tk.W, pady=(0, 6))
        self.image_preview = ImagePreview(preview_panel)
        preview_frame = self.image_preview.create_preview_frame()
        preview_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        preview_panel.rowconfigure(1, weight=1)
        
        # Configura seleção na treeview
        self.tree.bind('<<TreeviewSelect>>', self.on_file_select)
    
    def create_ai_tab(self):
        """Cria a aba de interação com IA."""
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="IA")
        
        # Frame principal
        main_frame = ttk.Frame(tab, style="Card.TFrame", padding=16)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configura grid
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=2)
        main_frame.rowconfigure(0, weight=0)
        main_frame.rowconfigure(1, weight=1)
        
        # Header
        tk.Label(
            main_frame,
            text="Inteligência Artificial",
            font=("Arial", 16, "bold"),
            fg="#1f4e79",
            bg="#ffffff"
        ).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        tk.Label(
            main_frame,
            text="Analise imagens, classifique arquivos e interaja com IA",
            font=("Arial", 10),
            fg="#5b6b7a",
            bg="#ffffff"
        ).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # Botões de ação IA
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        ttk.Button(button_frame, text="Verificar Conexão", command=self.check_ollama_connection, style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(button_frame, text="Analisar Imagem", command=self.analyze_image_with_ai).pack(side=tk.LEFT, padx=6)
        ttk.Button(button_frame, text="Classificar Arquivos", command=self.classify_files_with_ai).pack(side=tk.LEFT, padx=6)
        ttk.Button(button_frame, text="Renomear com IA", command=self.rename_with_ai).pack(side=tk.LEFT, padx=6)
        
        # Painel esquerdo - Treeview de arquivos
        files_panel = ttk.LabelFrame(main_frame, text="Arquivos", padding=10)
        files_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        files_panel.columnconfigure(0, weight=1)
        files_panel.rowconfigure(0, weight=1)
        
        # Treeview para arquivos na aba IA
        self.ai_tree = ttk.Treeview(files_panel, columns=('name', 'type'), show='headings', height=20, selectmode='extended')
        self.ai_tree.heading('name', text='Nome')
        self.ai_tree.heading('type', text='Tipo')
        self.ai_tree.column('name', width=200)
        self.ai_tree.column('type', width=80)
        self.ai_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ai_tree_scrollbar = ttk.Scrollbar(files_panel, orient=tk.VERTICAL, command=self.ai_tree.yview)
        self.ai_tree.configure(yscrollcommand=ai_tree_scrollbar.set)
        ai_tree_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind para seleção
        self.ai_tree.bind('<<TreeviewSelect>>', self.on_ai_file_select)

        # Painel central - Preview de imagem
        preview_panel = ttk.LabelFrame(main_frame, text="Preview", padding=10)
        preview_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        preview_panel.columnconfigure(0, weight=1)
        preview_panel.rowconfigure(0, weight=1)

        # Canvas para preview
        self.ai_preview_canvas = tk.Canvas(preview_panel, bg="#f0f0f0", width=300, height=300)
        self.ai_preview_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Label de informação do arquivo
        self.ai_file_info = tk.Label(preview_panel, text="Nenhum arquivo selecionado", bg="#ffffff", fg="#5b6b7a")
        self.ai_file_info.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))

        # Painel direito - Chat/Output
        chat_panel = ttk.LabelFrame(main_frame, text="Chat com IA", padding=10)
        chat_panel.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        chat_panel.columnconfigure(0, weight=1)
        chat_panel.rowconfigure(0, weight=1)
        chat_panel.rowconfigure(1, weight=0)

        # Área de chat (output)
        self.ai_output = tk.Text(chat_panel, height=20, wrap=tk.WORD, font=("Arial", 9), state='disabled')
        self.ai_output.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        chat_scrollbar = ttk.Scrollbar(chat_panel, orient=tk.VERTICAL, command=self.ai_output.yview)
        self.ai_output.configure(yscrollcommand=chat_scrollbar.set)
        chat_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Campo de entrada
        input_frame = ttk.Frame(chat_panel)
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        input_frame.columnconfigure(0, weight=1)

        self.ai_input = ttk.Entry(input_frame)
        self.ai_input.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        self.ai_input.bind('<Return>', self.send_ai_message)

        ttk.Button(input_frame, text="Enviar", command=self.send_ai_message).grid(row=0, column=1)

    def on_ai_file_select(self, event):
        """Quando um arquivo é selecionado na treeview da IA."""
        selected_items = self.ai_tree.selection()
        if not selected_items:
            return

        try:
            item = self.ai_tree.item(selected_items[0])
            file_path = item['values'][2] if len(item['values']) > 2 else None

            if file_path and os.path.exists(file_path):
                # Mostra informações do arquivo
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                size_str = f"{file_size / 1024:.1f} KB" if file_size < 1024 * 1024 else f"{file_size / (1024 * 1024):.1f} MB"
                self.ai_file_info.config(text=f"{file_name} ({size_str})")

                # Mostra preview se for imagem
                if file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
                    self.show_ai_preview(file_path)
                else:
                    self.ai_preview_canvas.delete("all")
                    self.ai_preview_canvas.create_text(
                        150, 150,
                        text="Arquivo não é uma imagem",
                        fill="#5b6b7a",
                        font=("Arial", 10)
                    )

        except Exception as e:
            self.logger.error(f"Erro ao selecionar arquivo na IA: {str(e)}")

    def show_ai_preview(self, file_path):
        """Mostra preview da imagem no canvas da IA."""
        try:
            from PIL import Image, ImageTk

            # Carrega imagem
            image = Image.open(file_path)

            # Redimensiona para caber no canvas
            canvas_width = 300
            canvas_height = 300
            image.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)

            # Converte para PhotoImage
            photo = ImageTk.PhotoImage(image)

            # Limpa canvas e mostra imagem
            self.ai_preview_canvas.delete("all")
            self.ai_preview_canvas.create_image(
                canvas_width // 2,
                canvas_height // 2,
                image=photo,
                anchor=tk.CENTER
            )

            # Mantém referência para não ser garbage collected
            self.ai_preview_image = photo

        except Exception as e:
            self.logger.error(f"Erro ao mostrar preview na IA: {str(e)}")
            self.ai_preview_canvas.delete("all")
            self.ai_preview_canvas.create_text(
                150, 150,
                text="Erro ao carregar imagem",
                fill="#ff0000",
                font=("Arial", 10)
            )

    def send_ai_message(self, event=None):
        """Envia mensagem para a IA."""
        message = self.ai_input.get().strip()
        if not message:
            return
        
        try:
            provider = self.config_manager.get('ai_provider.selected', 'ollama')

            # Habilita text widget
            self.ai_output.config(state='normal')

            # Mostra mensagem do usuário
            self.ai_output.insert(tk.END, f"Você: {message}\n\n")
            self.ai_output.see(tk.END)

            # Limpa input
            self.ai_input.delete(0, tk.END)

            # Envia para IA
            if provider == 'gemini':
                response = self.chat_with_gemini(message)
            else:
                response = self.chat_with_ollama(message)

            # Mostra resposta
            self.ai_output.insert(tk.END, f"IA: {response}\n\n")
            self.ai_output.see(tk.END)

            # Desabilita text widget
            self.ai_output.config(state='disabled')

        except Exception as e:
            self.ai_output.config(state='normal')
            self.ai_output.insert(tk.END, f"Erro: {str(e)}\n\n")
            self.ai_output.see(tk.END)
            self.ai_output.config(state='disabled')
            self.logger.error(f"Erro ao enviar mensagem para IA: {str(e)}")

    def chat_with_gemini(self, message: str) -> str:
        """Chat com Gemini."""
        from ..ai.gemini_client import GeminiClient

        api_key = self.config_manager.get('gemini.api_key')
        model = self.config_manager.get('gemini.model', 'gemini-3.5-flash')

        if not api_key:
            return "API Key do Gemini não configurada."

        client = GeminiClient(api_key, model)
        response = client.generate_text(message)

        return response if response else "Erro ao gerar resposta."

    def chat_with_ollama(self, message: str) -> str:
        """Chat com Ollama."""
        from ..ai.ollama_client import OllamaClient

        host = self.config_manager.get('ollama.host', 'http://localhost:11434')
        model = self.config_manager.get('ollama.model', 'qwen2-vl:7b')

        client = OllamaClient(host)
        response = client.generate_text(message, model)

        return response if response else "Erro ao gerar resposta."
    
    def check_ollama_connection(self):
        """Verifica a conexão com o provedor de IA selecionado."""
        try:
            provider = self.config_manager.get('ai_provider.selected', 'ollama')

            if provider == 'gemini':
                self.check_gemini_connection()
            else:
                self.check_ollama_connection_internal()

        except Exception as e:
            self.ai_output.insert(tk.END, f"❌ Erro ao verificar conexão: {str(e)}\n")
            self.ai_output.see(tk.END)
            self.logger.error(f"Erro ao verificar conexão: {str(e)}")

    def check_ollama_connection_internal(self):
        """Verifica a conexão com Ollama."""
        try:
            from ..ai.ollama_client import OllamaClient
            
            host = self.config_manager.get('ollama.host', 'http://localhost:11434')
            client = OllamaClient(host)
            
            self.ai_output.insert(tk.END, f"Verificando conexão com Ollama em {host}...\n")
            self.ai_output.see(tk.END)
            self.root.update()
            
            if client.check_connection():
                models = client.list_models()
                self.ai_output.insert(tk.END, "✅ Conexão estabelecida com sucesso!\n\n")
                self.ai_output.insert(tk.END, f"Modelos disponíveis: {', '.join(models) if models else 'Nenhum modelo encontrado'}\n")
                self.logger.info("Conexão com Ollama verificada com sucesso")
            else:
                self.ai_output.insert(tk.END, "❌ Falha na conexão com Ollama.\n")
                self.ai_output.insert(tk.END, "Verifique se o Ollama está rodando.\n")
                self.ai_output.insert(tk.END, "Execute: ollama serve\n")
                self.logger.warning("Falha na conexão com Ollama")
            
            self.ai_output.see(tk.END)
            
        except Exception as e:
            self.ai_output.insert(tk.END, f"❌ Erro ao verificar conexão Ollama: {str(e)}\n")
            self.ai_output.see(tk.END)
            self.logger.error(f"Erro ao verificar conexão Ollama: {str(e)}")
    
    def check_gemini_connection(self):
        """Verifica a conexão com Gemini."""
        try:
            from ..ai.gemini_client import GeminiClient

            api_key = self.config_manager.get('gemini.api_key')
            model = self.config_manager.get('gemini.model', 'gemini-3.5-flash')

            if not api_key:
                self.ai_output.insert(tk.END, "❌ API Key do Gemini não configurada.\n")
                self.ai_output.insert(tk.END, "Configure a API Key nas configurações (⚙️).\n")
                self.ai_output.see(tk.END)
                return

            client = GeminiClient(api_key, model)

            self.ai_output.insert(tk.END, f"Verificando conexão com Gemini ({model})...\n")
            self.ai_output.see(tk.END)
            self.root.update()

            if client.check_connection():
                models = client.list_models()
                self.ai_output.insert(tk.END, "✅ Conexão estabelecida com sucesso!\n\n")
                self.ai_output.insert(tk.END, f"Modelos disponíveis: {len(models)}\n")
                self.logger.info("Conexão com Gemini verificada com sucesso")
            else:
                self.ai_output.insert(tk.END, "❌ Falha na conexão com Gemini.\n")
                self.ai_output.insert(tk.END, "Verifique se a API Key está correta.\n")
                self.logger.warning("Falha na conexão com Gemini")

            self.ai_output.see(tk.END)

        except Exception as e:
            self.ai_output.insert(tk.END, f"❌ Erro ao verificar conexão Gemini: {str(e)}\n")
            self.ai_output.see(tk.END)
            self.logger.error(f"Erro ao verificar conexão Gemini: {str(e)}")

    def analyze_image_with_ai(self):
        """Analisa a imagem selecionada com IA."""
        selected_items = self.ai_tree.selection()
        if not selected_items:
            messagebox.showwarning("Aviso", "Selecione uma imagem na aba IA para analisar!")
            return
        
        try:
            item = self.ai_tree.item(selected_items[0])
            file_path = item['values'][2] if len(item['values']) > 2 else None
            
            if not file_path:
                messagebox.showwarning("Aviso", "Erro ao obter caminho do arquivo!")
                return
            
            if not file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
                messagebox.showwarning("Aviso", "Selecione uma imagem (.jpg, .jpeg, .png, .gif, .bmp, .webp)!")
                return
            
            provider = self.config_manager.get('ai_provider.selected', 'ollama')
            
            self.ai_output.insert(tk.END, f"Analisando imagem: {os.path.basename(file_path)}\n")
            self.ai_output.insert(tk.END, f"Provedor: {provider}\n")
            self.ai_output.insert(tk.END, "-" * 50 + "\n")
            self.ai_output.see(tk.END)
            self.root.update()
            
            if provider == 'gemini':
                result = self.analyze_with_gemini(file_path)
            else:
                result = self.analyze_with_ollama(file_path)

            if result:
                self.ai_output.insert(tk.END, f"Contexto: {result['context']}\n")
                self.ai_output.insert(tk.END, f"Sugestão de nome: {result['suggested_name']}\n")
                self.ai_output.insert(tk.END, f"Categoria: {result['category']}\n")
            
            self.ai_output.insert(tk.END, "-" * 50 + "\n\n")
            self.ai_output.see(tk.END)
            
            self.logger.info(f"Imagem analisada com IA ({provider}): {file_path}")
            
        except Exception as e:
            self.ai_output.insert(tk.END, f"❌ Erro ao analisar imagem: {str(e)}\n")
            self.ai_output.see(tk.END)
            self.logger.error(f"Erro ao analisar imagem com IA: {str(e)}")
    
    def analyze_with_ollama(self, file_path: str) -> dict:
        """Analisa imagem com Ollama."""
        from ..ai.image_analyzer import ImageAnalyzer

        host = self.config_manager.get('ollama.host', 'http://localhost:11434')
        model = self.config_manager.get('ollama.model', 'qwen2-vl:7b')

        self.ai_output.insert(tk.END, f"Modelo: {model}\n")
        self.ai_output.see(tk.END)
        self.root.update()

        analyzer = ImageAnalyzer(host, model)
        return analyzer.analyze_image(file_path)

    def analyze_with_gemini(self, file_path: str) -> dict:
        """Analisa imagem com Gemini."""
        from ..ai.gemini_client import GeminiClient

        api_key = self.config_manager.get('gemini.api_key')
        model = self.config_manager.get('gemini.model', 'gemini-3.5-flash')

        if not api_key:
            self.ai_output.insert(tk.END, "❌ API Key do Gemini não configurada.\n")
            self.ai_output.see(tk.END)
            return None

        self.ai_output.insert(tk.END, f"Modelo: {model}\n")
        self.ai_output.see(tk.END)
        self.root.update()

        client = GeminiClient(api_key, model)
        return client.analyze_image_for_file_organization(file_path)

    def classify_files_with_ai(self):
        """Classifica os arquivos com IA."""
        selected_items = self.ai_tree.selection()
        if not selected_items:
            messagebox.showwarning("Aviso", "Selecione arquivos na aba IA para classificar!")
            return
        
        try:
            # Coleta caminhos dos arquivos selecionados
            file_paths = []
            for item in selected_items:
                item_data = self.ai_tree.item(item)
                file_path = item_data['values'][2] if len(item_data['values']) > 2 else None
                if file_path and file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
                    file_paths.append(file_path)
            
            if not file_paths:
                messagebox.showwarning("Aviso", "Selecione imagens (.jpg, .jpeg, .png, .gif, .bmp, .webp) para classificar!")
                return
            
            provider = self.config_manager.get('ai_provider.selected', 'ollama')

            self.ai_output.insert(tk.END, f"Classificando {len(file_paths)} imagens com IA ({provider})...\n")
            self.ai_output.insert(tk.END, "-" * 50 + "\n")
            self.ai_output.see(tk.END)
            self.root.update()
            
            if provider == 'gemini':
                results = self.classify_with_gemini(file_paths)
            else:
                results = self.classify_with_ollama(file_paths)
            
            for i, result in enumerate(results):
                if result:
                    self.ai_output.insert(tk.END, f"{os.path.basename(file_paths[i])} -> {result['category']}\n")
                    self.ai_output.see(tk.END)
                    self.root.update()
            
            self.ai_output.insert(tk.END, "-" * 50 + "\n")
            self.ai_output.insert(tk.END, f"Classificação concluída: {len(results)} arquivos\n\n")
            self.ai_output.see(tk.END)
            
            self.logger.info(f"Arquivos classificados com IA ({provider}): {len(results)} imagens")
            
        except Exception as e:
            self.ai_output.insert(tk.END, f"❌ Erro ao classificar arquivos: {str(e)}\n")
            self.ai_output.see(tk.END)
            self.logger.error(f"Erro ao classificar arquivos com IA: {str(e)}")
    
    def classify_with_ollama(self, file_paths: list) -> list:
        """Classifica imagens com Ollama."""
        from ..ai.context_classifier import ContextClassifier

        host = self.config_manager.get('ollama.host', 'http://localhost:11434')
        model = self.config_manager.get('ollama.model', 'qwen2-vl:7b')

        self.ai_output.insert(tk.END, f"Modelo: {model}\n")
        self.ai_output.see(tk.END)
        self.root.update()

        classifier = ContextClassifier(host, model)
        return classifier.classify_batch(file_paths)

    def classify_with_gemini(self, file_paths: list) -> list:
        """Classifica imagens com Gemini."""
        from ..ai.gemini_client import GeminiClient

        api_key = self.config_manager.get('gemini.api_key')
        model = self.config_manager.get('gemini.model', 'gemini-3.5-flash')

        if not api_key:
            self.ai_output.insert(tk.END, "❌ API Key do Gemini não configurada.\n")
            self.ai_output.see(tk.END)
            return []

        self.ai_output.insert(tk.END, f"Modelo: {model}\n")
        self.ai_output.see(tk.END)
        self.root.update()

        client = GeminiClient(api_key, model)
        return client.classify_batch(file_paths)

    def rename_with_ai(self):
        """Renomeia arquivos com IA."""
        selected_items = self.ai_tree.selection()
        if not selected_items:
            messagebox.showwarning("Aviso", "Selecione arquivos na aba IA para renomear!")
            return
        
        try:
            # Coleta caminhos dos arquivos selecionados
            file_paths = []
            for item in selected_items:
                item_data = self.ai_tree.item(item)
                file_path = item_data['values'][2] if len(item_data['values']) > 2 else None
                if file_path and file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
                    file_paths.append(file_path)

            if not file_paths:
                messagebox.showwarning("Aviso", "Selecione imagens (.jpg, .jpeg, .png, .gif, .bmp, .webp) para renomear!")
                return
            
            provider = self.config_manager.get('ai_provider.selected', 'ollama')

            result = messagebox.askyesno(
                "Confirmação",
                f"Deseja renomear {len(file_paths)} imagens com IA ({provider})?\n"
                "Os arquivos serão renomeados baseados no conteúdo analisado."
            )
            
            if not result:
                return
            
            self.ai_output.insert(tk.END, f"Renomeando {len(file_paths)} imagens com IA...\n")
            self.ai_output.insert(tk.END, f"Provedor: {provider}\n")
            self.ai_output.insert(tk.END, "-" * 50 + "\n")
            self.ai_output.see(tk.END)
            self.root.update()
            
            renamed_count = 0
            error_count = 0
            
            for file_path in file_paths:
                try:
                    old_name = os.path.basename(file_path)

                    if provider == 'gemini':
                        result = self.analyze_with_gemini(file_path)
                    else:
                        result = self.analyze_with_ollama(file_path)

                    if not result:
                        error_count += 1
                        continue
                    
                    suggested_name = result['suggested_name']
                    
                    # Adiciona extensão original
                    extension = os.path.splitext(file_path)[1]
                    new_name = suggested_name + extension
                    
                    # Renomeia
                    directory = os.path.dirname(file_path)
                    self.batch_renamer = BatchRenamer(directory)
                    new_path = self.batch_renamer.rename_file(file_path, new_name)
                    
                    self.ai_output.insert(tk.END, f"{old_name} -> {os.path.basename(new_path)}\n")
                    renamed_count += 1
                    self.ai_output.see(tk.END)
                    self.root.update()
                    
                except Exception as e:
                    error_count += 1
                    self.ai_output.insert(tk.END, f"Erro ao renomear {os.path.basename(file_path)}: {str(e)}\n")
                    self.ai_output.see(tk.END)
            
            self.ai_output.insert(tk.END, "-" * 50 + "\n")
            self.ai_output.insert(tk.END, f"Renomeamento concluído: {renamed_count} arquivos, {error_count} erros\n\n")
            self.ai_output.see(tk.END)
            
            self.logger.info(f"Renomeamento com IA ({provider}) concluído: {renamed_count} arquivos")
            
            # Reescaneia para atualizar
            self.scan_files()
            
        except Exception as e:
            self.ai_output.insert(tk.END, f"❌ Erro ao renomear com IA: {str(e)}\n")
            self.ai_output.see(tk.END)
            self.logger.error(f"Erro ao renomear com IA: {str(e)}")

    def select_directory(self):
        """Abre diálogo para selecionar diretório e escaneia automaticamente."""
        directory = filedialog.askdirectory(title="Selecione o diretório para escanear")
        if directory:
            self.selected_directory.set(directory)
            self.logger.info(f"Diretório selecionado: {directory}")
            self.status_label.config(text=f"Diretório selecionado: {directory}")
            # Auto scan após selecionar
            self.scan_files()

    def scan_files(self):
        """Escaneia o diretório selecionado e mostra os arquivos."""
        directory = self.selected_directory.get()
        
        if not directory:
            messagebox.showwarning("Aviso", "Selecione um diretório primeiro!")
            self.logger.warning("Tentativa de escanear sem selecionar diretório")
            return
        
        if not os.path.isdir(directory):
            messagebox.showerror("Erro", "Diretório inválido!")
            self.logger.error(f"Diretório inválido: {directory}")
            return
        
        try:
            self.status_label.config(text="Escaneando...")
            self.root.update()
            
            # Escaneia o diretório
            self.scanned_files = scan_directory(directory)
            
            # Limpa a treeview principal
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Limpa a treeview da IA
            for item in self.ai_tree.get_children():
                self.ai_tree.delete(item)

            # Adiciona os arquivos na treeview principal
            for file_info in self.scanned_files:
                self.tree.insert('', tk.END, values=(
                    file_info.name,
                    file_info.category,
                    format_size(file_info.size),
                    file_info.path
                ))
            
            # Adiciona os arquivos na treeview da IA
            for file_info in self.scanned_files:
                file_ext = os.path.splitext(file_info.path)[1].lower()
                file_type = "Imagem" if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'] else "Outro"
                self.ai_tree.insert('', tk.END, values=(
                    file_info.name,
                    file_type,
                    file_info.path
                ))

            # Mostra resumo
            summary = get_scan_summary(self.scanned_files)
            self.status_label.config(
                text=f"Encontrados {summary['total_files']} arquivos ({summary['total_size_formatted']})"
            )
            
            self.logger.info(f"Escaneamento concluído: {summary['total_files']} arquivos")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao escanear: {str(e)}")
            self.logger.error(f"Erro ao escanear: {str(e)}")
            self.status_label.config(text="Erro ao escanear")

    def on_file_select(self, event):
        """Chamado quando um arquivo é selecionado na lista."""
        selected_items = self.tree.selection()
        if selected_items:
            item = self.tree.item(selected_items[0])
            file_path = item['values'][3]  # Coluna do caminho

            if self.image_preview:
                if file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                    self.image_preview.load_image(file_path)
                else:
                    self.image_preview.clear_preview()
    
    def organize_files(self):
        """Organiza os arquivos escaneados por categoria."""
        if not self.scanned_files:
            messagebox.showwarning("Aviso", "Escaneie arquivos primeiro!")
            self.logger.warning("Tentativa de organizar sem escanear arquivos")
            return
        
        directory = self.selected_directory.get()
        
        try:
            # Pergunta confirmação
            result = messagebox.askyesno(
                "Confirmação",
                f"Deseja organizar {len(self.scanned_files)} arquivos?\n"
                "Os arquivos serão movidos para pastas por categoria (imagem, vídeo)."
            )
            
            if not result:
                self.logger.info("Organização cancelada pelo usuário")
                return
            
            self.status_label.config(text="Organizando...")
            self.root.update()
            
            # Cria o organizador
            self.organizer = FileOrganizer(directory)
            
            # Organiza os arquivos
            results = self.organizer.organize_files(self.scanned_files)
            
            # Mostra resultado
            moved_count = len(results['moved'])
            error_count = len(results['errors'])
            
            message = f"Organização concluída!\n\n"
            message += f"Arquivos movidos: {moved_count}\n"
            
            if error_count > 0:
                message += f"Erros: {error_count}\n"
                message += "\nArquivos com erro:\n"
                for error in results['errors']:
                    message += f"- {error['file']}: {error['error']}\n"
            
            messagebox.showinfo("Resultado", message)
            self.status_label.config(text=f"Organização concluída: {moved_count} arquivos movidos")
            
            self.logger.info(f"Organização concluída: {moved_count} arquivos movidos, {error_count} erros")
            
            # Limpa a lista após organizar
            self.scanned_files = []
            for item in self.tree.get_children():
                self.tree.delete(item)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao organizar: {str(e)}")
            self.logger.error(f"Erro ao organizar: {str(e)}")
            self.status_label.config(text="Erro ao organizar")
    
    def move_to_folder(self):
        """Move os arquivos selecionados para uma pasta personalizada."""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Aviso", "Selecione pelo menos um arquivo para mover!")
            self.logger.warning("Tentativa de mover sem selecionar arquivos")
            return
        
        try:
            # Pergunta para selecionar/criar pasta
            directory = self.selected_directory.get()
            if not directory:
                messagebox.showwarning("Aviso", "Selecione um diretório primeiro!")
                return
            
            # Abre diálogo para selecionar pasta destino
            destination_folder = filedialog.askdirectory(
                title="Selecione a pasta de destino",
                initialdir=directory
            )
            
            if not destination_folder:
                self.logger.info("Seleção de pasta cancelada pelo usuário")
                return
            
            # Pergunta confirmação
            result = messagebox.askyesno(
                "Confirmação",
                f"Deseja mover {len(selected_items)} arquivos selecionados para:\n{destination_folder}?"
            )
            
            if not result:
                self.logger.info("Movimento cancelado pelo usuário")
                return
            
            self.status_label.config(text="Movendo arquivos...")
            self.root.update()
            
            # Move os arquivos
            moved_count = 0
            error_count = 0
            errors = []
            
            for item in selected_items:
                try:
                    item_data = self.tree.item(item)
                    file_path = item_data['values'][3]  # Coluna do caminho
                    filename = item_data['values'][0]  # Coluna do nome
                    
                    destination = os.path.join(destination_folder, filename)
                    
                    # Trata duplicatas
                    if os.path.exists(destination):
                        base_name = os.path.splitext(filename)[0]
                        extension = os.path.splitext(filename)[1]
                        counter = 1
                        while os.path.exists(destination):
                            new_filename = f"{base_name}_{counter}{extension}"
                            destination = os.path.join(destination_folder, new_filename)
                            counter += 1
                    
                    # Move o arquivo
                    shutil.move(file_path, destination)
                    moved_count += 1
                    self.logger.info(f"Movido: {file_path} -> {destination}")
                    
                except Exception as e:
                    error_count += 1
                    error_msg = f"Erro ao mover {item_data['values'][0]}: {str(e)}"
                    errors.append(error_msg)
                    self.logger.error(error_msg)
            
            # Mostra resultado
            message = f"Movimento concluído!\n\n"
            message += f"Arquivos movidos: {moved_count}\n"
            
            if error_count > 0:
                message += f"Erros: {error_count}\n\n"
                message += "Arquivos com erro:\n"
                for error in errors:
                    message += f"- {error}\n"
            
            messagebox.showinfo("Resultado", message)
            self.status_label.config(text=f"Movimento concluído: {moved_count} arquivos movidos")
            
            self.logger.info(f"Movimento concluído: {moved_count} arquivos movidos, {error_count} erros")
            
            # Reescaneia para atualizar a lista
            self.scan_files()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao mover arquivos: {str(e)}")
            self.logger.error(f"Erro ao mover arquivos: {str(e)}")
            self.status_label.config(text="Erro ao mover")
    
    def rename_selected(self):
        """Renomeia o arquivo selecionado."""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Aviso", "Selecione um arquivo para renomear!")
            return
        
        if len(selected_items) > 1:
            messagebox.showwarning("Aviso", "Selecione apenas um arquivo para renomear!")
            return
        
        item = self.tree.item(selected_items[0])
        file_path = item['values'][3]  # Coluna do caminho
        current_name = item['values'][0]  # Coluna do nome
        
        # Pede novo nome
        new_name = simpledialog.askstring(
            "Renomear Arquivo",
            f"Nome atual: {current_name}\n\nDigite o novo nome:",
            initialvalue=current_name
        )
        
        if not new_name:
            return
        
        if new_name == current_name:
            messagebox.showinfo("Info", "O nome é o mesmo, nada foi alterado.")
            return
        
        try:
            directory = self.selected_directory.get()
            self.batch_renamer = BatchRenamer(directory)
            
            new_path = self.batch_renamer.rename_file(file_path, new_name)
            
            messagebox.showinfo("Sucesso", f"Arquivo renomeado para: {os.path.basename(new_path)}")
            self.logger.info(f"Arquivo renomeado: {file_path} -> {new_path}")
            
            # Reescaneia para atualizar a lista
            self.scan_files()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao renomear: {str(e)}")
            self.logger.error(f"Erro ao renomear: {str(e)}")
    
    def open_settings(self):
        """Abre a janela de configurações."""
        try:
            self.settings_window = SettingsWindow(self.root, self.config_manager)
            self.logger.info("Janela de configurações aberta")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir configurações: {str(e)}")
            self.logger.error(f"Erro ao abrir configurações: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
