from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QTimer, QThreadPool, QRunnable
from typing import Optional, Callable
import threading


class PerformanceOptimizer:
    """Otimizador de performance para UI."""
    
    def __init__(self):
        self._thread_pool = QThreadPool()
        self._thread_pool.setMaxThreadCount(4)
        self._debounce_timers = {}
        self._throttle_timers = {}
    
    def run_async(self, func: Callable, callback: Optional[Callable] = None):
        """Executa função em thread separada."""
        class Worker(QRunnable):
            def __init__(self, func, callback):
                super().__init__()
                self.func = func
                self.callback = callback
            
            def run(self):
                try:
                    result = self.func()
                    if self.callback:
                        self.callback(result, None)
                except Exception as e:
                    if self.callback:
                        self.callback(None, e)
        
        worker = Worker(func, callback)
        self._thread_pool.start(worker)
    
    def debounce(self, func: Callable, delay: int = 300, key: str = "default") -> Callable:
        """Debounce - executa função apenas após delay sem novas chamadas."""
        def wrapper(*args, **kwargs):
            if key in self._debounce_timers:
                self._debounce_timers[key].stop()
                self._debounce_timers[key].deleteLater()
            
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: func(*args, **kwargs))
            timer.start(delay)
            
            self._debounce_timers[key] = timer
        
        return wrapper
    
    def throttle(self, func: Callable, delay: int = 300, key: str = "default") -> Callable:
        """Throttle - executa função no máximo uma vez a cada delay."""
        def wrapper(*args, **kwargs):
            if key in self._throttle_timers and self._throttle_timers[key].isActive():
                return
            
            func(*args, **kwargs)
            
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: self._throttle_timers.pop(key, None))
            timer.start(delay)
            
            self._throttle_timers[key] = timer
        
        return wrapper
    
    def lazy_load(self, widget: QWidget, load_func: Callable):
        """Lazy load - carrega widget apenas quando visível."""
        widget.hide()
        
        def check_visibility():
            if widget.isVisible():
                load_func()
                widget.show()
            else:
                QTimer.singleShot(100, check_visibility)
        
        QTimer.singleShot(100, check_visibility)
    
    def virtual_scroll(self, widget, item_count: int, item_height: int):
        """Virtual scroll - renderiza apenas itens visíveis."""
        # Implementação básica de virtual scroll
        widget.setProperty("virtual-scroll", True)
        widget.setProperty("item-count", item_count)
        widget.setProperty("item-height", item_height)
    
    def cache_images(self, enabled: bool = True, max_size: int = 100):
        """Cache de imagens."""
        # Configurar cache de imagens
        pass
    
    def optimize_rendering(self, widget: QWidget):
        """Otimiza rendering de widget."""
        widget.setAttribute(widget.WA_OpaquePaintEvent, True)
        widget.setAttribute(widget.WA_NoSystemBackground, True)
        widget.setAttribute(widget.WA_DontCreateNativeAncestors, True)
    
    def disable_animations(self, widget: QWidget, disabled: bool = True):
        """Desabilita animações para melhorar performance."""
        widget.setProperty("animations-disabled", disabled)
    
    def set_thread_pool_size(self, size: int):
        """Define tamanho do pool de threads."""
        self._thread_pool.setMaxThreadCount(size)
    
    def clear_caches(self):
        """Limpa todos os caches."""
        for timer in self._debounce_timers.values():
            timer.stop()
            timer.deleteLater()
        self._debounce_timers.clear()
        
        for timer in self._throttle_timers.values():
            timer.stop()
            timer.deleteLater()
        self._throttle_timers.clear()
    
    def cleanup(self):
        """Limpa recursos."""
        self.clear_caches()
        self._thread_pool.clear()


class ResponsiveLayout:
    """Helper para layouts responsivos."""
    
    @staticmethod
    def set_minimum_size(widget: QWidget, min_width: int, min_height: int):
        """Define tamanho mínimo responsivo."""
        widget.setMinimumSize(min_width, min_height)
    
    @staticmethod
    def set_maximum_size(widget: QWidget, max_width: int, max_height: int):
        """Define tamanho máximo responsivo."""
        widget.setMaximumSize(max_width, max_height)
    
    @staticmethod
    def set_size_policy(widget: QWidget, horizontal: str, vertical: str):
        """Define política de tamanho."""
        from PySide6.QtWidgets import QSizePolicy
        
        h_policy = getattr(QSizePolicy, horizontal, QSizePolicy.Preferred)
        v_policy = getattr(QSizePolicy, vertical, QSizePolicy.Preferred)
        
        widget.setSizePolicy(h_policy, v_policy)
    
    @staticmethod
    def enable_stretch(widget: QWidget, horizontal: bool = True, vertical: bool = False):
        """Habilita stretch do widget."""
        from PySide6.QtWidgets import QSizePolicy
        
        h_policy = QSizePolicy.Expanding if horizontal else QSizePolicy.Preferred
        v_policy = QSizePolicy.Expanding if vertical else QSizePolicy.Preferred
        
        widget.setSizePolicy(h_policy, v_policy)
    
    @staticmethod
    def set_aspect_ratio(widget: QWidget, ratio: float):
        """Define aspect ratio do widget."""
        widget.setProperty("aspect-ratio", ratio)
    
    @staticmethod
    def enable_responsive(widget: QWidget, enabled: bool = True):
        """Habilita comportamento responsivo."""
        widget.setProperty("responsive", enabled)


class MemoryMonitor:
    """Monitor de uso de memória."""
    
    def __init__(self):
        self._memory_usage = 0
        self._max_memory = 100 * 1024 * 1024  # 100MB
    
    def check_memory(self) -> int:
        """Verifica uso de memória em bytes."""
        import psutil
        process = psutil.Process()
        self._memory_usage = process.memory_info().rss
        return self._memory_usage
    
    def is_memory_high(self) -> bool:
        """Verifica se uso de memória está alto."""
        return self.check_memory() > self._max_memory
    
    def get_memory_mb(self) -> float:
        """Retorna uso de memória em MB."""
        return self.check_memory() / (1024 * 1024)
    
    def set_max_memory(self, max_mb: int):
        """Define limite máximo de memória em MB."""
        self._max_memory = max_mb * 1024 * 1024
    
    def cleanup_if_needed(self, cleanup_func: Callable):
        """Executa cleanup se memória estiver alta."""
        if self.is_memory_high():
            cleanup_func()
