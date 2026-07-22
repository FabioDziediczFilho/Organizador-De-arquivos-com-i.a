import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Optional
import os

from ..core.file_scanner import scan_directory, get_scan_summary, format_size
from ..core.file_organizer import FileOrganizer
from ..utils.logger import Logger

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
        self.root.geometry("800x600")
        
        # Inicializa o logger
        self.logger = Logger("FileOrganizerGUI")
        
        # Variáveis
        self.selected_directory = tk.StringVar()
        self.scanned_files = []
        self.organizer = None
        
        # Cria a interface
        self.create_widgets()
        
        self.logger.info("GUI inicializada com sucesso")

    def create_widgets(self):
        """Cria todos os widgets da interface."""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configura grid para expandir
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Label e Entry para diretório
        ttk.Label(main_frame, text="Diretório:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.selected_directory).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        ttk.Button(main_frame, text="Selecionar", command=self.select_directory).grid(row=0, column=2, pady=5)
        
        # Botão para escanear
        ttk.Button(main_frame, text="Escanear Arquivos", command=self.scan_files).grid(row=1, column=0, columnspan=3, pady=10)
        
        # Lista de arquivos
        ttk.Label(main_frame, text="Arquivos encontrados:").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        # Treeview para mostrar arquivos
        self.tree = ttk.Treeview(main_frame, columns=('name', 'category', 'size'), show='headings')
        self.tree.heading('name', text='Nome')
        self.tree.heading('category', text='Categoria')
        self.tree.heading('size', text='Tamanho')
        self.tree.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=3, column=3, sticky=(tk.N, tk.S))
        
        # Botão para organizar
        ttk.Button(main_frame, text="Organizar Arquivos", command=self.organize_files).grid(row=4, column=0, columnspan=3, pady=10)
        
        # Label de status
        self.status_label = ttk.Label(main_frame, text="Pronto", relief=tk.SUNKEN)
        self.status_label.grid(row=5, column=0, columnspan=4, sticky=(tk.W, tk.E))


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
                    format_size(file_info.size)
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

    def organize_files(self):
        """Organiza os arquivos escaneados."""
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
                "Os arquivos serão movidos para pastas por categoria."
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
if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()     