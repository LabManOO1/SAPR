from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTabWidget)
import matplotlib

matplotlib.use('Qt5Agg')
from postprocessor.epuresTab import EpuresTab
from postprocessor.graphsTabWidget import GraphsTab


class PostProcessorTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_data = None
        self.calculation_results = None
        self.setup_postprocessor()

    def setup_postprocessor(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Создаем вкладки
        self.tabs = QTabWidget()

        # Вкладка с эпюрами
        self.epures_tab = EpuresTab(self)

        # Вкладка с графиками
        self.graphs_tab = GraphsTab(self)

        self.tabs.addTab(self.epures_tab, "Эпюры")
        self.tabs.addTab(self.graphs_tab, "Графики")

        layout.addWidget(self.tabs)

    def set_data(self, data, calculation_results=None):
        """Установить данные для визуализации"""
        self.current_data = data
        self.calculation_results = calculation_results

        # Передаем данные в обе вкладки
        self.epures_tab.set_data(data, calculation_results)
        self.graphs_tab.set_data(data, calculation_results)








