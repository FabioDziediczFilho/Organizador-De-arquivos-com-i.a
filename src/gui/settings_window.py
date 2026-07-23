import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from ..utils.config_manager import ConfigManager
from ..utils.logger import Logger


class SettingsWindow:
    """Janela de configurações do aplicativo."""
    
    def __init__(self, parent: tk.Widget, config_manager: ConfigManager):
        """
        Inicializa a janela de configurações.
        
        Args:
            parent: Widget pai
            config_manager: Gerenciador de configurações
        """
        self.parent = parent
        self.config_manager = config_manager
        self.logger = Logger("SettingsWindow")
        self.window = None
        self.variables = {}
        
        self.create_window()
    
    def create_window(self):
        """Cria a janela de configurações."""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Configurações")
        self.window.geometry("600x500")
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configura grid
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Notebook para categorias
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Abas
        self.create_ollama_tab(notebook)
        self.create_gemini_tab(notebook)
        self.create_organization_tab(notebook)
        self.create_preview_tab(notebook)
        self.create_logging_tab(notebook)
        self.create_ui_tab(notebook)
        
        # Botões
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(button_frame, text="Salvar", command=self.save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.window.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Restaurar Padrões", command=self.restore_defaults).pack(side=tk.RIGHT, padx=5)
        
        self.logger.info("Janela de configurações criada")
    
    def create_ollama_tab(self, notebook):
        """Cria a aba de configurações do Ollama."""
        tab = ttk.Frame(notebook, padding="10")
        notebook.add(tab, text="Ollama")
        
        # Frame principal
        frame = ttk.Frame(tab)
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Host
        ttk.Label(frame, text="Host do Ollama:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.variables['ollama_host'] = tk.StringVar(value=self.config_manager.get('ollama.host'))
        ttk.Entry(frame, textvariable=self.variables['ollama_host'], width=40).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Modelo
        ttk.Label(frame, text="Modelo:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.variables['ollama_model'] = tk.StringVar(value=self.config_manager.get('ollama.model'))
        ttk.Entry(frame, textvariable=self.variables['ollama_model'], width=40).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Habilitar IA
        ttk.Label(frame, text="Habilitar IA:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.variables['ollama_enabled'] = tk.BooleanVar(value=self.config_manager.get('ollama.enabled'))
        ttk.Checkbutton(frame, variable=self.variables['ollama_enabled']).grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Informação
        info_label = ttk.Label(frame, text="Nota: Ollama precisa estar instalado e rodando para usar IA", 
                              foreground="gray", wraplength=400)
        info_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        # Configura grid
        frame.columnconfigure(1, weight=1)
    
    def create_gemini_tab(self, notebook):
        """Cria a aba de configurações do Gemini."""
        tab = ttk.Frame(notebook, padding="10")
        notebook.add(tab, text="Gemini")
        
        # Frame principal
        frame = ttk.Frame(tab)
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # API Key
        ttk.Label(frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.variables['gemini_api_key'] = tk.StringVar(value=self.config_manager.get('gemini.api_key'))
        ttk.Entry(frame, textvariable=self.variables['gemini_api_key'], width=50, show="*").grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Modelo
        ttk.Label(frame, text="Modelo:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.variables['gemini_model'] = tk.StringVar(value=self.config_manager.get('gemini.model'))
        gemini_models = ['gemini-3.5-flash', 'gemini-3.1-flash-lite', 'gemini-2.0-flash']
        ttk.Combobox(frame, textvariable=self.variables['gemini_model'], values=gemini_models, 
                    state='readonly', width=20).grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Habilitar Gemini
        ttk.Label(frame, text="Habilitar Gemini:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.variables['gemini_enabled'] = tk.BooleanVar(value=self.config_manager.get('gemini.enabled'))
        ttk.Checkbutton(frame, variable=self.variables['gemini_enabled']).grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Selecionar provedor
        ttk.Label(frame, text="Provedor de IA:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.variables['ai_provider'] = tk.StringVar(value=self.config_manager.get('ai_provider.selected'))
        providers = ['ollama', 'gemini']
        ttk.Combobox(frame, textvariable=self.variables['ai_provider'], values=providers, 
                    state='readonly', width=20).grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Informação
        info_label = ttk.Label(frame, text="Nota: Obtenha sua API Key em https://makersuite.google.com/app/apikey", 
                              foreground="gray", wraplength=400)
        info_label.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        # Configura grid
        frame.columnconfigure(1, weight=1)
    
    def create_organization_tab(self, notebook):
        """Cria a aba de configurações de organização."""
        tab = ttk.Frame(notebook, padding="10")
        notebook.add(tab, text="Organização")
        
        # Frame principal
        frame = ttk.Frame(tab)
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Criar backup
        ttk.Label(frame, text="Criar backup antes de mover:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.variables['org_backup'] = tk.BooleanVar(value=self.config_manager.get('organization.create_backup'))
        ttk.Checkbutton(frame, variable=self.variables['org_backup']).grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Confirmar ações
        ttk.Label(frame, text="Confirmar antes de ações:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.variables['org_confirm'] = tk.BooleanVar(value=self.config_manager.get('organization.confirm_actions'))
        ttk.Checkbutton(frame, variable=self.variables['org_confirm']).grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Renomear automaticamente
        ttk.Label(frame, text="Renomear automaticamente:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.variables['org_rename'] = tk.BooleanVar(value=self.config_manager.get('organization.auto_rename'))
        ttk.Checkbutton(frame, variable=self.variables['org_rename']).grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Configura grid
        frame.columnconfigure(1, weight=1)
    
    def create_preview_tab(self, notebook):
        """Cria a aba de configurações de preview."""
        tab = ttk.Frame(notebook, padding="10")
        notebook.add(tab, text="Preview")
        
        # Frame principal
        frame = ttk.Frame(tab)
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Largura máxima
        ttk.Label(frame, text="Largura máxima do preview:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.variables['preview_width'] = tk.IntVar(value=self.config_manager.get('preview.max_width'))
        ttk.Spinbox(frame, from_=200, to=800, textvariable=self.variables['preview_width'], width=10).grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Altura máxima
        ttk.Label(frame, text="Altura máxima do preview:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.variables['preview_height'] = tk.IntVar(value=self.config_manager.get('preview.max_height'))
        ttk.Spinbox(frame, from_=200, to=600, textvariable=self.variables['preview_height'], width=10).grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Carregar automaticamente
        ttk.Label(frame, text="Carregar preview automaticamente:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.variables['preview_auto'] = tk.BooleanVar(value=self.config_manager.get('preview.auto_load'))
        ttk.Checkbutton(frame, variable=self.variables['preview_auto']).grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Configura grid
        frame.columnconfigure(1, weight=1)
    
    def create_logging_tab(self, notebook):
        """Cria a aba de configurações de logging."""
        tab = ttk.Frame(notebook, padding="10")
        notebook.add(tab, text="Logs")
        
        # Frame principal
        frame = ttk.Frame(tab)
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Nível de log
        ttk.Label(frame, text="Nível de log:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.variables['log_level'] = tk.StringVar(value=self.config_manager.get('logging.level'))
        log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        ttk.Combobox(frame, textvariable=self.variables['log_level'], values=log_levels, 
                    state='readonly', width=15).grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Salvar logs
        ttk.Label(frame, text="Salvar logs em arquivo:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.variables['log_save'] = tk.BooleanVar(value=self.config_manager.get('logging.save_logs'))
        ttk.Checkbutton(frame, variable=self.variables['log_save']).grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Diretório de logs
        ttk.Label(frame, text="Diretório de logs:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.variables['log_dir'] = tk.StringVar(value=self.config_manager.get('logging.log_dir'))
        ttk.Entry(frame, textvariable=self.variables['log_dir'], width=40).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Configura grid
        frame.columnconfigure(1, weight=1)
    
    def create_ui_tab(self, notebook):
        """Cria a aba de configurações da interface."""
        tab = ttk.Frame(notebook, padding="10")
        notebook.add(tab, text="Interface")
        
        # Frame principal
        frame = ttk.Frame(tab)
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Tema
        ttk.Label(frame, text="Tema:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.variables['ui_theme'] = tk.StringVar(value=self.config_manager.get('ui.theme'))
        themes = ['default', 'clam', 'alt', 'classic']
        ttk.Combobox(frame, textvariable=self.variables['ui_theme'], values=themes, 
                    state='readonly', width=15).grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Idioma
        ttk.Label(frame, text="Idioma:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.variables['ui_language'] = tk.StringVar(value=self.config_manager.get('ui.language'))
        languages = ['pt-BR', 'en-US', 'es-ES']
        ttk.Combobox(frame, textvariable=self.variables['ui_language'], values=languages, 
                    state='readonly', width=15).grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Largura da janela
        ttk.Label(frame, text="Largura da janela:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.variables['ui_width'] = tk.IntVar(value=self.config_manager.get('ui.window_width'))
        ttk.Spinbox(frame, from_=800, to=1920, textvariable=self.variables['ui_width'], width=10).grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Altura da janela
        ttk.Label(frame, text="Altura da janela:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.variables['ui_height'] = tk.IntVar(value=self.config_manager.get('ui.window_height'))
        ttk.Spinbox(frame, from_=600, to=1080, textvariable=self.variables['ui_height'], width=10).grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Configura grid
        frame.columnconfigure(1, weight=1)
    
    def save_settings(self):
        """Salva as configurações."""
        try:
            # Ollama
            self.config_manager.set('ollama.host', self.variables['ollama_host'].get())
            self.config_manager.set('ollama.model', self.variables['ollama_model'].get())
            self.config_manager.set('ollama.enabled', self.variables['ollama_enabled'].get())
            
            # Gemini
            self.config_manager.set('gemini.api_key', self.variables['gemini_api_key'].get())
            self.config_manager.set('gemini.model', self.variables['gemini_model'].get())
            self.config_manager.set('gemini.enabled', self.variables['gemini_enabled'].get())
            
            # AI Provider
            self.config_manager.set('ai_provider.selected', self.variables['ai_provider'].get())
            
            # Organização
            self.config_manager.set('organization.create_backup', self.variables['org_backup'].get())
            self.config_manager.set('organization.confirm_actions', self.variables['org_confirm'].get())
            self.config_manager.set('organization.auto_rename', self.variables['org_rename'].get())
            
            # Preview
            self.config_manager.set('preview.max_width', self.variables['preview_width'].get())
            self.config_manager.set('preview.max_height', self.variables['preview_height'].get())
            self.config_manager.set('preview.auto_load', self.variables['preview_auto'].get())
            
            # Logging
            self.config_manager.set('logging.level', self.variables['log_level'].get())
            self.config_manager.set('logging.save_logs', self.variables['log_save'].get())
            self.config_manager.set('logging.log_dir', self.variables['log_dir'].get())
            
            # UI
            self.config_manager.set('ui.theme', self.variables['ui_theme'].get())
            self.config_manager.set('ui.language', self.variables['ui_language'].get())
            self.config_manager.set('ui.window_width', self.variables['ui_width'].get())
            self.config_manager.set('ui.window_height', self.variables['ui_height'].get())
            
            # Salva no arquivo
            if self.config_manager.save_config():
                messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
                self.logger.info("Configurações salvas pelo usuário")
                self.window.destroy()
            else:
                messagebox.showerror("Erro", "Erro ao salvar configurações!")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar configurações: {str(e)}")
            self.logger.error(f"Erro ao salvar configurações: {str(e)}")
    
    def restore_defaults(self):
        """Restaura as configurações padrão."""
        result = messagebox.askyesno(
            "Confirmar",
            "Deseja restaurar todas as configurações para os valores padrão?"
        )
        
        if result:
            try:
                self.config_manager.reset_to_default()
                self.config_manager.save_config()
                
                # Atualiza as variáveis
                self.variables['ollama_host'].set(self.config_manager.get('ollama.host'))
                self.variables['ollama_model'].set(self.config_manager.get('ollama.model'))
                self.variables['ollama_enabled'].set(self.config_manager.get('ollama.enabled'))
                self.variables['gemini_api_key'].set(self.config_manager.get('gemini.api_key'))
                self.variables['gemini_model'].set(self.config_manager.get('gemini.model'))
                self.variables['gemini_enabled'].set(self.config_manager.get('gemini.enabled'))
                self.variables['ai_provider'].set(self.config_manager.get('ai_provider.selected'))
                self.variables['org_backup'].set(self.config_manager.get('organization.create_backup'))
                self.variables['org_confirm'].set(self.config_manager.get('organization.confirm_actions'))
                self.variables['org_rename'].set(self.config_manager.get('organization.auto_rename'))
                self.variables['preview_width'].set(self.config_manager.get('preview.max_width'))
                self.variables['preview_height'].set(self.config_manager.get('preview.max_height'))
                self.variables['preview_auto'].set(self.config_manager.get('preview.auto_load'))
                self.variables['log_level'].set(self.config_manager.get('logging.level'))
                self.variables['log_save'].set(self.config_manager.get('logging.save_logs'))
                self.variables['log_dir'].set(self.config_manager.get('logging.log_dir'))
                self.variables['ui_theme'].set(self.config_manager.get('ui.theme'))
                self.variables['ui_language'].set(self.config_manager.get('ui.language'))
                self.variables['ui_width'].set(self.config_manager.get('ui.window_width'))
                self.variables['ui_height'].set(self.config_manager.get('ui.window_height'))
                
                messagebox.showinfo("Sucesso", "Configurações restauradas para os valores padrão!")
                self.logger.info("Configurações restauradas para os valores padrão")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao restaurar configurações: {str(e)}")
                self.logger.error(f"Erro ao restaurar configurações: {str(e)}")
