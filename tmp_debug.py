import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
from PySide6.QtWidgets import QApplication
from src.ui.components.file_tree import FileTreeWidget

app = QApplication([])
widget = FileTreeWidget()
widget.load_files([
    {'name': 'a.png', 'path': 'C:/temp/a.png', 'size': 123, 'category': 'img', 'file_type': 'Imagem'}
])
print('items loaded', widget.topLevelItemCount())
item = widget.topLevelItem(0)
widget.setCurrentItem(item)
print('selected ok')
