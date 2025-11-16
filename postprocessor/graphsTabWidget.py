from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QComboBox, QLabel, QPushButton, QCheckBox)
import matplotlib

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from postprocessor.mplCanvas import MplCanvas


class GraphsTab(QWidget):
    """Вкладка с графиками всех компонентов для выбранного стержня"""

    def __init__(self, postprocessor_tab):
        super().__init__()
        self.postprocessor_tab = postprocessor_tab
        self.current_data = None
        self.calculation_results = None
        self.setup_graphs_tab()

    def setup_graphs_tab(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Верхняя панель управления
        top_control_layout = QHBoxLayout()

        # Выбор стержня
        top_control_layout.addWidget(QLabel("Стержень:"))
        self.bar_combo = QComboBox()
        self.bar_combo.currentTextChanged.connect(self.update_graph)
        top_control_layout.addWidget(self.bar_combo)

        top_control_layout.addStretch()

        self.export_btn = QPushButton("Экспорт графиков")
        self.export_btn.clicked.connect(self.export_graphs)
        top_control_layout.addWidget(self.export_btn)

        layout.addLayout(top_control_layout)

        # Нижняя панель с чекбоксами
        bottom_control_layout = QHBoxLayout()

        # Чекбоксы для выбора графиков
        bottom_control_layout.addWidget(QLabel("Показать графики:"))

        self.show_u_checkbox = QCheckBox("Перемещения u(x)")
        self.show_u_checkbox.setChecked(True)
        self.show_u_checkbox.stateChanged.connect(self.update_graph)
        bottom_control_layout.addWidget(self.show_u_checkbox)

        self.show_n_checkbox = QCheckBox("Продольные силы N(x)")
        self.show_n_checkbox.setChecked(True)
        self.show_n_checkbox.stateChanged.connect(self.update_graph)
        bottom_control_layout.addWidget(self.show_n_checkbox)

        self.show_sigma_checkbox = QCheckBox("Напряжения σ(x)")
        self.show_sigma_checkbox.setChecked(True)
        self.show_sigma_checkbox.stateChanged.connect(self.update_graph)
        bottom_control_layout.addWidget(self.show_sigma_checkbox)

        bottom_control_layout.addStretch()

        layout.addLayout(bottom_control_layout)

        # Создаем canvas и панель инструментов
        self.graph_canvas = MplCanvas(self)
        self.toolbar = NavigationToolbar(self.graph_canvas, self)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.graph_canvas)

    def set_data(self, data, calculation_results=None):
        """Установить данные для графиков"""
        self.current_data = data
        self.calculation_results = calculation_results

        # Обновляем список стержней
        self.update_bar_list()
        self.update_graph()

    def update_bar_list(self):
        """Обновить список стержней в комбобоксе"""
        self.bar_combo.clear()

        if not self.current_data or not self.current_data.get("Objects"):
            return

        bars_data = self.current_data["Objects"][0]["list_of_values"]
        for bar in bars_data:
            self.bar_combo.addItem(f"Стержень {bar['barNumber']}")

    def update_graph(self):
        """Обновить график"""
        if not self.current_data or not self.calculation_results:
            return

        selected_bar = self.bar_combo.currentText()
        if not selected_bar:
            return

        # Извлекаем номер стержня из текста
        try:
            bar_number = int(selected_bar.split()[-1])
        except:
            return

        # Получаем выбранные графики
        show_u = self.show_u_checkbox.isChecked()
        show_n = self.show_n_checkbox.isChecked()
        show_sigma = self.show_sigma_checkbox.isChecked()

        self.graph_canvas.plot_all_components(
            self.current_data,
            self.calculation_results,
            bar_number,
            show_u,
            show_n,
            show_sigma
        )

    def export_graphs(self):
        """Экспорт графиков в файл"""
        try:
            from PyQt5.QtWidgets import QFileDialog
            filename, selected_filter = QFileDialog.getSaveFileName(
                self, "Сохранить график", "", "PNG Files (*.png);;PDF Files (*.pdf);;SVG Files (*.svg)"
            )
            if filename:
                self.graph_canvas.fig.savefig(filename, dpi=300, bbox_inches='tight')
        except:
            pass