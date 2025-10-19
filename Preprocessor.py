from PyQt5.QtWidgets import (QPushButton, QLabel,
                             QVBoxLayout, QWidget,
                             QHBoxLayout, QMenu, QAction, QMessageBox)
from PyQt5.QtCore import Qt,  QTimer
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

        # Кнопка для показа/скрытия меню (в тулбаре)
        self.toggle_dock_btn = QPushButton("Показать/скрыть настройки конструкции")
        self.toggle_dock_btn.clicked.connect(self.toggle_dock)

        top_layout.addWidget(self.toggle_dock_btn)

        mainPreProc_layout.addLayout(top_layout)
        mainPreProc_layout.addStretch(1)

        mainPreProc_layout.addLayout(middle_layout)
        mainPreProc_layout.addStretch(1)

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
                                "quantity": "1",
                                "list_of_values": [
                                    {
                                        "barNumber": "1",
                                        "length": "1",
                                        "cross_section": "1",
                                        "modulus_of_elasticity": "1",
                                        "pressure": "1"
                                    }
                                ]
                            },
                            {
                                "Object": "node_loads",
                                "quantity": "0",
                                "list_of_values": []
                            },
                            {
                                "Object": "distributed_loads",
                                "quantity": "0",
                                "list_of_values": []
                            }
                        ],
                        "Left_support": 0,
                        "Right_support": 0
                    }
                    json.dump(basic_project, f, indent=2, ensure_ascii=False)

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

        with open(self.current_path_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        if not self.validation_data(data):
            QMessageBox.critical(self, "Ошибка", f"Данные в файле не корректны!")
            return False

        # Загружаем данные в таблицы
        self.dock_menu.barsTable.setTableData(data)
        self.dock_menu.concentratedLoadsTable.setTableData(data)
        self.dock_menu.distributedLoadTable.setTableData(data)
        if data["Left_support"] == 1:
            self.dock_menu.left_seal_ChBox.setChecked(True)

        if data["Right_support"] == 1:
            self.dock_menu.right_seal_ChBox.setChecked(True)

        # Устанавливаем путь и обновляем интерфейс
        self.main_window.file_path = self.current_path_file
        self.main_window.set_window_title_with_file()

        # Устанавливаем статус "Проект сохранен"
        self.main_window.set_project_saved_status(True)

        # Показываем временное сообщение о загрузке
        self.main_window.handle_open_project()
        QMessageBox.information(self, "Успех", f"Проект открыт")
        self.graphics_manager.draw_construction(data)

        return True

    def validation_data(self, data):
        try:
            if not all(key in data for key in ['Objects', 'Left_support', 'Right_support']):
                return False, "Отсутствуют обязательные поля"

            if len(data['Objects']) != 3:
                return False, "Неверное количество объектов"
            for i in range(3):
                print(i)
                if int(data["Objects"][i]["quantity"]) != len(data["Objects"][i]["list_of_values"]):
                    return False
            if (data['Objects'][0]['quantity'] == '') or (data['Objects'][0]['quantity'] == '0'):
                return False
            for bars in data['Objects'][0]['list_of_values']:
                if bars['barNumber'] == "" or bars['length'] == "" or bars['cross_section'] == "" or bars['modulus_of_elasticity'] == "" or bars['pressure'] == "":
                    return False
            for node_loads in data['Objects'][1]['list_of_values']:
                if node_loads['node_number'] == "" or node_loads['force_value'] == "":
                    return False
            for distributed_loads in data['Objects'][2]['list_of_values']:
                if distributed_loads['bar_number'] == "" or distributed_loads['distributed_value'] == "":
                    return False
            for distributed_loads_values in data["Objects"][2]["list_of_values"]:
                if (int(distributed_loads_values["bar_number"]) > data["Objects"][0]["quantity"]) or (int(distributed_loads_values["bar_number"]) <=0):
                    return False
            for distributed_loads_values in data["Objects"][1]["list_of_values"]:
                if (int(distributed_loads_values["node_number"]) > data["Objects"][0]["quantity"]+1) or (int(distributed_loads_values["node_number"]) <= 0):
                    return False
            if int(data['Objects'][0]['quantity']) <= 0 or int(data['Objects'][1]['quantity']) < 0 or int(data['Objects'][2]['quantity']) < 0:
                return False
            if data['Left_support'] not in [0, 1] or data['Right_support'] not in [0, 1]:
                return False
            for bars in data['Objects'][0]['list_of_values']:
                if int(bars['length']) <= 0 or int(bars['cross_section']) <= 0 or int(bars['modulus_of_elasticity']) <= 0 or int(bars['pressure']) <= 0:
                    return False

        except KeyError:
            return False
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"{e}")
            return False
        return True

    def save_project(self):
        """Сохранить проект"""
        # Проверяем, есть ли путь к файлу
        if not self.main_window.file_path:
            QMessageBox.warning(self, "Ошибка", "Сначала создайте или откройте проект")
            return

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

            if not self.validation_data(data):
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
        else:
            QMessageBox.warning(self, "Ошибка", "Не все данные заполнены корректно!")

    def close_application(self):
        reply = QMessageBox.question(self, "Выход",
                                     "Вы уверены, что хотите выйти?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.main_window.close()