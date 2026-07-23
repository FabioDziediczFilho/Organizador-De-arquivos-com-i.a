import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from typing import List, Optional
import os

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
        ttk.Button(button_frame, text="Organizar por Padrão", command=self.organize_by_pattern).pack(side=tk.LEFT, padx=6)
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
        self.tree = ttk.Treeview(files_panel, columns=('name', 'category', 'size', 'path'), show='headings', height=12)
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

    def select_directory(self):
        """Abre diálogo para selecionar diretório."""
        directory = filedialog.askdirectory(title="Selecione o diretório para escanear")
        if directory:
            self.selected_directory.set(directory)
            self.logger.info(f"Diretório selecionado: {directory}")
            self.status_label.config(text=f"Diretório selecionado: {directory}")

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
            
            # Limpa a treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Adiciona os arquivos na treeview
            for file_info in self.scanned_files:
                self.tree.insert('', tk.END, values=(
                    file_info.name,
                    file_info.category,
                    format_size(file_info.size),
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
    
    def organize_by_pattern(self):
        """Organiza os arquivos por padrão de nome."""
        if not self.scanned_files:
            messagebox.showwarning("Aviso", "Escaneie arquivos primeiro!")
            self.logger.warning("Tentativa de organizar por padrão sem escanear arquivos")
            return
        
        directory = self.selected_directory.get()
        
        try:
            # Pergunta confirmação
            result = messagebox.askyesno(
                "Confirmação",
                f"Deseja organizar {len(self.scanned_files)} arquivos por padrão de nome?\n"
                "Arquivos com nomes similares serão movidos para pastas específicas.\n"
                "Ex: 'foto casamento 1', 'foto casamento 2' -> pasta 'Foto casamento'"
            )
            
            if not result:
                self.logger.info("Organização por padrão cancelada pelo usuário")
                return
            
            self.status_label.config(text="Organizando por padrão...")
            self.root.update()
            
            # Cria o renomeador
            self.batch_renamer = BatchRenamer(directory)
            
            # Obtém caminhos dos arquivos
            file_paths = [f.path for f in self.scanned_files]
            
            # Organiza por padrão
            results = self.batch_renamer.organize_by_pattern(file_paths)
            
            # Mostra resultado
            moved_count = len(results['moved'])
            error_count = len(results['errors'])
            
            message = f"Organização por padrão concluída!\n\n"
            message += f"Arquivos movidos: {moved_count}\n"
            message += f"Pastas criadas: {len(results['groups'])}\n\n"
            
            if results['groups']:
                message += "Pastas criadas:\n"
                for folder_name, group_info in results['groups'].items():
                    message += f"- {folder_name}: {group_info['count']} arquivos\n"
            
            if error_count > 0:
                message += f"\nErros: {error_count}\n"
                for error in results['errors']:
                    message += f"- {error['file']}: {error['error']}\n"
            
            messagebox.showinfo("Resultado", message)
            self.status_label.config(text=f"Organização concluída: {moved_count} arquivos movidos")
            
            self.logger.info(f"Organização por padrão concluída: {moved_count} arquivos movidos, {len(results['groups'])} pastas")
            
            # Limpa a lista após organizar
            self.scanned_files = []
            for item in self.tree.get_children():
                self.tree.delete(item)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao organizar por padrão: {str(e)}")
            self.logger.error(f"Erro ao organizar por padrão: {str(e)}")
            self.status_label.config(text="Erro ao organizar")
    
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
