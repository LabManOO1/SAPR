import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import tempfile
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QTimer
import numpy as np


class ReportGenerator:
    def __init__(self, main_window):
        self.main_window = main_window
        self._register_fonts()

    def _register_fonts(self):
        """Регистрация шрифтов с поддержкой кириллицы"""
        try:
            # Попробуем использовать DejaVu Sans если установлен
            try:
                # DejaVu Sans обычно устанавливается с ReportLab
                dejavu_paths = [
                    "C:/Windows/Fonts/DejaVuSans.ttf",
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "/Library/Fonts/DejaVuSans.ttf"
                ]

                for font_path in dejavu_paths:
                    if os.path.exists(font_path):
                        pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
                        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', font_path))
                        print(f"Зарегистрирован шрифт DejaVuSans: {font_path}")
                        return
            except:
                pass

            # Если DejaVu не найден, ищем Arial
            font_paths = [
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/arialbd.ttf",  # Arial Bold
                "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
                "/Library/Fonts/Arial.ttf"
            ]

            for font_path in font_paths:
                if os.path.exists(font_path):
                    if 'bd' in font_path.lower():
                        pdfmetrics.registerFont(TTFont('Arial-Bold', font_path))
                    else:
                        pdfmetrics.registerFont(TTFont('Arial', font_path))
                    print(f"Зарегистрирован шрифт: {font_path}")

            # Регистрируем семейство шрифтов
            if 'Arial' in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Arial-Bold')

        except Exception as e:
            print(f"Ошибка регистрации шрифтов: {e}")

    def _get_russian_style(self, styles, style_name, base_style='Normal', **kwargs):
        """Создать стиль с поддержкой русского языка"""
        # Пробуем разные шрифты в порядке приоритета
        font_names = ['DejaVuSans', 'Arial', 'Helvetica']
        font_name = 'Helvetica'

        for test_font in font_names:
            if test_font in pdfmetrics.getRegisteredFontNames():
                font_name = test_font
                break

        print(f"Используется шрифт: {font_name} для стиля {style_name}")

        style = ParagraphStyle(
            f'Russian{style_name}',
            parent=styles[base_style],
            fontName=font_name,
            **kwargs
        )
        return style

    def generate_report(self):
        """Сформировать PDF отчет"""
        try:
            if not self.main_window.file_path:
                QMessageBox.warning(self.main_window, "Ошибка", "Сначала сохраните проект")
                return False

            # Создаем имя файла для отчета
            base_name = os.path.splitext(self.main_window.file_path)[0]
            report_filename = f"{base_name}_report.pdf"

            # Создаем PDF документ
            doc = SimpleDocTemplate(
                report_filename,
                pagesize=A4,
                topMargin=20 * mm,
                bottomMargin=20 * mm,
                leftMargin=15 * mm,
                rightMargin=15 * mm
            )

            elements = []
            styles = getSampleStyleSheet()

            # Создаем стили с русскими шрифтами
            title_style = self._get_russian_style(
                styles, 'Title', 'Heading1',
                fontSize=16,
                spaceAfter=30,
                alignment=1  # Center
            )

            heading2_style = self._get_russian_style(
                styles, 'Heading2', 'Heading2',
                fontSize=14,
                spaceAfter=12,
                spaceBefore=12
            )

            heading3_style = self._get_russian_style(
                styles, 'Heading3', 'Heading3',
                fontSize=12,
                spaceAfter=6,
                spaceBefore=6
            )

            normal_style = self._get_russian_style(
                styles, 'Normal', 'Normal',
                fontSize=10,
                spaceAfter=6
            )

            # Заголовок отчета
            title = Paragraph("ОТЧЕТ ПО РАСЧЕТУ СТЕРЖНЕВОЙ СИСТЕМЫ", title_style)
            elements.append(title)

            # Информация о проекте
            project_info = [
                f"Проект: {os.path.basename(self.main_window.file_path)}",
                f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
            ]

            for info in project_info:
                elements.append(Paragraph(info, normal_style))
                elements.append(Spacer(1, 5))

            elements.append(Spacer(1, 15))

            # 1. ТАБЛИЦА КОНСТРУКЦИИ И СИЛ
            elements.append(Paragraph("1. ИСХОДНЫЕ ДАННЫЕ КОНСТРУКЦИИ", heading2_style))
            elements.append(Spacer(1, 10))

            # Таблица стержней
            if hasattr(self.main_window.preprocessor_tab, 'current_data'):
                data = self.main_window.preprocessor_tab.current_data

                # Таблица стержней
                bars_table_data = self._create_bars_table_data(data)
                if bars_table_data:
                    bars_table = Table(bars_table_data, colWidths=[20 * mm, 25 * mm, 25 * mm, 30 * mm, 25 * mm])
                    bars_table.setStyle(self._get_table_style())
                    elements.append(Paragraph("Таблица стержней:", heading3_style))
                    elements.append(Spacer(1, 5))
                    elements.append(bars_table)
                    elements.append(Spacer(1, 15))

                # Таблица нагрузок
                loads_table_data = self._create_loads_table_data(data)
                if loads_table_data:
                    # Уменьшаем ширину колонок для компактности
                    loads_table = Table(loads_table_data, colWidths=[35 * mm, 25 * mm, 30 * mm])
                    loads_table.setStyle(self._get_table_style())
                    elements.append(Paragraph("Таблица нагрузок:", heading3_style))
                    elements.append(Spacer(1, 5))
                    elements.append(loads_table)
                    elements.append(Spacer(1, 15))

            # 2. ИЗОБРАЖЕНИЕ КОНСТРУКЦИИ
            elements.append(Paragraph("2. СХЕМА КОНСТРУКЦИИ", heading2_style))
            elements.append(Spacer(1, 10))

            # Сохраняем изображение конструкции во временный файл
            construction_img_path = self._save_construction_image()
            if construction_img_path and os.path.exists(construction_img_path):
                try:
                    construction_img = Image(construction_img_path, width=150 * mm, height=80 * mm)
                    elements.append(construction_img)
                    elements.append(Spacer(1, 15))
                except Exception as e:
                    print(f"Ошибка загрузки изображения конструкции: {e}")
                    elements.append(Paragraph("Изображение конструкции недоступно", normal_style))

            # 3. РЕЗУЛЬТАТЫ РАСЧЕТОВ
            if hasattr(self.main_window.processor_tab, 'calculation_results'):
                elements.append(Paragraph("3. РЕЗУЛЬТАТЫ РАСЧЕТОВ", heading2_style))
                elements.append(Spacer(1, 10))

                # Таблица перемещений узлов
                displacements_data = self._create_displacements_table_data()
                if displacements_data:
                    displacements_table = Table(displacements_data, colWidths=[30 * mm, 50 * mm])
                    displacements_table.setStyle(self._get_table_style())
                    elements.append(Paragraph("Перемещения узлов:", heading3_style))
                    elements.append(Spacer(1, 5))
                    elements.append(displacements_table)
                    elements.append(Spacer(1, 15))

                # Таблица проверки прочности
                strength_data = self._create_strength_table_data()
                if strength_data:
                    strength_table = Table(strength_data, colWidths=[25 * mm, 35 * mm, 35 * mm, 35 * mm])
                    strength_table.setStyle(self._get_table_style())
                    elements.append(Paragraph("Проверка прочности:", heading3_style))
                    elements.append(Spacer(1, 5))
                    elements.append(strength_table)
                    elements.append(Spacer(1, 15))

            # 4. ЭПЮРЫ (УБРАНЫ ГРАФИКИ)
            elements.append(Paragraph("4. ЭПЮРЫ", heading2_style))
            elements.append(Spacer(1, 10))

            # Сохраняем только эпюры во временные файлы
            epure_images = self._save_epure_images()
            for epure_name, epure_path in epure_images:
                if os.path.exists(epure_path):
                    try:
                        elements.append(Paragraph(f"Эпюра {epure_name}:", heading3_style))
                        epure_img = Image(epure_path, width=150 * mm, height=80 * mm)
                        elements.append(epure_img)
                        elements.append(Spacer(1, 10))
                    except Exception as e:
                        print(f"Ошибка загрузки эпюры {epure_name}: {e}")

            # Формируем PDF
            doc.build(elements)

            # Очищаем временные файлы
            temp_files = [construction_img_path] + [path for _, path in epure_images if path]
            self._cleanup_temp_files(temp_files)

            QMessageBox.information(self.main_window, "Успех",
                                    f"Отчет успешно сформирован:\n{report_filename}")
            return True

        except Exception as e:
            QMessageBox.critical(self.main_window, "Ошибка",
                                 f"Ошибка при формировании отчета: {str(e)}")
            return False

    def _get_table_style(self):
        """Получить стиль таблицы с поддержкой русского шрифта"""
        font_names = ['DejaVuSans', 'Arial', 'Helvetica']
        normal_font = 'Helvetica'
        bold_font = 'Helvetica-Bold'

        for font in font_names:
            if font in pdfmetrics.getRegisteredFontNames():
                normal_font = font
                if f'{font}-Bold' in pdfmetrics.getRegisteredFontNames():
                    bold_font = f'{font}-Bold'
                break

        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(red=(200.0/255), green=(240.0/255), blue=(240.0/255)),),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), bold_font),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), normal_font),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ])

    def _create_bars_table_data(self, data):
        """Создать данные для таблицы стержней"""
        bars = data["Objects"][0]["list_of_values"]
        if not bars:
            return None

        table_data = [["№ стержня", "Длина, L", "Сечение, A", "Модуль упр., E", "Напряжение, σ"]]

        for bar in bars:
            table_data.append([
                str(bar["barNumber"]),
                f"{smart_round(bar['length'])}",
                f"{smart_round(bar['cross_section'])}",
                f"{smart_round(bar['modulus_of_elasticity'])}",
                f"{smart_round(bar['pressure'])}"
            ])

        return table_data

    def _create_loads_table_data(self, data):
        """Создать данные для таблицы нагрузок"""
        concentrated_loads = data["Objects"][1]["list_of_values"]
        distributed_loads = data["Objects"][2]["list_of_values"]

        # Сокращенные заголовки для компактности
        table_data = [["Тип нагрузки", "Элемент", "Значение"]]

        for load in concentrated_loads:
            table_data.append(["Сосредоточенная", f"Узел {load['node_number']}", f"{smart_round(load['force_value'])}"])

        for load in distributed_loads:
            table_data.append(["Распределенная", f"Стержень {load['bar_number']}", f"{smart_round(load['distributed_value'])}"])

        return table_data if len(table_data) > 1 else None

    def _create_displacements_table_data(self):
        """Создать данные для таблицы перемещений"""
        processor = self.main_window.processor_tab
        if not processor.calculation_results:
            return None

        displacements = processor.calculation_results.get('nodal_displacements', [])
        if not displacements:
            return None

        table_data = [["Узел", "Перемещение u(x)"]]

        for i, disp in enumerate(displacements):
            table_data.append([f"Узел {i + 1}", f"{smart_round(disp)}"])

        return table_data

    def _create_strength_table_data(self):
        """Создать данные для таблицы проверки прочности"""
        processor = self.main_window.processor_tab
        if not hasattr(processor, 'strength_table'):
            return None

        # Получаем данные из таблицы прочности
        try:
            table_data = [["Стержень", "Макс. напряжение |σ|", "Допустимое [σ]", "Состояние"]]

            for row in range(processor.strength_table.rowCount()):
                row_data = []
                for col in range(processor.strength_table.columnCount()):
                    item = processor.strength_table.item(row, col)
                    if item:
                        row_data.append(item.text())
                    else:
                        row_data.append("")
                if any(row_data):  # Добавляем только непустые строки
                    table_data.append(row_data)

            return table_data if len(table_data) > 1 else None
        except Exception as e:
            print(f"Ошибка получения данных прочности: {e}")
            return None

    def _save_construction_image(self):
        """Сохранить изображение конструкции во временный файл"""
        try:
            preprocessor = self.main_window.preprocessor_tab
            if hasattr(preprocessor, 'graphics_manager'):
                # Создаем временный файл
                temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                temp_path = temp_file.name
                temp_file.close()

                # Ждем обновления графики
                QTimer.singleShot(200, lambda: None)

                # Сохраняем изображение через grab
                view = preprocessor.graphics_manager.view
                pixmap = view.grab()
                success = pixmap.save(temp_path, "PNG")

                if success and os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                    print(f"Сохранено изображение конструкции: {temp_path} ({os.path.getsize(temp_path)} bytes)")
                    return temp_path
                else:
                    print("Не удалось сохранить изображение конструкции")
                    return None

        except Exception as e:
            print(f"Ошибка сохранения изображения конструкции: {e}")
        return None

    def _save_epure_images(self):
        """Сохранить эпюры во временные файлы"""
        epures = []
        try:
            postprocessor = self.main_window.postprocessor_tab

            # ПРИНУДИТЕЛЬНО ПЕРЕДАЕМ ДАННЫЕ В ЭПЮРЫ
            if hasattr(self.main_window.preprocessor_tab, 'current_data') and hasattr(self.main_window.processor_tab,
                                                                                      'calculation_results'):
                data = self.main_window.preprocessor_tab.current_data
                calculation_results = self.main_window.processor_tab.calculation_results

                if data and calculation_results:
                    # Принудительно устанавливаем данные в эпюры
                    if hasattr(postprocessor, 'epures_tab'):
                        postprocessor.epures_tab.set_data(data, calculation_results)

            if hasattr(postprocessor, 'epures_tab') and hasattr(postprocessor.epures_tab, 'epure_widget'):
                # Сохраняем разные типы эпюр
                epure_types = [
                    ("перемещений", "displacement"),
                    ("продольных сил", "force"),
                    ("напряжений", "stress")
                ]

                for epure_name, epure_type in epure_types:
                    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                    temp_path = temp_file.name
                    temp_file.close()

                    try:
                        # Устанавливаем тип эпюры
                        epure_widget = postprocessor.epures_tab.epure_widget
                        epure_widget.set_epure_type(epure_type)

                        # ПРИНУДИТЕЛЬНО ОБНОВЛЯЕМ ДАННЫЕ
                        if hasattr(self.main_window.preprocessor_tab, 'current_data') and hasattr(
                                self.main_window.processor_tab, 'calculation_results'):
                            data = self.main_window.preprocessor_tab.current_data
                            calculation_results = self.main_window.processor_tab.calculation_results

                            if data and calculation_results:
                                bars_data = data["Objects"][0]["list_of_values"]
                                displacements = calculation_results.get('nodal_displacements', [])

                                if bars_data and displacements:
                                    epure_widget.set_data(bars_data, displacements, calculation_results)

                        # Даем время на отрисовку
                        QTimer.singleShot(300, lambda: None)

                        # Принудительно обновляем виджет
                        epure_widget.update()
                        epure_widget.repaint()

                        # Ждем завершения отрисовки
                        QTimer.singleShot(200, lambda: None)

                        # Сохраняем как изображение
                        pixmap = epure_widget.grab()
                        if not pixmap.isNull():
                            success = pixmap.save(temp_path, "PNG", quality=100)
                            if success and os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                                epures.append((epure_name, temp_path))
                                print(f"Сохранена эпюра {epure_name}: {os.path.getsize(temp_path)} bytes")
                            else:
                                print(f"Не удалось сохранить эпюру {epure_name}")
                        else:
                            print(f"Пустой pixmap для эпюры {epure_name}")

                    except Exception as e:
                        print(f"Ошибка сохранения эпюры {epure_name}: {e}")

        except Exception as e:
            print(f"Общая ошибка сохранения эпюр: {e}")

        return epures

    def _save_graph_images(self):
        """Сохранить графики во временные файлы"""
        # УБРАНО СОХРАНЕНИЕ ГРАФИКОВ КОМПОНЕНТОВ НДС
        return []  # Возвращаем пустой список

    def _cleanup_temp_files(self, file_paths):
        """Очистить временные файлы"""
        for path in file_paths:
            try:
                if path and os.path.exists(path):
                    os.unlink(path)
                    print(f"Удален временный файл: {path}")
            except Exception as e:
                print(f"Ошибка удаления файла {path}: {e}")

def smart_round(number, precision=6):
    """
    Округляет число до указанной точности и убирает лишние нули
    """
    rounded = round(number, precision)

    # Преобразуем в строку для обработки
    str_rounded = str(rounded)
    if len(str_rounded) > precision:
        str_rounded = str_rounded[:precision]

    # Если есть дробная часть
    if '.' in str_rounded:
        # Убираем нули в конце и точку, если после нее ничего не осталось
        str_rounded = str_rounded.rstrip('0').rstrip('.')

    return str_rounded