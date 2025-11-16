import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QTabWidget, QWidget, QMessageBox
from PyQt5.QtGui import QIcon
from preprocessor.Preprocessor import PreprocessorTab
from processor.processor import ProcessorTab
from postprocessor.postprocessor import PostProcessorTab
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_path = None
        self.current_data = None
        self.calculation_results = None  # Добавляем хранение результатов
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f"SAPR")
        self.setGeometry(350, 200, 1280, 720)
        self.setWindowIcon(QIcon("icons/MainIcon.png"))
        self.starus_bar_label = QLabel("")
        self.statusBar().addPermanentWidget(self.starus_bar_label)

        # СОЗДАЕМ ВИДЖЕТ ВКЛАДОК
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)  # Устанавливаем вкладки как центральный виджет

        # СОЗДАЕМ СОДЕРЖИМОЕ ДЛЯ КАЖДОЙ ВКЛАДКИ
        # Вкладка 1 - Препроцессор
        self.preprocessor_tab = PreprocessorTab(self, self.file_path)
        self.tabs.addTab(self.preprocessor_tab, "Препроцессор")

        # Вкладка 2 - Процессор
        self.processor_tab = ProcessorTab(self)
        self.tabs.addTab(self.processor_tab, "Процессор")

        # Вкладка 3 - Постпроцессор
        self.postprocessor_tab = PostProcessorTab(self)
        self.tabs.addTab(self.postprocessor_tab, "Постпроцессор")

        # Подключаем сигнал смены вкладок
        self.tabs.currentChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index):
        """Обновляем данные при переходе на вкладку процессора или постпроцессора"""
        if index == 1:  # Вкладка процессора
            if hasattr(self.preprocessor_tab, 'current_data'):
                self.current_data = self.preprocessor_tab.current_data
                self.processor_tab.set_data(self.current_data)

        elif index == 2:  # Вкладка постпроцессора
            # Передаем данные и результаты расчетов в постпроцессор
            if hasattr(self.processor_tab, 'calculation_results'):
                self.calculation_results = self.processor_tab.calculation_results
                self.postprocessor_tab.set_data(self.current_data, self.calculation_results)
            elif self.current_data:
                # Если расчетов еще не было, передаем только данные
                self.postprocessor_tab.set_data(self.current_data)

    def handle_new_project(self):
        """Обработка создания нового проекта"""
        self.statusBar().showMessage("Новый проект создан", 3000)

    def handle_open_project(self):
        """Обработка открытия существующего проекта"""
        self.statusBar().showMessage("Проект загружен", 3000)

    def set_project_saved_status(self, saved=True):
        """Установить статус сохраненности проекта"""
        if saved:
            self.statusBar().showMessage("Проект сохранен")
        else:
            self.statusBar().showMessage("Проект не сохранен")

    def set_window_title_with_file(self):
        """Установить заголовок окна с именем файла"""
        if self.file_path:
            file_name = os.path.basename(self.file_path)
            self.setWindowTitle(f"SAPR - {file_name}")
        else:
            self.setWindowTitle("SAPR - Новый проект")

    def setup_processor(self):
        pass

    def setup_postprocessor(self):
        pass

    def closeEvent(self, event):
        """Обработка события закрытия окна"""
        reply = QMessageBox.question(
            self,
            'Подтверждение выхода',
            'Вы уверены, что хотите выйти?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            event.accept()  # Закрыть приложение
        else:
            event.ignore()  # Отменить закрытие


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()