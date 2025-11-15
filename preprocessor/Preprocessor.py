from PyQt5.QtWidgets import (QPushButton, QLabel,
                             QVBoxLayout, QWidget,
                             QHBoxLayout, QMenu, QAction, QMessageBox, QCheckBox, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer

from preprocessor.setConstruction import Dock_cunstraction
from fileManager import FileManager
import os
import json
from startMenu import StartupDialog
from preprocessor.graphics import ConstructionGraphicsManager
from validator import Validator


class PreprocessorTab(QWidget):  # Наследуем от QWidget
    def __init__(self, main_window, current_path_file):  # Принимаем главное окно как параметр
        super().__init__()
        self.main_window = main_window  # Сохраняем ссылку на главное окно
        self.current_path_file = current_path_file
        self.graphics_manager = ConstructionGraphicsManager()
        self.validator = Validator(self.main_window)
        self.setupPreprocessor()
        self.current_data = None
        QTimer.singleShot(100, self.show_startup_dialog)

    def setupPreprocessor(self):
        mainPreProc_layout = QVBoxLayout(self)
        mainPreProc_layout.setContentsMargins(2, 2, 2, 2)  # Минимальные отступы
        mainPreProc_layout.setSpacing(2)

        top_layout = QHBoxLayout()

        middle_layout = QHBoxLayout()
        graphics_widget = self.graphics_manager.view
        graphics_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
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

        self.loads_checkbox = QCheckBox()
        self.loads_checkbox.setChecked(True)
        self.loads_checkbox.stateChanged.connect(self.on_construction_data_changed)

        loads_text = QLabel("Нагрузки")

        bottom_layout.addWidget(self.loads_checkbox)
        bottom_layout.addWidget(loads_text)
        bottom_layout.addStretch(1)

        mainPreProc_layout.addLayout(top_layout)

        mainPreProc_layout.addLayout(middle_layout)

        mainPreProc_layout.addLayout(bottom_layout)

        mainPreProc_layout.setAlignment(middle_layout, Qt.AlignCenter)

    def create_graphics_widget(self):
        """Создание виджета с графикой конструкции"""
        layout = QVBoxLayout()
        layout.addWidget(self.graphics_manager.view)

    def resizeEvent(self, event):
        """Обработка изменения размера всей вкладки"""
        super().resizeEvent(event)
        # Обновляем графику при изменении размера
        if self.current_data:
            QTimer.singleShot(100, lambda: self.graphics_manager.update_construction())

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

        if not self.validator.validation_data(normalized_data):
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

        if not self.validator.validation_data(data):
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
                self.graphics_manager.draw_construction(None, False)
                self.main_window.set_project_saved_status(False)
                return

            if data and self.validator.validation_data(data):
                # Обновляем текущие данные
                self.current_data = data

                loads = False

                # Обновляем графическое отображение
                if self.loads_checkbox.isChecked():
                    loads = True

                self.graphics_manager.draw_construction(data, loads)

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