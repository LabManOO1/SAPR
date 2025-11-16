from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QMessageBox,
                             QTabWidget, QComboBox,
                             QDoubleSpinBox, QFormLayout, QGroupBox, QDialog, QCheckBox, QDialogButtonBox)
from PyQt5.QtCore import Qt
from processor.calculations import BarSystemCalculator
import numpy as np
import csv
import os
from datetime import datetime
from processor.resultsTableWidget import ResultsTable
from processor.strengthTableWidget import StrengthTable
from processor.stiffnessMatrixTableWidget import StiffnessMatrixTable
from report_generator import ReportGenerator
from validator import Validator


class ExportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Экспорт таблиц в CSV")
        self.setModal(True)
        self.resize(400, 300)

        self.selected_tables = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Группа выбора таблиц
        tables_group = QGroupBox("Выберите таблицы для экспорта:")
        tables_layout = QVBoxLayout(tables_group)

        self.checkboxes = {}
        tables = [
            ("displacements", "Перемещения узлов"),
            ("strength", "Проверка прочности"),
            ("distributed", "Распределенные параметры"),
            ("stiffness_matrix", "Матрица жесткости")  # Добавляем матрицу жесткости
        ]

        for table_id, table_name in tables:
            checkbox = QCheckBox(table_name)
            checkbox.setChecked(True)
            self.checkboxes[table_id] = checkbox
            tables_layout.addWidget(checkbox)

        tables_layout.addStretch(1)
        layout.addWidget(tables_group)

        # Кнопки
        button_layout = QHBoxLayout()

        self.select_all_btn = QPushButton("Выбрать все")
        self.select_all_btn.clicked.connect(self.select_all)

        self.deselect_all_btn = QPushButton("Снять все")
        self.deselect_all_btn.clicked.connect(self.deselect_all)

        button_layout.addWidget(self.select_all_btn)
        button_layout.addWidget(self.deselect_all_btn)
        button_layout.addStretch(1)

        layout.addLayout(button_layout)

        # Стандартные кнопки диалога
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def select_all(self):
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(True)

    def deselect_all(self):
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(False)

    def get_selected_tables(self):
        selected = []
        for table_id, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                selected.append(table_id)
        return selected


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

        # Добавляем кнопку экспорта в CSV
        self.export_csv_btn = QPushButton("Экспорт в CSV")
        self.export_csv_btn.setMinimumHeight(35)
        self.export_csv_btn.clicked.connect(self.export_to_csv)
        self.export_csv_btn.setEnabled(False)

        # Кнопка формирования отчета
        self.report_btn = QPushButton("Сформировать отчет (PDF)")
        self.report_btn.setMinimumHeight(35)
        self.report_btn.clicked.connect(self.generate_report)
        self.report_btn.setEnabled(True)
        self.report_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    font-weight: bold;
                    border: none;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)

        # Верхняя панель с кнопками
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.calculate_btn)
        top_layout.addWidget(self.export_csv_btn)
        top_layout.addWidget(self.report_btn)
        top_layout.addStretch(1)

        # Горизонтальный layout для групп настроек
        settings_horizontal_layout = QHBoxLayout()

        # Группа настроек для распределенных параметров (слева)
        settings_group = QGroupBox("Настройки расчета распределенных параметров")
        settings_layout = QFormLayout(settings_group)

        # Выбор стержня
        self.bar_selector = QComboBox()
        self.bar_selector.currentIndexChanged.connect(self.update_distributed_table)
        settings_layout.addRow("Стержень:", self.bar_selector)

        # Шаг дискретизации
        self.step_selector = QDoubleSpinBox()
        self.step_selector.setRange(0.01, 10.0)
        self.step_selector.setValue(0.1)
        self.step_selector.setSingleStep(0.1)
        self.step_selector.setDecimals(2)
        self.step_selector.valueChanged.connect(self.update_distributed_table)
        settings_layout.addRow("Шаг дискретизации:", self.step_selector)

        # Группа для расчета в конкретной точке (справа)
        point_calc_group = QGroupBox("Расчет параметров в конкретной точке")
        point_layout = QFormLayout(point_calc_group)

        # Выбор стержня для точечного расчета
        self.point_bar_selector = QComboBox()
        self.point_bar_selector.currentIndexChanged.connect(self.calculate_point_parameters)
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

        # Таблица проверки прочности (НОВАЯ вкладка)
        self.strength_table = StrengthTable()

        # Матрица жесткости (табличное представление)
        self.matrix_table = StiffnessMatrixTable()

        # Добавляем таблицы во вкладки
        self.results_tabs.addTab(self.distributed_table, "Распределенные параметры")
        self.results_tabs.addTab(self.displacements_table, "Перемещения узлов")
        self.results_tabs.addTab(self.strength_table, "Проверка прочности")  # Новая вкладка
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

    def calculate(self):
        """Выполнить расчеты"""
        validator = Validator(self.main_window)
        if not validator.validation_data(self.current_data):
            QMessageBox.warning(self, "Ошибка", "Некорректные данные для расчета")
            self.status_label.setText("Нет данных для расчета")
            self.calculate_btn.setEnabled(False)
            return
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
                self.export_csv_btn.setEnabled(True)
                self.status_label.setText("Расчет успешно завершен")

                # Автоматически рассчитываем параметры для текущей точки
                self.calculate_point_parameters()

                # ПЕРЕДАЕМ ДАННЫЕ В ПОСТПРОЦЕССОР
                if hasattr(self.main_window, 'post_processor'):
                    self.main_window.post_processor.set_data(self.current_data, self.calculation_results)

                QMessageBox.information(self, "Успех", "Расчет завершен успешно!")
            else:
                QMessageBox.critical(self, "Ошибка", "Ошибка при выполнении расчетов")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка расчета: {str(e)}")
            self.status_label.setText("Ошибка расчета")

    def calculate_max_stresses(self):
        """Расчет максимальных напряжений по длине каждого стержня"""
        bars_data = self.current_data["Objects"][0]["list_of_values"]
        max_stresses = []
        allowable_stresses = []
        strength_conditions = []

        for bar in bars_data:
            bar_number = bar["barNumber"]
            L = bar["length"]
            allowable_stress = bar.get("pressure", 1.0)  # Допустимое напряжение из данных

            # Расчет распределенных параметров с малым шагом для точного определения максимума
            distributed_data = self.calculator.calculate_distributed_parameters(bar_number, L / 100)

            # Находим максимальное по модулю напряжение
            max_stress = max(abs(point['stress']) for point in distributed_data)

            max_stresses.append(max_stress)
            allowable_stresses.append(allowable_stress)
            strength_conditions.append(max_stress <= allowable_stress)

        return max_stresses, allowable_stresses, strength_conditions

    def display_results(self):
        """Отобразить результаты расчетов"""
        if not self.calculation_results:
            return

        # Перемещения узлов
        displacements_data = []
        for i, disp in enumerate(self.calculation_results['nodal_displacements']):
            displacements_data.append([f"{i + 1}", f"{smart_round(disp)}"])
        self.displacements_table.set_data(displacements_data)

        # Автоматическое обновление таблицы распределенных параметров
        self.update_distributed_table()

        # Проверка прочности
        max_stresses, allowable_stresses, strength_conditions = self.calculate_max_stresses()
        bars_data = self.current_data["Objects"][0]["list_of_values"]
        self.strength_table.set_strength_data(bars_data, max_stresses, allowable_stresses, strength_conditions)

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
                    f"{smart_round(point['x'])}",
                    f"{smart_round(point['displacement'])}",
                    f"{smart_round(point['Nx'])}",
                    f"{smart_round(point['stress'])}"
                ])

            self.distributed_table.set_data(table_data)

        except Exception as e:
            # Не показываем сообщение об ошибке при автоматическом обновлении
            # чтобы не мешать пользователю при изменении настроек
            pass

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
            self.displacement_result.setText(f"{smart_round(u_x)}")
            self.force_result.setText(f"{smart_round(Nx)}")
            self.stress_result.setText(f"{smart_round(sigma)}")

        except Exception as e:
            print(f"Ошибка в calculate_point_parameters: {e}")  # Для отладки
            self.displacement_result.setText("Ошибка")
            self.force_result.setText("Ошибка")
            self.stress_result.setText("Ошибка")


    def export_to_csv(self):
        """Экспорт выбранных таблиц в CSV файлы"""
        if not self.calculation_results:
            QMessageBox.warning(self, "Ошибка", "Нет результатов для экспорта")
            return

        # Показываем диалог выбора таблиц
        dialog = ExportDialog(self)
        if dialog.exec_() != QDialog.Accepted:
            return

        selected_tables = dialog.get_selected_tables()
        if not selected_tables:
            QMessageBox.warning(self, "Ошибка", "Не выбрано ни одной таблицы для экспорта")
            return

        try:
            # Получаем базовое имя файла из основного файла проекта
            base_filename = self.get_export_base_filename()

            # Создаем папку для экспорта если нужно
            export_dir = os.path.dirname(base_filename)
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)

            # Экспортируем выбранные таблицы
            exported_files = []

            table_exporters = {
                "displacements": ("Перемещения узлов", self.export_displacements_to_csv),
                "strength": ("Проверка прочности", self.export_strength_to_csv),
                "distributed": ("Распределенные параметры", self.export_distributed_to_csv),
                "stiffness_matrix": ("Матрица жесткости", self.export_stiffness_matrix_to_csv)
                # Добавляем экспорт матрицы
            }

            for table_id in selected_tables:
                if table_id in table_exporters:
                    table_name, exporter_func = table_exporters[table_id]
                    filename = f"{base_filename}_{table_id}.csv"

                    if exporter_func(filename):
                        exported_files.append((table_name, filename))

            if exported_files:
                self.show_export_success_message(exported_files)
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось экспортировать данные")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка экспорта", f"Ошибка при экспорте в CSV: {str(e)}")

    def get_export_base_filename(self):
        """Получить базовое имя файла для экспорта"""
        if hasattr(self.main_window, 'file_path') and self.main_window.file_path:
            # Используем путь основного файла проекта
            base_path = os.path.splitext(self.main_window.file_path)[0]
            return f"{base_path}_results"
        else:
            # Если файл не сохранен, используем папку export_results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"export_results/sapr_export_{timestamp}"

    def show_export_success_message(self, exported_files):
        """Показать сообщение об успешном экспорте"""
        message = f"Успешно экспортировано {len(exported_files)} таблиц:\n\n"
        for table_name, filename in exported_files:
            message += f"• {table_name}\n"

        message += f"\nФайлы сохранены в:\n{os.path.dirname(exported_files[0][1])}"

        # Показываем диалог с возможностью открыть папку
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Экспорт завершен")
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Information)

        open_folder_btn = msg_box.addButton("Открыть папку", QMessageBox.ActionRole)
        msg_box.addButton(QMessageBox.Ok)

        msg_box.exec_()

        if msg_box.clickedButton() == open_folder_btn:
            self.open_export_folder(exported_files[0][1])

    def open_export_folder(self, filepath):
        """Открыть папку с экспортированными файлами"""
        try:
            folder_path = os.path.dirname(filepath)
            if os.name == 'nt':  # Windows
                os.startfile(folder_path)
            elif os.name == 'posix':  # macOS, Linux
                import subprocess
                subprocess.run(['open', folder_path] if os.uname().sysname == 'Darwin' else ['xdg-open', folder_path])
        except Exception as e:
            print(f"Не удалось открыть папку: {e}")

    def export_displacements_to_csv(self, filename):
        """Экспорт перемещений узлов в CSV"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                writer.writerow(['Узел', 'Перемещение u(x)'])

                displacements = self.calculation_results.get('nodal_displacements', [])
                for i, disp in enumerate(displacements):
                    writer.writerow([f'Узел {i + 1}', smart_round(disp)])
            return True
        except Exception as e:
            print(f"Ошибка экспорта перемещений: {e}")
            return False

    def export_strength_to_csv(self, filename):
        """Экспорт проверки прочности в CSV"""
        try:
            max_stresses, allowable_stresses, strength_conditions = self.calculate_max_stresses()
            bars_data = self.current_data["Objects"][0]["list_of_values"]

            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                writer.writerow(['Стержень', 'Макс. напряжение |σ|', 'Допустимое напряжение [σ]', 'Состояние'])

                for i, bar in enumerate(bars_data):
                    if i < len(max_stresses):
                        status = "Прочность обеспечена" if strength_conditions[i] else "ПРЕВЫШЕНИЕ!"
                        writer.writerow([
                            f'Стержень {bar["barNumber"]}',
                            smart_round(max_stresses[i]),
                            smart_round(allowable_stresses[i]),
                            status
                        ])
            return True
        except Exception as e:
            print(f"Ошибка экспорта прочности: {e}")
            return False

    def export_distributed_to_csv(self, filename):
        """Экспорт распределенных параметров для текущего стержня в CSV"""
        try:
            if not hasattr(self, 'calculator'):
                return False

            bar_number = self.bar_selector.currentData()
            step = self.step_selector.value()
            distributed_data = self.calculator.calculate_distributed_parameters(bar_number, step)

            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                writer.writerow(['Координата x', 'Перемещение u(x)', 'Продольная сила Nx', 'Напряжение σ'])

                for point in distributed_data:
                    writer.writerow([
                        smart_round(point['x']),
                        smart_round(point['displacement']),
                        smart_round(point['Nx']),
                        smart_round(point['stress'])
                    ])
            return True
        except Exception as e:
            print(f"Ошибка экспорта распределенных параметров: {e}")
            return False

    def export_stiffness_matrix_to_csv(self, filename):
        """Экспорт матрицы жесткости в CSV"""
        try:
            stiffness_matrix = self.calculation_results.get('stiffness_matrix', [])
            if not stiffness_matrix:
                return False

            n = len(stiffness_matrix)

            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')

                # Записываем заголовки столбцов
                headers = [f"Узел {i + 1}" for i in range(n)]
                writer.writerow([''] + headers)  # Первая ячейка пустая для красоты

                # Записываем данные матрицы
                for i in range(n):
                    row_data = [f"Узел {i + 1}"]  # Заголовок строки
                    for j in range(n):
                        value = stiffness_matrix[i][j]
                        if abs(value) < 1e-10:  # Показываем нули как 0
                            display_value = "0"
                        else:
                            display_value = f"{value:.6e}"
                        row_data.append(display_value)
                    writer.writerow(row_data)

            return True
        except Exception as e:
            print(f"Ошибка экспорта матрицы жесткости: {e}")
            return False

    def generate_report(self):
        """Сформировать PDF отчет"""
        if not self.current_data:
            QMessageBox.warning(self, "Ошибка", "Нет данных для формирования отчета")
            return

        if not hasattr(self, 'calculation_results') or not self.calculation_results:
            QMessageBox.warning(self, "Ошибка", "Сначала выполните расчет")
            return

        # Создаем генератор отчетов
        report_generator = ReportGenerator(self.main_window)
        report_generator.generate_report()

def smart_round(number, precision=6):
    """
    Округляет число до указанной точности и убирает лишние нули
    """
    rounded = round(number, precision)

    # Преобразуем в строку для обработки
    str_rounded = str(rounded)
    if len(str_rounded) > precision+2:
        str_rounded = str_rounded[:precision+2]

    # Если есть дробная часть
    if '.' in str_rounded:
        # Убираем нули в конце и точку, если после нее ничего не осталось
        str_rounded = str_rounded.rstrip('0').rstrip('.')

    return str_rounded