from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QObject, Signal, QParallelAnimationGroup, QSequentialAnimationGroup
from PySide6.QtWidgets import QWidget
from typing import Optional


class AnimationManager(QObject):
    """Gerenciador de animações para UI."""
    
    animation_finished = Signal()
    
    def __init__(self):
        super().__init__()
        self._animations = {}
    
    def fade_in(self, widget: QWidget, duration: int = 300, start_opacity: float = 0.0, end_opacity: float = 1.0):
        """Animação de fade-in."""
        animation = QPropertyAnimation(widget, b"windowOpacity")
        animation.setDuration(duration)
        animation.setStartValue(start_opacity)
        animation.setEndValue(end_opacity)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        animation.finished.connect(self.animation_finished.emit)
        animation.start()
        
        return animation
    
    def fade_out(self, widget: QWidget, duration: int = 300, start_opacity: float = 1.0, end_opacity: float = 0.0):
        """Animação de fade-out."""
        animation = QPropertyAnimation(widget, b"windowOpacity")
        animation.setDuration(duration)
        animation.setStartValue(start_opacity)
        animation.setEndValue(end_opacity)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        animation.finished.connect(self.animation_finished.emit)
        animation.start()
        
        return animation
    
    def slide_in_left(self, widget: QWidget, duration: int = 300, distance: int = 100):
        """Animação de slide-in da esquerda."""
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        
        start_geometry = widget.geometry()
        end_geometry = widget.geometry()
        start_geometry.translate(-distance, 0)
        
        animation.setStartValue(start_geometry)
        animation.setEndValue(end_geometry)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        animation.finished.connect(self.animation_finished.emit)
        animation.start()
        
        return animation
    
    def slide_in_right(self, widget: QWidget, duration: int = 300, distance: int = 100):
        """Animação de slide-in da direita."""
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        
        start_geometry = widget.geometry()
        end_geometry = widget.geometry()
        start_geometry.translate(distance, 0)
        
        animation.setStartValue(start_geometry)
        animation.setEndValue(end_geometry)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        animation.finished.connect(self.animation_finished.emit)
        animation.start()
        
        return animation
    
    def slide_in_top(self, widget: QWidget, duration: int = 300, distance: int = 100):
        """Animação de slide-in de cima."""
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        
        start_geometry = widget.geometry()
        end_geometry = widget.geometry()
        start_geometry.translate(0, -distance)
        
        animation.setStartValue(start_geometry)
        animation.setEndValue(end_geometry)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        animation.finished.connect(self.animation_finished.emit)
        animation.start()
        
        return animation
    
    def scale_in(self, widget: QWidget, duration: int = 300, start_scale: float = 0.8, end_scale: float = 1.0):
        """Animação de scale-in."""
        # Para PySide6, precisamos usar geometry para simular scale
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        
        current_geometry = widget.geometry()
        center = current_geometry.center()
        
        start_width = int(current_geometry.width() * start_scale)
        start_height = int(current_geometry.height() * start_scale)
        start_x = center.x() - start_width // 2
        start_y = center.y() - start_height // 2
        
        animation.setStartValue(start_x, start_y, start_width, start_height)
        animation.setEndValue(current_geometry)
        animation.setEasingCurve(QEasingCurve.OutBack)
        
        animation.finished.connect(self.animation_finished.emit)
        animation.start()
        
        return animation
    
    def bounce(self, widget: QWidget, duration: int = 500):
        """Animação de bounce."""
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.OutBounce)
        
        current_geometry = widget.geometry()
        start_geometry = current_geometry.translated(0, -20)
        
        animation.setStartValue(start_geometry)
        animation.setEndValue(current_geometry)
        
        animation.finished.connect(self.animation_finished.emit)
        animation.start()
        
        return animation
    
    def parallel_animations(self, animations: list):
        """Executa animações em paralelo."""
        group = QParallelAnimationGroup()
        
        for animation in animations:
            group.addAnimation(animation)
        
        group.finished.connect(self.animation_finished.emit)
        group.start()
        
        return group
    
    def sequential_animations(self, animations: list):
        """Executa animações em sequência."""
        group = QSequentialAnimationGroup()
        
        for animation in animations:
            group.addAnimation(animation)
        
        group.finished.connect(self.animation_finished.emit)
        group.start()
        
        return group
    
    def stop_all(self):
        """Para todas as animações ativas."""
        for animation in self._animations.values():
            if animation.state() == animation.Running:
                animation.stop()
        self._animations.clear()
