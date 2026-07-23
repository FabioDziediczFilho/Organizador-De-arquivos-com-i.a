from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QPushButton
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QImage, QPainter, QColor
from typing import Optional
from ...models.file_model import FileItem
from .styled_widgets import FluentButton, FluentLabel
import os


class ImagePreviewWidget(QWidget):
    """Widget de preview de imagens com zoom."""

    # Signals
    image_loaded = Signal(str)  # file_path
    image_error = Signal(str)  # error_message

    def __init__(self, parent=None):
        super().__init__(parent)

        self._current_file: Optional[FileItem] = None
        self._pixmap: Optional[QPixmap] = None
        self._scale_factor = 1.0

        self._setup_ui()

    def _setup_ui(self):
        """Configura a UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # ScrollArea para zoom
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)

        # Label para mostrar imagem
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(400, 300)
        self.image_label.setStyleSheet("background-color: #2D2D2D; border: 1px solid #4A4A4A;")
        self.image_label.setText("Selecione uma imagem para preview")

        self.scroll_area.setWidget(self.image_label)
        layout.addWidget(self.scroll_area)

        # Info label
        self.info_label = FluentLabel("", subheading=True)
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

        # Botões de zoom
        button_layout = QVBoxLayout()

        zoom_in_btn = FluentButton("Zoom In", secondary=True)
        zoom_in_btn.clicked.connect(self.zoom_in)

        zoom_out_btn = FluentButton("Zoom Out", secondary=True)
        zoom_out_btn.clicked.connect(self.zoom_out)

        fit_btn = FluentButton("Ajustar", secondary=True)
        fit_btn.clicked.connect(self.fit_to_window)

        button_layout.addWidget(zoom_in_btn)
        button_layout.addWidget(zoom_out_btn)
        button_layout.addWidget(fit_btn)

        layout.addLayout(button_layout)

    def load_image(self, file_item: Optional[FileItem]):
        """Carrega uma imagem."""
        self._current_file = file_item

        if not file_item or not file_item.is_image:
            self.clear()
            return

        try:
            file_path = file_item.path
            if not os.path.exists(file_path):
                self.image_error.emit(f"Arquivo não encontrado: {file_path}")
                self.clear()
                return

            # Carregar imagem
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                self.image_error.emit(f"Erro ao carregar imagem: {file_path}")
                self.clear()
                return

            self._pixmap = pixmap
            self._scale_factor = 1.0

            # Mostrar imagem ajustada
            self.fit_to_window()

            # Atualizar info
            self.info_label.setText(f"{file_item.name} ({file_item.size_formatted})")

            self.image_loaded.emit(file_path)

        except Exception as e:
            self.image_error.emit(f"Erro ao carregar imagem: {str(e)}")
            self.clear()

    def clear(self):
        """Limpa o preview."""
        self._current_file = None
        self._pixmap = None
        self._scale_factor = 1.0
        self.image_label.clear()
        self.image_label.setText("Selecione uma imagem para preview")
        self.info_label.setText("")

    def fit_to_window(self):
        """Ajusta imagem ao tamanho da janela."""
        if not self._pixmap:
            return

        window_size = self.scroll_area.size()
        pixmap_size = self._pixmap.size()

        if window_size.width() <= 0 or window_size.height() <= 0 or pixmap_size.width() <= 0 or pixmap_size.height() <= 0:
            self._scale_factor = 1.0
            return

        scale_x = (window_size.width() - 20) / pixmap_size.width()
        scale_y = (window_size.height() - 20) / pixmap_size.height()

        self._scale_factor = max(0.0, min(scale_x, scale_y, 1.0))
        self._update_display()

    def zoom_in(self):
        """Aumenta o zoom."""
        if not self._pixmap:
            return

        self._scale_factor *= 1.2
        self._update_display()

    def zoom_out(self):
        """Diminui o zoom."""
        if not self._pixmap:
            return

        self._scale_factor /= 1.2
        self._update_display()

    def _update_display(self):
        """Atualiza a imagem exibida."""
        if not self._pixmap:
            return

        if self._scale_factor <= 0:
            self._scale_factor = 1.0

        scaled_pixmap = self._pixmap.scaled(
            self._pixmap.size() * self._scale_factor,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.image_label.setPixmap(scaled_pixmap)

    def get_current_file(self) -> Optional[FileItem]:
        """Retorna o arquivo atual."""
        return self._current_file

    def resizeEvent(self, event):
        """Redimensiona o widget."""
        super().resizeEvent(event)
        if self._pixmap:
            self.fit_to_window()
