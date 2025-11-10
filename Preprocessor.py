from PyQt5.QtWidgets import (QPushButton, QLabel,
                             QVBoxLayout, QWidget,
                             QHBoxLayout, QMenu, QAction, QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt, QTimer

from setConstruction import Dock_cunstraction
from fileManager import FileManager
import os
import json
from startMenu import StartupDialog
from graphics import ConstructionGraphicsManager


class PreprocessorTab(QWidget):  # Наследуем от QWidget
    def __init__(self, main_window, current_path_file):  # Принимаем главное окно как параметр
        super().__init__()
        self.main_window = main_window  # Сохраняем ссылку на главное окно
        self.current_path_file = current_path_file
        self.graphics_manager = ConstructionGraphicsManager()
        self.setupPreprocessor()
        self.current_data = None
        QTimer.singleShot(100, self.show_startup_dialog)

    def setupPreprocessor(self):
        mainPreProc_layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()

        middle_layout = QHBoxLayout()
        graphics_widget = self.create_graphics_widget()
        middle_layout.addWidget(graphics_widget)

        self.FileButton = QPushButton('Файл')
        self.create_file_menu()
        top_layout.addWidget(self.FileButton)
        top_layout.addStretch(1)

        # СОЗДАЕМ ВЫДВИЖНОЕ МЕНЮ
        self.create_dock_menu()
        self.connect_table_signals()

        # Кнопка для показа/скрытия меню (в тулбаре)
        self.toggle_dock_btn = QPushButton("Показать/скрыть настройки конструкции")
        self.toggle_dock_btn.clicked.connect(self.toggle_dock)

        top_layout.addWidget(self.toggle_dock_btn)

        bottom_layout = QHBoxLayout()
        self.draw_grid_checkbox = QCheckBox()
        self.draw_grid_checkbox.stateChanged.connect(self.on_construction_data_changed)
        paint_grid_text = QLabel("Сетка")

        self.loads_checkbox = QCheckBox()
        self.loads_checkbox.setChecked(True)
        self.loads_checkbox.stateChanged.connect(self.on_construction_data_changed)

        loads_text = QLabel("Нагрузки")

        bottom_layout.addWidget(self.draw_grid_checkbox)
        bottom_layout.addWidget(paint_grid_text)
        bottom_layout.addWidget(self.loads_checkbox)
        bottom_layout.addWidget(loads_text)
        bottom_layout.addStretch(1)

        mainPreProc_layout.addLayout(top_layout)
        mainPreProc_layout.addStretch(1)

        mainPreProc_layout.addLayout(middle_layout)
        mainPreProc_layout.addStretch(1)

        mainPreProc_layout.addLayout(bottom_layout)

        mainPreProc_layout.setAlignment(middle_layout, Qt.AlignCenter)

    def create_graphics_widget(self):
        """Создание виджета с графикой конструкции"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        layout.addWidget(self.graphics_manager.view)

        return widget

    def show_startup_dialog(self):
        """Показать стартовое диалоговое окно"""
        dialog = StartupDialog(self)
        # Показываем диалог и ждем результат

        result = dialog.exec_()
        self.file_path = dialog.file_path
        # Обрабатываем результат
        if result not in (1, 2):
            self.close()  # Закрываем приложение

    def create_dock_menu(self):
        """Создаем выдвижное меню и добавляем его в главное окно"""
        self.dock_menu = Dock_cunstraction(self.main_window)  # Создаем для главного окна
        self.main_window.addDockWidget(Qt.RightDockWidgetArea, self.dock_menu)  # Добавляем в главное окно

    def toggle_dock(self):
        """Показываем/скрываем выдвижное меню"""
        self.dock_menu.setVisible(not self.dock_menu.isVisible())

    def create_file_menu(self):
        """Создает всплывающее меню для кнопки Файл"""
        # Создаем меню и привязываем его к кнопке
        file_menu = QMenu(self)

        # Действие "Новый проект"
        new_action = QAction("Новый проект", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_project)

        # Действие "Открыть проект"
        open_action = QAction("Открыть проект...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_project)

        # Действие "Сохранить"
        save_action = QAction("Сохранить", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_project)

        # Разделитель
        file_menu.addSeparator()

        # Разделитель
        file_menu.addSeparator()

        # Действие "Выход"
        exit_action = QAction("Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close_application)

        # Добавляем все действия в меню
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)

        file_menu.addAction(exit_action)

        # Привязываем меню к кнопке
        self.FileButton.setMenu(file_menu)

    def new_project(self):
        # Получаем путь для сохранения файла
        file_manager = FileManager(self)
        self.current_path_file = file_manager.create_new_project()

        if self.current_path_file:  # Если пользователь выбрал путь (не нажал Cancel)
            # Создаем файл
            try:
                with open(self.current_path_file, 'w', encoding='utf-8') as f:
                    # Записываем базовую структуру проекта
                    basic_project = {
                        "Objects": [
                            {
                                "Object": "bar",
                                "quantity": 1,
                                "list_of_values": [
                                    {
                                        "barNumber": 1,
                                        "length": 1.0,
                                        "cross_section": 1.0,
                                        "modulus_of_elasticity": 1.0,
                                        "pressure": 1.0
                                    }
                                ]
                            },
                            {
                                "Object": "node_loads",
                                "quantity": 0,
                                "list_of_values": []
                            },
                            {
                                "Object": "distributed_loads",
                                "quantity": 0,
                                "list_of_values": []
                            }
                        ],
                        "Left_support": 0,
                        "Right_support": 0
                    }
                    json.dump(basic_project, f, indent=2, ensure_ascii=False)

                self.current_data = basic_project
                print(self.current_data)

                # Устанавливаем путь в главном окне
                self.main_window.file_path = self.current_path_file
                self.main_window.set_window_title_with_file()
                self.main_window.handle_new_project()

                # ★★★ ОЧИЩАЕМ ТАБЛИЦЫ ДЛЯ НОВОГО ПРОЕКТА ★★★
                self.dock_menu.barsTable.setRowCount(1)
                self.dock_menu.concentratedLoadsTable.setRowCount(0)
                self.dock_menu.distributedLoadTable.setRowCount(0)
                self.dock_menu.barsTable.setTableData(basic_project)

                # Очищаем заделки
                self.dock_menu.left_seal_ChBox.setChecked(False)
                self.dock_menu.right_seal_ChBox.setChecked(False)
                QMessageBox.information(self, "Успех", f"Проект создан")
                normalized_data = self._normalize_data_types(basic_project)
                self.graphics_manager.draw_construction(normalized_data)

                return True

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось создать файл: {str(e)}")
                return False
        else:
            # Пользователь нажал Cancel
            return False

    def open_project(self):
        file_manager = FileManager(self)
        self.current_path_file = file_manager.open_existing_project()
        if self.current_path_file is None:
            return False

        try:
            with open(self.current_path_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка чтения файла: {e}")
            return False

        # Нормализуем данные перед валидацией (преобразуем строки в числа)
        normalized_data = self._normalize_data_types(data)

        if not self.validation_data(normalized_data):
            QMessageBox.critical(self, "Ошибка", "Данные в файле не корректны!")
            return False

        # Загружаем данные в таблицы используя нормализованные данные
        self.dock_menu.barsTable.setTableData(normalized_data)
        self.dock_menu.concentratedLoadsTable.setTableData(normalized_data)
        self.dock_menu.distributedLoadTable.setTableData(normalized_data)

        if normalized_data["Left_support"] == 1:
            self.dock_menu.left_seal_ChBox.setChecked(True)
        else:
            self.dock_menu.left_seal_ChBox.setChecked(False)

        if normalized_data["Right_support"] == 1:
            self.dock_menu.right_seal_ChBox.setChecked(True)
        else:
            self.dock_menu.right_seal_ChBox.setChecked(False)

        self.current_data = normalized_data
        print("Загруженные данные:", self.current_data)

        # Устанавливаем путь и обновляем интерфейс
        self.main_window.file_path = self.current_path_file
        self.main_window.set_window_title_with_file()

        # Устанавливаем статус "Проект сохранен"
        self.main_window.set_project_saved_status(True)

        # Показываем временное сообщение о загрузке
        self.main_window.handle_open_project()
        QMessageBox.information(self, "Успех", f"Проект открыт")
        self.graphics_manager.draw_construction(normalized_data)

        return True

    def _normalize_data_types(self, data):
        """
        Нормализует типы данных в JSON, преобразуя строки в числа где это необходимо
        """
        try:
            normalized = json.loads(json.dumps(data))  # Создаем глубокую копию

            # Нормализуем заделки
            normalized["Left_support"] = self._safe_convert_to_int(data["Left_support"])
            normalized["Right_support"] = self._safe_convert_to_int(data["Right_support"])

            # Нормализуем quantity для всех объектов
            for i in range(3):
                normalized["Objects"][i]["quantity"] = self._safe_convert_to_int(data["Objects"][i]["quantity"])

            # Нормализуем стержни
            for bar in normalized["Objects"][0]["list_of_values"]:
                bar["barNumber"] = self._safe_convert_to_int(bar["barNumber"])
                bar["length"] = self._safe_convert_to_float(bar["length"])
                bar["cross_section"] = self._safe_convert_to_float(bar["cross_section"])
                bar["modulus_of_elasticity"] = self._safe_convert_to_float(bar["modulus_of_elasticity"])
                bar["pressure"] = self._safe_convert_to_float(bar["pressure"])

            # Нормализуем сосредоточенные нагрузки
            for node_load in normalized["Objects"][1]["list_of_values"]:
                node_load["node_number"] = self._safe_convert_to_int(node_load["node_number"])
                node_load["force_value"] = self._safe_convert_to_float(node_load["force_value"])

            # Нормализуем распределенные нагрузки
            for distributed_load in normalized["Objects"][2]["list_of_values"]:
                distributed_load["bar_number"] = self._safe_convert_to_int(distributed_load["bar_number"])
                distributed_load["distributed_value"] = self._safe_convert_to_float(
                    distributed_load["distributed_value"])

            return normalized

        except Exception as e:
            print(f"Ошибка нормализации данных: {e}")
            return data  # Возвращаем оригинальные данные в случае ошибки

    def validation_data(self, data):
        """
        Валидация данных проекта с проверкой типов и структуры
        """
        self.main_window.starus_bar_label.setText("")
        try:
            # 1. Проверка наличия основных ключей
            required_root_keys = ['Objects', 'Left_support', 'Right_support']
            if not all(key in data for key in required_root_keys):
                return False

            # 2. Проверка типа основных полей
            if not isinstance(data['Objects'], list):
                return False

            # 3. Проверка количества объектов
            if len(data['Objects']) != 3:
                return False

            # 4. Проверка структуры каждого объекта
            required_object_keys = ['Object', 'quantity', 'list_of_values']
            for i in range(3):
                obj = data["Objects"][i]

                # Проверка наличия ключей
                if not all(key in obj for key in required_object_keys):
                    return False

                # Проверка типов
                if not isinstance(obj['Object'], str):
                    return False
                if not isinstance(obj['list_of_values'], list):
                    return False

                # Безопасное преобразование quantity
                quantity = self._safe_convert_to_int(obj['quantity'])
                if quantity is None or quantity < 0:
                    return False

                # Проверка соответствия quantity и длины list_of_values
                if quantity != len(obj['list_of_values']):
                    return False

            # 5. Проверка специфичных типов объектов
            if data["Objects"][0]['Object'] != 'bar':
                return False
            if data["Objects"][1]['Object'] != 'node_loads':
                return False
            if data["Objects"][2]['Object'] != 'distributed_loads':
                return False

            # 6. Проверка заделок
            left_support = self._safe_convert_to_int(data["Left_support"])
            right_support = self._safe_convert_to_int(data["Right_support"])

            if left_support is None or right_support is None:
                return False

            if left_support not in [0, 1] or right_support not in [0, 1]:
                return False

            # 7. Проверка стержней
            bars_quantity = self._safe_convert_to_int(data['Objects'][0]['quantity'])
            if bars_quantity is None or bars_quantity <= 0:
                return False

            bar_numbers = []
            for bar in data['Objects'][0]['list_of_values']:
                # Проверка наличия ключей
                required_bar_keys = ['barNumber', 'length', 'cross_section', 'modulus_of_elasticity', 'pressure']
                if not all(key in bar for key in required_bar_keys):
                    return False

                # Проверка типов и значений
                bar_number = self._safe_convert_to_int(bar['barNumber'])
                length = self._safe_convert_to_float(bar['length'])
                cross_section = self._safe_convert_to_float(bar['cross_section'])
                modulus_of_elasticity = self._safe_convert_to_float(bar['modulus_of_elasticity'])
                pressure = self._safe_convert_to_float(bar['pressure'])

                if (bar_number is None or length is None or cross_section is None or
                        modulus_of_elasticity is None or pressure is None):
                    return False

                if (bar_number <= 0 or length <= 0 or cross_section <= 0 or
                        modulus_of_elasticity <= 0 or pressure <= 0):
                    return False

                bar_numbers.append(bar_number)

            # 8. Проверка сосредоточенных нагрузок
            node_loads_quantity = self._safe_convert_to_int(data['Objects'][1]['quantity'])
            if node_loads_quantity is None or node_loads_quantity < 0:
                return False

            node_numbers = []
            for node_load in data['Objects'][1]['list_of_values']:
                # Проверка наличия ключей
                required_node_keys = ['node_number', 'force_value']
                if not all(key in node_load for key in required_node_keys):
                    return False

                # Проверка типов и значений
                node_number = self._safe_convert_to_int(node_load['node_number'])
                force_value = self._safe_convert_to_float(node_load['force_value'])

                if node_number is None or force_value is None:
                    return False

                if node_number <= 0:
                    return False

                # Проверка существования узла
                total_nodes = bars_quantity + 1
                if node_number > total_nodes:
                    self.main_window.starus_bar_label.setText("Есть сосредоточенная нагрузка на несуществующий узел!")
                    return False

                node_numbers.append(node_number)

            # 9. Проверка распределенных нагрузок
            distributed_loads_quantity = self._safe_convert_to_int(data['Objects'][2]['quantity'])
            if distributed_loads_quantity is None or distributed_loads_quantity < 0:
                return False

            distributed_bar_numbers = []
            for distributed_load in data['Objects'][2]['list_of_values']:
                # Проверка наличия ключей
                required_distributed_keys = ['bar_number', 'distributed_value']
                if not all(key in distributed_load for key in required_distributed_keys):
                    return False

                # Проверка типов и значений
                bar_number = self._safe_convert_to_int(distributed_load['bar_number'])
                distributed_value = self._safe_convert_to_float(distributed_load['distributed_value'])

                if bar_number is None or distributed_value is None:
                    return False

                if bar_number <= 0:
                    return False

                # Проверка существования стержня
                if bar_number > bars_quantity:
                    self.main_window.starus_bar_label.setText("Есть распределенная нагрузка на несуществующий стержень!")
                    return False

                distributed_bar_numbers.append(bar_number)

            # 10. Проверка уникальности номеров стержней
            if len(bar_numbers) != len(set(bar_numbers)):
                return False

            # 11. Проверка корректной нумерации стержней (1, 2, 3...)
            if sorted(bar_numbers) != list(range(1, bars_quantity + 1)):
                return False

            # 12. Проверка уникальности узлов для сосредоточенных нагрузок
            if len(node_numbers) != len(set(node_numbers)):
                return False

            # 13. Проверка уникальности стержней для распределенных нагрузок
            if len(distributed_bar_numbers) != len(set(distributed_bar_numbers)):
                return False

        except (KeyError, ValueError, TypeError, IndexError) as e:
            print(f"Ошибка валидации: {e}")
            return False

        return True

    def _safe_convert_to_int(self, value):
        """
        Безопасное преобразование к целому числу
        """
        try:
            if value is None:
                return None

            if isinstance(value, (int, float)):
                return int(value)
            elif isinstance(value, str):
                # Удаляем пробелы и проверяем на пустоту
                cleaned = value.strip()
                if not cleaned:
                    return None
                # Сначала в float, потом в int для случаев "1.0", "2.0"
                return int(float(cleaned))
            else:
                return None
        except (ValueError, TypeError):
            return None

    def _safe_convert_to_float(self, value):
        """
        Безопасное преобразование к вещественному числу
        """
        try:
            if value is None:
                return None

            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                # Удаляем пробелы и проверяем на пустоту
                cleaned = value.strip()
                if not cleaned:
                    return None
                # Заменяем запятую на точку для корректного преобразования
                cleaned = cleaned.replace(',', '.')
                return float(cleaned)
            else:
                return None
        except (ValueError, TypeError):
            return None

    def _check_node_loads_conflicts(self, node_forces):
        """
        Проверяет, есть ли на одном узле нагрузки с одинаковым знаком
        Возвращает False если обнаружены конфликты
        """
        for node_number, forces in node_forces.items():
            if len(forces) > 1:
                # Проверяем знаки всех сил на этом узле
                signs = [1 if force > 0 else -1 if force < 0 else 0 for force in forces]

                # Если все ненулевые силы имеют одинаковый знак - это конфликт
                non_zero_signs = [sign for sign in signs if sign != 0]
                if len(non_zero_signs) > 0:
                    first_sign = non_zero_signs[0]
                    if all(sign == first_sign for sign in non_zero_signs):
                        print(
                            f"Обнаружены конфликтующие нагрузки на узле {node_number}: все силы имеют одинаковый знак")
                        return False

                # Дополнительная проверка: если есть силы с разными знаками, это нормально
                # (они могут компенсировать друг друга)

        return True

    def _safe_convert_to_int(self, value):
        """
        Безопасное преобразование к целому числу
        """
        try:
            if value is None:
                return None

            if isinstance(value, (int, float)):
                return int(value)
            elif isinstance(value, str):
                # Удаляем пробелы и проверяем на пустоту
                cleaned = value.strip()
                if not cleaned:
                    return None
                # Сначала в float, потом в int для случаев "1.0", "2.0"
                return int(float(cleaned))
            else:
                return None
        except (ValueError, TypeError):
            return None

    def _safe_convert_to_float(self, value):
        """
        Безопасное преобразование к вещественному числу
        """
        try:
            if value is None:
                return None

            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                # Удаляем пробелы и проверяем на пустоту
                cleaned = value.strip()
                if not cleaned:
                    return None
                # Заменяем запятую на точку для корректного преобразования
                cleaned = cleaned.replace(',', '.')
                return float(cleaned)
            else:
                return None
        except (ValueError, TypeError):
            return None

    def get_data(self):
        data = {}
        Objects = []

        # Получаем данные из таблиц
        bars_data = self.dock_menu.barsTable.getTableData()
        concentrated_data = self.dock_menu.concentratedLoadsTable.getTableData()
        distributed_data = self.dock_menu.distributedLoadTable.getTableData()

        # Проверяем, что все данные заполнены
        if bars_data and concentrated_data and distributed_data:
            Objects.append(bars_data)
            Objects.append(concentrated_data)
            Objects.append(distributed_data)
            data["Objects"] = Objects
            if self.dock_menu.left_seal_ChBox.isChecked():
                data["Left_support"] = 1
            else:
                data["Left_support"] = 0
            if self.dock_menu.right_seal_ChBox.isChecked():
                data["Right_support"] = 1
            else:
                data["Right_support"] = 0
            return data

        else:
            return False

    def save_project(self):
        """Сохранить проект"""
        # Проверяем, есть ли путь к файлу
        if not self.main_window.file_path:
            QMessageBox.warning(self, "Ошибка", "Сначала создайте или откройте проект")
            return

        data = self.get_data()
        if not data:
            QMessageBox.warning(self, "Ошибка", "Не все данные заполнены корректно!")
            return False

        if not self.validation_data(data):
            QMessageBox.warning(self, "Ошибка", "Не все данные заполнены корректно!")
            return False

        print("Данные для сохранения:", data)
        print("Путь файла:", self.main_window.file_path)

        try:
            # Проверка и создание директории
            directory = os.path.dirname(self.main_window.file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

            # Проверка прав доступа
            if directory and not os.access(directory, os.W_OK):
                QMessageBox.critical(self, "Ошибка", f"Нет прав на запись в директорию: {directory}")
                return

            with open(self.main_window.file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            print("Файл успешно сохранен!")
            self.main_window.set_project_saved_status(True)
            QMessageBox.information(self, "Успех", f"Файл сохранен:\n{self.main_window.file_path}")


        except PermissionError:
            QMessageBox.critical(self, "Ошибка",
                                 f"Нет прав доступа к файлу.\n"
                                 f"Возможно файл открыт в другой программе.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения:\n{str(e)}")

    def connect_table_signals(self):
        """Подключение сигналов для отслеживания изменений в таблицах"""
        # Подключаем сигналы изменения данных в таблицах
        self.dock_menu.barsTable.itemChanged.connect(self.on_construction_data_changed)
        self.dock_menu.concentratedLoadsTable.itemChanged.connect(self.on_construction_data_changed)
        self.dock_menu.distributedLoadTable.itemChanged.connect(self.on_construction_data_changed)

        # Подключаем сигналы чекбоксов заделок
        self.dock_menu.left_seal_ChBox.stateChanged.connect(self.on_construction_data_changed)
        self.dock_menu.right_seal_ChBox.stateChanged.connect(self.on_construction_data_changed)


    def on_construction_data_changed(self):
        """Вызывается при изменении данных в таблицах или заделках"""
        try:
            # Получаем актуальные данные из таблиц
            data = self.get_data()

            # Если таблица стержней пустая, очищаем графику и устанавливаем статус "не сохранено"
            if self.dock_menu.barsTable.rowCount() == 0:
                self.graphics_manager.draw_construction(None, False, False)
                self.main_window.set_project_saved_status(False)
                return

            if data and self.validation_data(data):
                # Обновляем текущие данные
                self.current_data = data

                grid = False
                loads = False

                # Обновляем графическое отображение
                if self.draw_grid_checkbox.isChecked():
                    grid = True
                if self.loads_checkbox.isChecked():
                    loads = True

                self.graphics_manager.draw_construction(data, grid, loads)

                # Устанавливаем статус "не сохранено"
                self.main_window.set_project_saved_status(False)
            # else:
            #     self.main_window.starus_bar_label.setText("В таблицах есть пустые значения!")

        except Exception as e:
            print(f"Ошибка при обновлении графики: {e}")

    def remove_bar_with_related_loads(self, bar_number):
        """Удалить стержень и все связанные с ним нагрузки"""
        # Удаляем связанные нагрузки
        self.dock_menu.barsTable.remove_related_loads(
            bar_number,
            self.dock_menu.concentratedLoadsTable,
            self.dock_menu.distributedLoadTable
        )

        # Обновляем графику
        self.on_construction_data_changed()

    def close_application(self):
            self.main_window.close()