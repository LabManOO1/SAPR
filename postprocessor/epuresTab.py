from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QComboBox, QLabel)
import matplotlib

matplotlib.use('Qt5Agg')
from postprocessor.epure_widget import EpureWidget


class EpuresTab(QWidget):
    """Вкладка с эпюрами"""

    def __init__(self, postprocessor_tab):
        super().__init__()
        self.postprocessor_tab = postprocessor_tab
        self.current_data = None
        self.calculation_results = None
        self.setup_epures_tab()

    def setup_epures_tab(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Панель управления
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)

        control_layout.addWidget(QLabel("Тип эпюры:"))
        self.epure_type_combo = QComboBox()
        self.epure_type_combo.addItems(["Перемещения u(x)", "Продольные силы N(x)", "Напряжения σ(x)"])
        self.epure_type_combo.currentTextChanged.connect(self.update_epure)
        control_layout.addWidget(self.epure_type_combo)

        control_layout.addStretch()

        self.epure_widget = EpureWidget()
        layout.addLayout(control_layout)
        layout.addWidget(self.epure_widget)

    def set_data(self, data, calculation_results=None):
        """Установить данные для визуализации"""
        self.current_data = data
        self.calculation_results = calculation_results
        if data and data.get("Objects"):
            bars_data = data["Objects"][0]["list_of_values"]
            displacements = calculation_results.get('nodal_displacements', []) if calculation_results else []
            self.epure_widget.set_data(bars_data, displacements, calculation_results)
            self.update_epure()

    def update_epure(self):
        """Обновить отображение эпюры"""
        if not self.current_data:
            return

        epure_type_map = {
            "Перемещения u(x)": "displacement",
            "Продольные силы N(x)": "force",
            "Напряжения σ(x)": "stress"
        }

        epure_type = epure_type_map.get(self.epure_type_combo.currentText(), "displacement")
        self.epure_widget.set_epure_type(epure_type)