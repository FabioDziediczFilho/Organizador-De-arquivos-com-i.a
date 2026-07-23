import os
import pytest
from PIL import Image
from PySide6.QtWidgets import QApplication

from src.models.file_model import FileItem
from src.ui.components.image_preview import ImagePreviewWidget


@pytest.fixture(scope="session")
def qt_app():
    app = QApplication.instance() or QApplication([])
    return app


def test_fit_to_window_keeps_scale_positive_when_widget_is_not_yet_resized(tmp_path, qt_app):
    image_path = tmp_path / "sample.png"
    Image.new("RGB", (100, 200), color="red").save(image_path)

    widget = ImagePreviewWidget()
    file_item = FileItem(
        name=image_path.name,
        path=str(image_path),
        size=100,
        category="imagem",
        file_type="Imagem",
    )

    widget.load_image(file_item)

    assert widget._scale_factor > 0
    assert widget._pixmap is not None
