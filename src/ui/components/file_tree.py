from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView, QStyle
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QStandardItemModel
from typing import List, Optional
from ...models.file_model import FileItem
import os


class FileTreeWidget(QTreeWidget):
    """TreeWidget de arquivos com estilo moderno."""
    
    # Signals
    file_selected = Signal(object)  # FileItem
    files_selected = Signal(list)  # List[FileItem]
    file_double_clicked = Signal(object)  # FileItem
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configurações
        self.setHeaderLabels(["Nome", "Tipo", "Tamanho", "Caminho"])
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.setSelectionMode(QTreeWidget.ExtendedSelection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # Ajustar colunas
        header = self.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        # Conectar signals
        self.itemSelectionChanged.connect(self._on_selection_changed)
        self.itemDoubleClicked.connect(self._on_double_clicked)
    
    def load_files(self, file_data: List):
        """Carrega arquivos na treeview. Aceita FileItem ou dicionários."""
        self.clear()
        
        for data in file_data:
            # Converter dicionário para FileItem se necessário
            if isinstance(data, dict):
                file_item = FileItem(
                    name=data.get('name', ''),
                    path=data.get('path', ''),
                    size=data.get('size', 0),
                    category=data.get('category', 'outro'),
                    file_type=data.get('file_type', 'outro')
                )
            else:
                file_item = data
            
            item = QTreeWidgetItem()
            item.setText(0, file_item.name)
            item.setText(1, file_item.file_type)
            item.setText(2, file_item.size_formatted)
            item.setText(3, file_item.path)
            
            # Armazenar referência ao FileItem usando setData
            try:
                item.setData(0, Qt.UserRole, file_item)
                print(f"[DEBUG] Armazenado FileItem no item: {file_item.name}")
            except Exception as e:
                print(f"[ERROR] Erro ao armazenar FileItem: {e}")
                import traceback
                traceback.print_exc()
            
            # Ícone baseado no tipo
            if file_item.is_image:
                item.setIcon(0, self.style().standardIcon(QStyle.SP_FileIcon))
            else:
                item.setIcon(0, self.style().standardIcon(QStyle.SP_FileIcon))
            
            self.addTopLevelItem(item)
        
        # Ordenar por nome
        self.sortByColumn(0, Qt.AscendingOrder)
    
    def _on_selection_changed(self):
        """Callback quando seleção muda."""
        selected_items = self.selectedItems()
        
        print(f"[DEBUG] Seleção mudou: {len(selected_items)} itens selecionados")
        
        if len(selected_items) >= 1:
            try:
                print(f"[DEBUG] Tentando obter dados do item 0")
                file_item = selected_items[0].data(0, Qt.UserRole)
                print(f"[DEBUG] FileItem selecionado: {type(file_item)}")
                if file_item:
                    print(f"[DEBUG] FileItem.name: {file_item.name if hasattr(file_item, 'name') else 'N/A'}")
                else:
                    print("[DEBUG] FileItem é None")
                
                if len(selected_items) == 1:
                    print("[DEBUG] Emitindo file_selected")
                    self.file_selected.emit(file_item)
            except Exception as e:
                print(f"[ERROR] Erro ao obter dados do item: {e}")
                import traceback
                traceback.print_exc()
        
        try:
            file_items = [item.data(0, Qt.UserRole) for item in selected_items]
            print(f"[DEBUG] Emitindo files_selected com {len(file_items)} itens")
            self.files_selected.emit(file_items)
        except Exception as e:
            print(f"[ERROR] Erro ao emitir files_selected: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Callback quando item é double-clicked."""
        file_item = item.data(0, Qt.UserRole)
        self.file_double_clicked.emit(file_item)
    
    def get_selected_files(self) -> List[FileItem]:
        """Retorna arquivos selecionados."""
        selected_items = self.selectedItems()
        return [item.data(0, Qt.UserRole) for item in selected_items]
    
    def get_selected_file(self) -> Optional[FileItem]:
        """Retorna o arquivo selecionado (ou None se múltiplos)."""
        selected_items = self.selectedItems()
        if len(selected_items) == 1:
            return selected_items[0].data(0, Qt.UserRole)
        return None
    
    def filter_by_type(self, file_type: str):
        """Filtra arquivos por tipo."""
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            file_item = item.data(0, Qt.UserRole)
            if file_item.file_type == file_type:
                item.setHidden(False)
            else:
                item.setHidden(True)
    
    def filter_by_category(self, category: str):
        """Filtra arquivos por categoria."""
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            file_item = item.data(0, Qt.UserRole)
            if file_item.category == category:
                item.setHidden(False)
            else:
                item.setHidden(True)
    
    def clear_filter(self):
        """Limpa filtros."""
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            item.setHidden(False)
    
    def select_all(self):
        """Seleciona todos os itens."""
        self.selectAll()
    
    def clear_selection(self):
        """Limpa seleção."""
        self.clearSelection()
