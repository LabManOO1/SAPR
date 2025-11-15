from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QLabel, QMessageBox,
                             QTabWidget, QHeaderView, QTextEdit, QComboBox,
                             QDoubleSpinBox, QFormLayout, QGroupBox, QLineEdit)
from PyQt5.QtCore import Qt
import json
from processor.calculations import BarSystemCalculator
import numpy as np


class ResultsTable(QTableWidget):
    def __init__(self, headers, parent=None):
        super().__init__(parent)
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.setEditTriggers(QTableWidget.NoEditTriggers)  # Только чтение
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def set_data(self, data):
        self.setRowCount(len(data))
        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, item)


class StiffnessMatrixTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setMinimumHeight(400)

    def set_matrix_data(self, matrix):
        if not matrix:
            return

        n = len(matrix)
        self.setRowCount(n)
        self.setColumnCount(n)

        # Устанавливаем заголовки
        headers = [f"Узел {i + 1}" for i in range(n)]
        self.setHorizontalHeaderLabels(headers)
        self.setVerticalHeaderLabels(headers)

        # Заполняем данными
        for i in range(n):
            for j in range(n):
                value = matrix[i][j]
                if abs(value) < 1e-10:  # Показываем нули как 0
                    display_value = "0"
                else:
                    display_value = f"{value:.6e}"

                item = QTableWidgetItem(display_value)
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(i, j, item)


class ProcessorTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_data = None
        self.calculation_results = None
        self.setup_processor()

    def setup_processor(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Кнопка расчета
        self.calculate_btn = QPushButton("Рассчитать")
        self.calculate_btn.setMinimumHeight(40)
        self.calculate_btn.clicked.connect(self.calculate)
        self.calculate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)

        # Кнопка сохранения результатов
        self.save_btn = QPushButton("Сохранить результаты")
        self.save_btn.setMinimumHeight(35)
        self.save_btn.clicked.connect(self.save_results)
        self.save_btn.setEnabled(False)

        # Верхняя панель с кнопками
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.calculate_btn)
        top_layout.addWidget(self.save_btn)
        top_layout.addStretch(1)

        # Горизонтальный layout для групп настроек
        settings_horizontal_layout = QHBoxLayout()

        # Группа настроек для распределенных параметров (слева)
        settings_group = QGroupBox("Настройки расчета распределенных параметров")
        settings_layout = QFormLayout(settings_group)

        # Выбор стержня
        self.bar_selector = QComboBox()
        settings_layout.addRow("Стержень:", self.bar_selector)

        # Шаг дискретизации
        self.step_selector = QDoubleSpinBox()
        self.step_selector.setRange(0.01, 10.0)
        self.step_selector.setValue(0.1)
        self.step_selector.setSingleStep(0.1)
        self.step_selector.setDecimals(2)
        settings_layout.addRow("Шаг дискретизации:", self.step_selector)

        # Кнопка обновления таблицы распределенных параметров
        self.update_distributed_btn = QPushButton("Обновить таблицу")
        self.update_distributed_btn.clicked.connect(self.update_distributed_table)
        self.update_distributed_btn.setEnabled(False)
        settings_layout.addRow(self.update_distributed_btn)

        # Группа для расчета в конкретной точке (справа)
        point_calc_group = QGroupBox("Расчет параметров в конкретной точке")
        point_layout = QFormLayout(point_calc_group)

        # Выбор стержня для точечного расчета
        self.point_bar_selector = QComboBox()
        point_layout.addRow("Стержень:", self.point_bar_selector)

        # Координата x
        self.x_coordinate_input = QDoubleSpinBox()
        self.x_coordinate_input.setRange(0.0, 100.0)
        self.x_coordinate_input.setValue(0.0)
        self.x_coordinate_input.setSingleStep(0.1)
        self.x_coordinate_input.setDecimals(3)
        self.x_coordinate_input.valueChanged.connect(self.calculate_point_parameters)
        point_layout.addRow("Координата x:", self.x_coordinate_input)

        # Результаты точечного расчета
        self.point_results_layout = QFormLayout()

        self.displacement_result = QLabel("—")
        self.point_results_layout.addRow("Перемещение u(x):", self.displacement_result)

        self.force_result = QLabel("—")
        self.point_results_layout.addRow("Продольная сила Nx:", self.force_result)

        self.stress_result = QLabel("—")
        self.point_results_layout.addRow("Напряжение σ:", self.stress_result)

        point_layout.addRow(self.point_results_layout)

        # Добавляем обе группы в горизонтальный layout
        settings_horizontal_layout.addWidget(settings_group)
        settings_horizontal_layout.addWidget(point_calc_group)

        # Создаем вкладки для разных типов результатов
        self.results_tabs = QTabWidget()

        # Таблица распределенных параметров (ПЕРВАЯ вкладка)
        self.distributed_table = ResultsTable([
            "x",
            "Перемещение u(x)",
            "Продольная сила Nx",
            "Напряжение σ"
        ])

        # Таблица перемещений узлов (ВТОРАЯ вкладка)
        self.displacements_table = ResultsTable(["Узел", "Перемещение u(x)"])

        # Матрица жесткости (табличное представление)
        self.matrix_table = StiffnessMatrixTable()

        # Добавляем таблицы во вкладки (ПОМЕНЯЛИ МЕСТАМИ)
        self.results_tabs.addTab(self.distributed_table, "Распределенные параметры")
        self.results_tabs.addTab(self.displacements_table, "Перемещения узлов")
        self.results_tabs.addTab(self.matrix_table, "Матрица жесткости")

        # Статус расчета
        self.status_label = QLabel("Данные не загружены")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("padding: 10px; font-weight: bold;")

        layout.addLayout(top_layout)
        layout.addLayout(settings_horizontal_layout)  # Используем горизонтальный layout
        layout.addWidget(self.status_label)
        layout.addWidget(self.results_tabs)

    def set_data(self, data):
        """Установить данные для расчета"""
        self.current_data = data
        if data and data.get("Objects") and data["Objects"][0]["list_of_values"]:
            bars_data = data["Objects"][0]["list_of_values"]
            bars_count = len(bars_data)

            # Обновляем списки стержней
            self.bar_selector.clear()
            self.point_bar_selector.clear()
            for bar in bars_data:
                bar_text = f"Стержень {bar['barNumber']} (L={bar['length']})"
                self.bar_selector.addItem(bar_text, bar['barNumber'])
                self.point_bar_selector.addItem(bar_text, bar['barNumber'])

            # Устанавливаем максимальное значение для координаты x
            if bars_data:
                max_length = max(bar['length'] for bar in bars_data)
                self.x_coordinate_input.setRange(0.0, max_length)
                self.x_coordinate_input.setValue(0.0)

            self.status_label.setText(f"Готов к расчету. Стержней: {bars_count}")
            self.calculate_btn.setEnabled(True)
        else:
            self.status_label.setText("Нет данных для расчета")
            self.calculate_btn.setEnabled(False)
            self.update_distributed_btn.setEnabled(False)

    def calculate(self):
        """Выполнить расчеты"""
        if not self.current_data:
            QMessageBox.warning(self, "Ошибка", "Нет данных для расчета")
            return

        try:
            # Создаем калькулятор и выполняем расчеты
            calculator = BarSystemCalculator(self.current_data)
            success = calculator.calculate_all()

            if success:
                self.calculator = calculator
                self.calculation_results = calculator.get_all_results()
                self.display_results()
                self.update_distributed_btn.setEnabled(True)
                self.save_btn.setEnabled(True)
                self.status_label.setText("Расчет успешно завершен")

                # Автоматически рассчитываем параметры для текущей точки
                self.calculate_point_parameters()

                QMessageBox.information(self, "Успех", "Расчет завершен успешно!")
            else:
                QMessageBox.critical(self, "Ошибка", "Ошибка при выполнении расчетов")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка расчета: {str(e)}")
            self.status_label.setText("Ошибка расчета")

    def display_results(self):
        """Отобразить результаты расчетов"""
        if not self.calculation_results:
            return

        # Перемещения узлов
        displacements_data = []
        for i, disp in enumerate(self.calculation_results['nodal_displacements']):
            displacements_data.append([f"{i + 1}", f"{self.smart_round(disp)}"])
        self.displacements_table.set_data(displacements_data)

        # Автоматическое обновление таблицы распределенных параметров
        self.update_distributed_table()

        # Матрица жесткости в табличном виде
        self.matrix_table.set_matrix_data(self.calculation_results['stiffness_matrix'])

    def update_distributed_table(self):
        """Обновить таблицу распределенных параметров"""
        if not hasattr(self, 'calculator') or not self.calculation_results:
            return

        try:
            # Получаем выбранный стержень и шаг дискретизации
            bar_number = self.bar_selector.currentData()
            step = self.step_selector.value()

            # Расчет распределенных параметров
            distributed_data = self.calculator.calculate_distributed_parameters(bar_number, step)

            # Формируем данные для таблицы
            table_data = []
            for point in distributed_data:
                table_data.append([
                    f"{self.smart_round(point['x'])}",
                    f"{self.smart_round(point['displacement'])}",
                    f"{self.smart_round(point['Nx'])}",
                    f"{self.smart_round(point['stress'])}"
                ])

            self.distributed_table.set_data(table_data)

        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при расчете распределенных параметров: {str(e)}")

    def calculate_point_parameters(self):
        """Расчет параметров в конкретной точке"""
        if not hasattr(self, 'calculator') or not self.calculation_results:
            self.displacement_result.setText("—")
            self.force_result.setText("—")
            self.stress_result.setText("—")
            return

        try:
            bar_number = self.point_bar_selector.currentData()
            x_coord = self.x_coordinate_input.value()

            bars_data = self.current_data["Objects"][0]["list_of_values"]
            bar = next((b for b in bars_data if b['barNumber'] == bar_number), None)

            if not bar:
                return

            # Проверяем границы
            if x_coord > bar['length']:
                x_coord = bar['length']
                self.x_coordinate_input.setValue(x_coord)

            # РАСЧЕТ В ТОЧНОЙ КООРДИНАТЕ, а не поиск ближайшей
            L = bar["length"]
            A = bar["cross_section"]
            E = bar["modulus_of_elasticity"]

            displacements = np.array(self.calculation_results['nodal_displacements'])
            u_i = displacements[bar_number - 1]
            u_j = displacements[bar_number]

            # Находим распределенную нагрузку
            q = 0
            distributed_loads = self.current_data["Objects"][2]["list_of_values"]
            for dist_load in distributed_loads:
                if dist_load["bar_number"] == bar_number:
                    q = dist_load["distributed_value"]
                    break

            # Правильная формула перемещения
            xi = x_coord / L
            u_linear = u_i + (u_j - u_i) * xi
            if E * A != 0:
                u_distributed = (q * L ** 2) / (2 * E * A) * xi * (1 - xi)
            else:
                u_distributed = 0
            u_x = u_linear + u_distributed

            # Продольная сила
            Nx = (E * A / L) * (u_j - u_i) + q * (L / 2 - x_coord)

            # Напряжение
            sigma = Nx / A if A != 0 else 0

            # Используем smart_round для форматирования, но передаем ЧИСЛА
            self.displacement_result.setText(f"{self.smart_round(u_x)}")
            self.force_result.setText(f"{self.smart_round(Nx)}")
            self.stress_result.setText(f"{self.smart_round(sigma)}")

        except Exception as e:
            print(f"Ошибка в calculate_point_parameters: {e}")  # Для отладки
            self.displacement_result.setText("Ошибка")
            self.force_result.setText("Ошибка")
            self.stress_result.setText("Ошибка")

    def save_results(self):
        """Сохранить результаты в файл"""
        if not self.calculation_results or not self.main_window.file_path:
            QMessageBox.warning(self, "Ошибка", "Нет результатов для сохранения или файл не выбран")
            return

        try:
            # Загружаем текущие данные из файла
            with open(self.main_window.file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            # Создаем копию результатов без лишних полей
            filtered_results = {
                'stiffness_matrix': self.calculation_results.get('stiffness_matrix', []),
                'nodal_displacements': self.calculation_results.get('nodal_displacements', [])
            }
            # УБИРАЕМ bar_forces, bar_stresses, reactions

            # Добавляем отфильтрованные результаты расчетов
            data["CalculationResults"] = filtered_results

            # Сохраняем обратно
            with open(self.main_window.file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            QMessageBox.information(self, "Успех", "Результаты сохранены в файл проекта")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {str(e)}")

    def smart_round(self, number, precision=6):
        """
        Округляет число до указанной точности и убирает лишние нули
        """
        rounded = round(number, precision)

        # Преобразуем в строку для обработки
        str_rounded = str(rounded)

        # Если есть дробная часть
        if '.' in str_rounded:
            # Убираем нули в конце и точку, если после нее ничего не осталось
            str_rounded = str_rounded.rstrip('0').rstrip('.')

        return str_rounded