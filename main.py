#!/usr/bin/env python3
"""
Ponto de entrada principal para o Organizador de Arquivos com IA.
"""

from src.gui.main_window import MainWindow
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
