from PySide6.QtCore import QObject, Signal, Property
from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex
from typing import List, Optional
import os


class FileItem(QObject):
    """Modelo de item de arquivo com signals Qt."""

    data_changed = Signal()

    def __init__(self, name: str, path: str, size: int, category: str = "outro", file_type: str = "outro"):
        super().__init__()
        self.name = name
        self.path = path
        self.size = size
        self.category = category
        self.file_type = file_type

    @property
    def extension(self) -> str:
        """Retorna a extensão do arquivo."""
        return os.path.splitext(self.name)[1].lower()

    @property
    def is_image(self) -> bool:
        """Verifica se é uma imagem."""
        return self.extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']

    @property
    def size_formatted(self) -> str:
        """Retorna o tamanho formatado."""
        if self.size < 1024:
            return f"{self.size} B"
        elif self.size < 1024 * 1024:
            return f"{self.size / 1024:.1f} KB"
        elif self.size < 1024 * 1024 * 1024:
            return f"{self.size / (1024 * 1024):.1f} MB"
        else:
            return f"{self.size / (1024 * 1024 * 1024):.1f} GB"


class FileListModel(QAbstractListModel):
    """Modelo de lista de arquivos para QListView/QTreeView."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._files: List[FileItem] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._files)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._files):
            return None

        file_item = self._files[index.row()]

        if role == Qt.DisplayRole:
            return file_item.name
        elif role == Qt.UserRole:
            return file_item
        elif role == Qt.ToolTipRole:
            return f"{file_item.path}\n{file_item.size_formatted}"

        return None

    def add_file(self, file_item: FileItem):
        """Adiciona um arquivo ao modelo."""
        self.beginInsertRows(QModelIndex(), len(self._files), len(self._files))
        self._files.append(file_item)
        self.endInsertRows()

    def remove_file(self, index: int):
        """Remove um arquivo do modelo."""
        if 0 <= index < len(self._files):
            self.beginRemoveRows(QModelIndex(), index, index)
            self._files.pop(index)
            self.endRemoveRows()

    def clear(self):
        """Limpa todos os arquivos do modelo."""
        self.beginResetModel()
        self._files.clear()
        self.endResetModel()

    def get_file(self, index: int) -> Optional[FileItem]:
        """Retorna um arquivo pelo índice."""
        if 0 <= index < len(self._files):
            return self._files[index]
        return None

    def get_files(self) -> List[FileItem]:
        """Retorna todos os arquivos."""
        return self._files.copy()

    def filter_by_type(self, file_type: str) -> List[FileItem]:
        """Filtra arquivos por tipo."""
        return [f for f in self._files if f.file_type == file_type]

    def filter_by_category(self, category: str) -> List[FileItem]:
        """Filtra arquivos por categoria."""
        return [f for f in self._files if f.category == category]

    def sort_by_name(self, ascending: bool = True):
        """Ordena por nome."""
        self.beginResetModel()
        self._files.sort(key=lambda x: x.name.lower(), reverse=not ascending)
        self.endResetModel()

    def sort_by_size(self, ascending: bool = True):
        """Ordena por tamanho."""
        self.beginResetModel()
        self._files.sort(key=lambda x: x.size, reverse=not ascending)
        self.endResetModel()

    def sort_by_category(self, ascending: bool = True):
        """Ordena por categoria."""
        self.beginResetModel()
        self._files.sort(key=lambda x: x.category.lower(), reverse=not ascending)
        self.endResetModel()
