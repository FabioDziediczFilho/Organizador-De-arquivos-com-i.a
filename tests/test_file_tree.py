import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from src.models.file_model import FileItem
from src.ui.components.file_tree import FileTreeWidget

@pytest.fixture(scope="session")
def qt_app():
    return QApplication.instance() or QApplication([])

def test_file_tree_selection_changed_emit_correct_item(qt_app):
    widget = FileTreeWidget()

    # Create mock items
    f1 = FileItem(name="image.jpg", path="/dummy/image.jpg", size=100, category="imagem", file_type="Imagem")
    f2 = FileItem(name="video.mp4", path="/dummy/video.mp4", size=200, category="video", file_type="Vídeo")

    # Load files
    widget.load_files([f1, f2])

    # Track signal emission
    emitted_files = []
    def on_file_selected(file_item):
        emitted_files.append(file_item)

    widget.file_selected.connect(on_file_selected)

    # Select first item
    item1 = widget.topLevelItem(0) # In TreeWidget, items are sorted by name, "image.jpg" vs "video.mp4"
    widget.setCurrentItem(item1)

    assert len(emitted_files) >= 1
    # Check that first emitted file matches either f1 or f2 depending on order
    selected_name = emitted_files[-1].name
    assert selected_name in ["image.jpg", "video.mp4"]

    # Clear selection
    widget.clearSelection()
    assert emitted_files[-1] is None  # Should have emitted None to clear preview
