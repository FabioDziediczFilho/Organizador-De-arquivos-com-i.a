from PySide6.QtWidgets import (
    QPushButton, QLineEdit, QComboBox, QCheckBox,
    QFrame, QLabel, QGroupBox, QSpinBox, QDoubleSpinBox
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QColor, QPen
from typing import Optional


class FluentButton(QPushButton):
    """Botão com estilo Fluent Design."""

    def __init__(self, text: str = "", accent: bool = True, secondary: bool = False, parent=None):
        super().__init__(text, parent)
        self._accent = accent
        self._secondary = secondary

        # Aplicar propriedades para estilo
        if accent:
            self.setProperty("accent", True)
        elif secondary:
            self.setProperty("secondary", True)

        self.setMinimumHeight(36)
        self.setCursor(Qt.PointingHandCursor)


class FluentCard(QFrame):
    """Card com estilo Fluent Design."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("card", True)
        self.setFrameShape(QFrame.NoFrame)


class FluentLineEdit(QLineEdit):
    """LineEdit com estilo Fluent Design."""

    def __init__(self, placeholder: str = "", parent=None):
        super().__init__(parent)
        if placeholder:
            self.setPlaceholderText(placeholder)
        self.setMinimumHeight(36)


class FluentComboBox(QComboBox):
    """ComboBox com estilo Fluent Design."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(36)


class FluentCheckBox(QCheckBox):
    """CheckBox com estilo Fluent Design."""

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)


class FluentLabel(QLabel):
    """Label com estilo Fluent Design."""

    def __init__(self, text: str = "", heading: bool = False, subheading: bool = False, parent=None):
        super().__init__(text, parent)

        if heading:
            self.setProperty("heading", True)
            self.setStyleSheet("font-size: 16pt; font-weight: 600; color: #0078D4;")
        elif subheading:
            self.setProperty("subheading", True)
            self.setStyleSheet("font-size: 12pt; font-weight: 500; color: #888888;")


class FluentGroupBox(QGroupBox):
    """GroupBox com estilo Fluent Design."""

    def __init__(self, title: str = "", parent=None):
        super().__init__(title, parent)


class FluentSpinBox(QSpinBox):
    """SpinBox com estilo Fluent Design."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(36)


class FluentDoubleSpinBox(QDoubleSpinBox):
    """DoubleSpinBox com estilo Fluent Design."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(36)


class FluentSeparator(QFrame):
    """Separador horizontal com estilo Fluent Design."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setStyleSheet("background-color: #4A4A4A; max-height: 1px;")


class FluentVerticalSeparator(QFrame):
    """Separador vertical com estilo Fluent Design."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setStyleSheet("background-color: #4A4A4A; max-width: 1px;")
