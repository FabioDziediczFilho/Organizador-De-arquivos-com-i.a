from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from typing import Optional


class AccessibilityHelper:
    """Helper para funcionalidades de acessibilidade."""
    
    @staticmethod
    def set_accessible_name(widget: QWidget, name: str):
        """Define nome acessível para widget."""
        widget.setAccessibleName(name)
    
    @staticmethod
    def set_accessible_description(widget: QWidget, description: str):
        """Define descrição acessível para widget."""
        widget.setAccessibleDescription(description)
    
    @staticmethod
    def set_focus_policy(widget: QWidget, policy: Qt.FocusPolicy = Qt.StrongFocus):
        """Define política de foco para widget."""
        widget.setFocusPolicy(policy)
    
    @staticmethod
    def set_shortcut(widget: QWidget, shortcut: str):
        """Define atalho de teclado para widget."""
        widget.setShortcut(shortcut)
    
    @staticmethod
    def enable_tab_navigation(widget: QWidget):
        """Habilita navegação por tab."""
        widget.setFocusPolicy(Qt.TabFocus)
    
    @staticmethod
    def set_tooltip(widget: QWidget, tooltip: str):
        """Define tooltip para widget."""
        widget.setToolTip(tooltip)
    
    @staticmethod
    def set_status_tip(widget: QWidget, status_tip: str):
        """Define status tip para widget."""
        widget.setStatusTip(status_tip)
    
    @staticmethod
    def enable_keyboard_navigation(widget: QWidget):
        """Habilita navegação por teclado."""
        widget.setFocusPolicy(Qt.StrongFocus)
    
    @staticmethod
    def set_role(widget: QWidget, role: Qt.AccessibleRole):
        """Define papel acessível para widget."""
        widget.setAccessibleRole(role)
    
    @staticmethod
    def configure_button(button, name: str, description: str, shortcut: Optional[str] = None):
        """Configura acessibilidade para botão."""
        AccessibilityHelper.set_accessible_name(button, name)
        AccessibilityHelper.set_accessible_description(button, description)
        AccessibilityHelper.set_focus_policy(button, Qt.StrongFocus)
        
        if shortcut:
            AccessibilityHelper.set_shortcut(button, shortcut)
    
    @staticmethod
    def configure_input(input_widget, name: str, description: str, placeholder: str = ""):
        """Configura acessibilidade para input."""
        AccessibilityHelper.set_accessible_name(input_widget, name)
        AccessibilityHelper.set_accessible_description(input_widget, description)
        AccessibilityHelper.set_focus_policy(input_widget, Qt.StrongFocus)
        
        if placeholder:
            input_widget.setPlaceholderText(placeholder)
    
    @staticmethod
    def configure_list(list_widget, name: str, description: str):
        """Configura acessibilidade para lista."""
        AccessibilityHelper.set_accessible_name(list_widget, name)
        AccessibilityHelper.set_accessible_description(list_widget, description)
        AccessibilityHelper.set_role(list_widget, Qt.AccessibleRole.List)
        AccessibilityHelper.set_focus_policy(list_widget, Qt.StrongFocus)
    
    @staticmethod
    def configure_tree(tree_widget, name: str, description: str):
        """Configura acessibilidade para tree."""
        AccessibilityHelper.set_accessible_name(tree_widget, name)
        AccessibilityHelper.set_accessible_description(tree_widget, description)
        AccessibilityHelper.set_role(tree_widget, Qt.AccessibleRole.Tree)
        AccessibilityHelper.set_focus_policy(tree_widget, Qt.StrongFocus)
    
    @staticmethod
    def configure_tab(tab_widget, name: str, description: str):
        """Configura acessibilidade para tab widget."""
        AccessibilityHelper.set_accessible_name(tab_widget, name)
        AccessibilityHelper.set_accessible_description(tab_widget, description)
        AccessibilityHelper.set_role(tab_widget, Qt.AccessibleRole.PageTabList)
        AccessibilityHelper.set_focus_policy(tab_widget, Qt.StrongFocus)
    
    @staticmethod
    def configure_dialog(dialog, name: str, description: str):
        """Configura acessibilidade para dialog."""
        AccessibilityHelper.set_accessible_name(dialog, name)
        AccessibilityHelper.set_accessible_description(dialog, description)
        AccessibilityHelper.set_role(dialog, Qt.AccessibleRole.Dialog)
    
    @staticmethod
    def configure_window(window, name: str, description: str):
        """Configura acessibilidade para janela."""
        AccessibilityHelper.set_accessible_name(window, name)
        AccessibilityHelper.set_accessible_description(window, description)
        AccessibilityHelper.set_role(window, Qt.AccessibleRole.Window)
    
    @staticmethod
    def announce_message(widget: QWidget, message: str):
        """Anuncia mensagem para leitores de tela."""
        # PySide6 não tem suporte nativo, mas podemos usar accessibleDescription
        widget.setAccessibleDescription(message)
        # Forçar atualização de acessibilidade
        widget.update()
    
    @staticmethod
    def enable_high_contrast_mode(widget: QWidget, enabled: bool = True):
        """Habilita modo de alto contraste."""
        if enabled:
            widget.setProperty("high-contrast", True)
        else:
            widget.setProperty("high-contrast", False)
    
    @staticmethod
    def enable_large_text(widget: QWidget, enabled: bool = True):
        """Habilita texto grande."""
        if enabled:
            widget.setProperty("large-text", True)
        else:
            widget.setProperty("large-text", False)
    
    @staticmethod
    def enable_screen_reader_support(widget: QWidget, enabled: bool = True):
        """Habilita suporte a leitor de tela."""
        if enabled:
            widget.setProperty("screen-reader", True)
        else:
            widget.setProperty("screen-reader", False)
