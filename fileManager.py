from PyQt5.QtWidgets import (QFileDialog, QMessageBox)
import os


class FileManager(QFileDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.file_path = None

    def create_new_project(self):
        """Обработчик создания нового проекта"""
        # Получаем путь для сохранения файла
        self.file_path, _ = self.getSaveFileName(
            self,
            "Создать новый проект SAPR",
            f"{os.getcwd()}/projects",
            "SAPR Projects (*.json);"
        )

        if self.file_path:  # Если пользователь выбрал путь (не нажал Cancel)
            # Добавляем расширение, если его нет
            if not self.file_path.endswith('.json'):
                self.file_path += '.json'

            # Создаем файл
            try:
                with open(self.file_path, 'x', encoding='utf-8') as f:
                    # Записываем базовую структуру проекта
                    import json
                    basic_project = {
                          "Objects": [
                            {
                              "Object": "bar",
                              "quantity": "1",
                              "list_of_values": [
                              {
                                "barNumber": "",
                                "length": "",
                                "cross_section": "",
                                "modulus_of_elasticity": "",
                                "pressure": ""
                              }
                            ]
                          },
                            {
                              "Object": "node_loads",
                              "quantity": "1",
                              "list_of_values": [
                                {
                                  "node_number": "",
                                  "force_value": ""
                                }
                              ]
                            },
                            {
                              "Object": "distributed_loads",
                              "quantity": "1",
                              "list_of_values": [
                                {
                                  "bar_number": "",
                                  "distributed_value": ""
                                }
                              ]
                            }
                          ]
                        }
                    json.dump(basic_project, f, indent=2)


                self.selected_file_path = self.file_path  # Сохраняем путь
                self.done(1)  # Завершаем с кодом 1 (успех)

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось создать файл: {str(e)}")
                # Не завершаем диалог - пользователь может попробовать снова
        else:
            # Пользователь нажал Cancel - остаемся в диалоге
            pass

    def open_existing_project(self):
        """Обработчик открытия существующего проекта"""
        self.file_path, _ = self.getOpenFileName(
            self,
            "Открыть проект SAPR",
            f"{os.getcwd()}/projects",
            "JSON Files (*.json)"
        )

        if self.file_path:  # Если пользователь выбрал файл
            # Простая проверка существования файла
            if os.path.exists(self.file_path):
                self.selected_file_path = self.file_path
                self.done(2)  # Завершаем ТОЛЬКО если файл выбран и существует
            else:
                QMessageBox.warning(self, "Ошибка", "Файл не существует")