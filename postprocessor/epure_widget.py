import numpy as np
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QPolygonF, QBrush


class EpureWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bars_data = []
        self.displacements = []
        self.current_epure_type = "displacement"  # displacement, force, stress
        self.setMinimumSize(800, 600)

    def set_data(self, bars_data, displacements, calculation_results=None):
        """Установить данные для построения эпюр"""
        self.bars_data = bars_data
        self.displacements = displacements
        self.calculation_results = calculation_results or {}
        self.update()

    def set_epure_type(self, epure_type):
        """Установить тип эпюры: displacement, force, stress"""
        self.current_epure_type = epure_type
        self.update()

    def paintEvent(self, event):
        """Отрисовка виджета"""
        if not self.bars_data:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()

        # Вся высота под эпюру
        self.draw_epure(painter, width, height)

    def calculate_auto_scale(self, all_values):
        """Автоматически вычисляет масштаб для оптимального отображения"""
        if not all_values:
            return 1.0

        try:
            # Находим максимальное абсолютное значение по всем стержням
            max_abs_value = max(max(abs(v) for v in values) for values in all_values if values)

            if max_abs_value == 0:
                return 1.0

            # Вычисляем доступную высоту для эпюры (80% от общей высоты)
            available_height = self.height() * 0.8

            # Масштаб вычисляем так, чтобы максимальное значение занимало 40% доступной высоты
            # Это дает запас для отображения и не позволяет эпюре вылезать за экран
            scale = (available_height * 0.4) / max_abs_value

            return scale
        except:
            return 1.0

    def draw_epure(self, painter, width, height):
        """Рисует эпюру"""
        if not self.bars_data:
            return

        margin = 50
        available_width = width - 2 * margin

        num_bars = len(self.bars_data)
        bar_width = available_width / num_bars if num_bars > 0 else available_width

        # Положение эпюры
        epure_top = 80  # Отступ сверху для названия эпюры
        epure_bottom = height - 40
        zero_line_y = (epure_top + epure_bottom) / 2

        x_start = margin

        # Собираем все значения для автоматического масштабирования
        all_values = []
        for bar in self.bars_data:
            x_coords, values = self.calculate_epure_data(bar)
            if values:
                all_values.append(values)

        # Автоматически вычисляем масштаб
        auto_scale = self.calculate_auto_scale(all_values)

        # Нулевая линия
        painter.setPen(QPen(QColor(100, 100, 100), 1, Qt.DashLine))
        painter.drawLine(margin, int(zero_line_y), width - margin, int(zero_line_y))

        # Подпись типа эпюры (центрируем вверху)
        epure_names = {
            "displacement": "Эпюра перемещений u(x)",
            "force": "Эпюра продольных сил N(x)",
            "stress": "Эпюра напряжений σ(x)"
        }

        painter.setPen(QColor(0, 0, 0))
        painter.setFont(QFont("Arial", 14, QFont.Bold))
        title = epure_names.get(self.current_epure_type, "")
        title_width = painter.fontMetrics().horizontalAdvance(title)
        title_x = (width - title_width) / 2
        painter.drawText(int(title_x), 40, title)

        # Собираем все ключевые точки для устранения дублирования
        all_key_points = {}

        # Рисуем эпюру для каждого стержня
        for bar_index, bar in enumerate(self.bars_data):
            # Используем фиксированную ширину для каждого стержня
            x_end = x_start + bar_width

            # Подпись номера стержня (всегда черным цветом)
            painter.setPen(QColor(0, 0, 0))
            painter.setFont(QFont("Arial", 10, QFont.Bold))
            mid_x = (x_start + x_end) / 2
            painter.drawText(int(mid_x - 20), int(epure_top - 10), f"Стержень {bar['barNumber']}")

            # Вертикальная линия-разделитель в начале стержня
            painter.setPen(QPen(QColor(100, 100, 100), 1, Qt.DashLine))
            painter.drawLine(int(x_start), int(epure_top), int(x_start), int(epure_bottom))

            # Получаем данные для эпюры
            x_coords, values = self.calculate_epure_data(bar)

            if x_coords and values:
                # Масштабируем координаты с фиксированной шириной
                # Нормализуем координаты x от 0 до 1, затем масштабируем к фиксированной ширине
                if bar['length'] > 0:
                    normalized_x = [x / bar['length'] for x in x_coords]
                else:
                    normalized_x = x_coords
                scaled_x = [x_start + x * bar_width for x in normalized_x]
                scaled_values = [zero_line_y - v * auto_scale for v in values]

                # Рисуем линию эпюры
                color = self.get_epure_color(self.current_epure_type)
                painter.setPen(QPen(color, 3))

                for i in range(len(scaled_x) - 1):
                    painter.drawLine(
                        int(scaled_x[i]), int(scaled_values[i]),
                        int(scaled_x[i + 1]), int(scaled_values[i + 1])
                    )

                # ЗАПОЛНЕНИЕ ШТРИХОВКОЙ ДЛЯ ВСЕХ ТИПОВ ЭПЮР
                self.draw_hatching(painter, scaled_x, scaled_values, zero_line_y, color, x_start, x_end)

                # ОСОБАЯ ОБРАБОТКА ДЛЯ ЭПЮРЫ ПЕРЕМЕЩЕНИЙ - СОБИРАЕМ КЛЮЧЕВЫЕ ТОЧКИ
                if self.current_epure_type == "displacement":
                    self.collect_displacement_key_points(all_key_points, bar, scaled_x,
                                                         scaled_values, values, x_start, x_end)

                # ПОДПИСИ ЗНАЧЕНИЙ ДЛЯ ВСЕХ ТИПОВ ЭПЮР (только в начале и конце)
                painter.setFont(QFont("Arial", 8))
                for i in [0, len(scaled_x) - 1]:  # Только первая и последняя точки
                    text = f"{abs(values[i]):.3f}"
                    text_width = painter.fontMetrics().horizontalAdvance(text)
                    text_height = painter.fontMetrics().height()

                    # Определяем лучшую позицию для подписи
                    if values[i] >= 0:
                        # Для положительных значений - над линией
                        text_x = scaled_x[i] + 5
                        text_y = scaled_values[i] - text_height - 5
                    else:
                        # Для отрицательных значений - под линией
                        text_x = scaled_x[i] + 5
                        text_y = scaled_values[i] + text_height + 10

                    # Фон для лучшей читаемости
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(QColor(255, 255, 255, 230))
                    painter.drawRect(int(text_x) - 3, int(text_y) - text_height + 3,
                                     text_width + 6, text_height)

                    # Текст
                    painter.setPen(QColor(0, 0, 0))
                    painter.drawText(int(text_x), int(text_y), text)

            # Вертикальная линия-разделитель в конце последнего стержня
            if bar['barNumber'] == len(self.bars_data):
                painter.setPen(QPen(QColor(100, 100, 100), 1, Qt.DashLine))
                painter.drawLine(int(x_end), int(epure_top), int(x_end), int(epure_bottom))

            x_start = x_end

        # Рисуем все ключевые точки БЕЗ ДУБЛИРОВАНИЯ (только для перемещений)
        if self.current_epure_type == "displacement":
            self.draw_all_key_points(painter, all_key_points)

    def draw_hatching(self, painter, scaled_x, scaled_values, zero_line_y, color, x_start, x_end):
        """Рисует штриховку между линией эпюры и нулевой линией ДЛЯ ВСЕХ ТИПОВ ЭПЮР"""
        # Фиксированное количество линий штриховки для каждого стержня
        num_hatch_lines = 8

        # Настраиваем перо для штриховки (сплошные линии)
        hatch_pen = QPen(color, 1)
        hatch_pen.setStyle(Qt.SolidLine)
        painter.setPen(hatch_pen)

        # Вычисляем шаг между линиями штриховки
        bar_width = x_end - x_start
        hatch_spacing = bar_width / (num_hatch_lines + 1)

        # Рисуем линии штриховки
        for i in range(1, num_hatch_lines + 1):
            x_pos = x_start + i * hatch_spacing

            # Находим соответствующую точку на линии эпюры
            # Ищем ближайшую точку на кривой эпюры
            closest_idx = min(range(len(scaled_x)), key=lambda idx: abs(scaled_x[idx] - x_pos))
            y_epure = scaled_values[closest_idx]

            # Определяем направление штриховки
            if y_epure < zero_line_y:
                # Положительные значения - штриховка вниз к нулевой линии
                painter.drawLine(int(x_pos), int(y_epure), int(x_pos), int(zero_line_y))
            elif y_epure > zero_line_y:
                # Отрицательные значения - штриховка вверх к нулевой линии
                painter.drawLine(int(x_pos), int(y_epure), int(x_pos), int(zero_line_y))

    def collect_displacement_key_points(self, all_key_points, bar, scaled_x,
                                        scaled_values, values, x_start, x_end):
        """Собирает ключевые точки для эпюры перемещений без дублирования"""
        # Находим распределенную нагрузку для определения типа эпюры
        q = 0
        if hasattr(self, 'calculation_results') and 'distributed_loads' in self.calculation_results:
            for load in self.calculation_results['distributed_loads']:
                if load['bar_number'] == bar['barNumber']:
                    q = load['distributed_value']
                    break

        # Точка в начале стержня (только если это первый стержень)
        if bar['barNumber'] == 1:
            key = round(scaled_x[0], 2)  # Используем координату как ключ
            if key not in all_key_points:
                all_key_points[key] = (scaled_x[0], scaled_values[0], values[0])

        # Точка в конце стержня (всегда добавляем - это будет началом следующего)
        key = round(scaled_x[-1], 2)
        if key not in all_key_points:
            all_key_points[key] = (scaled_x[-1], scaled_values[-1], values[-1])

        # Для параболы находим вершину (если есть распределенная нагрузка)
        if q != 0:
            # Находим точку с максимальным/минимальным значением
            max_idx = np.argmax(values) if q > 0 else np.argmin(values)
            min_idx = np.argmin(values) if q > 0 else np.argmax(values)

            # Выбираем экстремум в зависимости от знака нагрузки
            extr_idx = max_idx if abs(values[max_idx]) > abs(values[min_idx]) else min_idx

            key = round(scaled_x[extr_idx], 2)
            if key not in all_key_points:
                all_key_points[key] = (scaled_x[extr_idx], scaled_values[extr_idx], values[extr_idx])

    def draw_all_key_points(self, painter, all_key_points):
        """Рисует все ключевые точки без дублирования"""
        color = self.get_epure_color("displacement")

        # Сортируем точки по координате X для последовательного отображения
        sorted_points = sorted(all_key_points.values(), key=lambda point: point[0])

        # Отслеживаем занятые позиции для избежания наложений
        occupied_positions = []

        for x, y, value in sorted_points:
            # Рисуем точку
            painter.setPen(QPen(QColor(0, 0, 0), 2))
            painter.setBrush(QColor(255, 255, 255))
            painter.drawEllipse(int(x) - 4, int(y) - 4, 8, 8)
            painter.setBrush(Qt.NoBrush)

            # Подпись значения (только число, без знака)
            painter.setFont(QFont("Arial", 9, QFont.Bold))
            text = f"{abs(value):.3f}"  # Убираем знак для всех значений
            text_width = painter.fontMetrics().horizontalAdvance(text)
            text_height = painter.fontMetrics().height()

            # ОПРЕДЕЛЯЕМ ЛУЧШУЮ ПОЗИЦИЮ ДЛЯ ПОДПИСИ
            text_x, text_y = self.find_best_text_position(x, y, value, text_width, text_height, occupied_positions)

            # Запоминаем занятую позицию
            occupied_positions.append((text_x, text_y, text_width, text_height))

            # Фон для подписи
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(255, 255, 255, 230))  # Более непрозрачный фон
            painter.drawRect(int(text_x) - 3, int(text_y) - text_height + 3,
                             text_width + 6, text_height)

            # Текст
            painter.setPen(QColor(0, 0, 0))
            painter.drawText(int(text_x), int(text_y), text)

    def find_best_text_position(self, x, y, value, text_width, text_height, occupied_positions):
        """Находит лучшую позицию для текста чтобы избежать наложений"""
        # Основные варианты позиционирования
        positions = []

        if value >= 0:
            # Для положительных значений пробуем позиции сверху
            positions.extend([
                (x + 8, y - text_height - 8),  # Справа сверху
                (x - text_width - 8, y - text_height - 8),  # Слева сверху
                (x + 8, y + 15),  # Справа снизу (альтернатива)
                (x - text_width - 8, y + 15)  # Слева снизу (альтернатива)
            ])
        else:
            # Для отрицательных значений пробуем позиции снизу
            positions.extend([
                (x + 8, y + 15),  # Справа снизу
                (x - text_width - 8, y + 15),  # Слева снизу
                (x + 8, y - text_height - 8),  # Справа сверху (альтернатива)
                (x - text_width - 8, y - text_height - 8)  # Слева сверху (альтернатива)
            ])

        # Проверяем каждую позицию на конфликты
        for pos_x, pos_y in positions:
            if not self.is_position_occupied(pos_x, pos_y, text_width, text_height, occupied_positions):
                return pos_x, pos_y

        # Если все позиции заняты, используем первую и сдвигаем немного
        return positions[0][0], positions[0][1] + 20

    def is_position_occupied(self, pos_x, pos_y, text_width, text_height, occupied_positions):
        """Проверяет, занята ли позиция другими подписями"""
        new_rect = (pos_x, pos_y, text_width, text_height)

        for occupied in occupied_positions:
            occ_x, occ_y, occ_width, occ_height = occupied

            # Проверяем пересечение прямоугольников
            if not (pos_x + text_width < occ_x or
                    pos_x > occ_x + occ_width or
                    pos_y + text_height < occ_y or
                    pos_y > occ_y + occ_height):
                return True

        return False

    def calculate_epure_data(self, bar):
        """Вычисляет данные для построения эпюры"""
        try:
            L = bar['length']
            bar_number = bar['barNumber']
            A = bar['cross_section']
            E = bar['modulus_of_elasticity']

            if not self.displacements or len(self.displacements) < bar_number + 1:
                return [], []

            u_i = self.displacements[bar_number - 1]
            u_j = self.displacements[bar_number]

            # Находим распределенную нагрузку
            q = 0
            if hasattr(self, 'calculation_results') and 'distributed_loads' in self.calculation_results:
                for load in self.calculation_results['distributed_loads']:
                    if load['bar_number'] == bar_number:
                        q = load['distributed_value']
                        break

            # Для эпюры перемещений используем больше точек для плавной параболы
            if self.current_epure_type == "displacement":
                num_points = 200  # Увеличили для более точного нахождения вершин
            else:
                num_points = max(10, int(L * 10))

            # Используем меньше точек для очень больших длин чтобы избежать переполнения
            if L > 10000:  # Если длина больше 10000
                num_points = min(num_points, 100)  # Ограничиваем до 100 точек

            x_coords = np.linspace(0, L, num_points)
            values = []

            for x in x_coords:
                if self.current_epure_type == "displacement":
                    # Линейная интерполяция между узловых перемещений
                    u_linear = u_i + (u_j - u_i) * (x / L)

                    # Параболическая составляющая от распределенной нагрузки
                    if E * A != 0 and q != 0:
                        # Добавляем проверку на очень большие значения
                        distributed_component = (q * x * (L - x)) / (2 * E * A)
                        # Ограничиваем величину чтобы избежать переполнения
                        if abs(distributed_component) > 1e10:
                            distributed_component = 0
                        u_distributed = distributed_component
                    else:
                        u_distributed = 0

                    total_u = u_linear + u_distributed
                    values.append(total_u)

                elif self.current_epure_type == "force":
                    Nx = (E * A / L) * (u_j - u_i) + q * (L / 2 - x)
                    # Ограничиваем величину
                    if abs(Nx) > 1e10:
                        Nx = 0
                    values.append(Nx)

                elif self.current_epure_type == "stress":
                    Nx = (E * A / L) * (u_j - u_i) + q * (L / 2 - x)
                    # Ограничиваем величину
                    if abs(Nx) > 1e10:
                        Nx = 0
                    sigma = Nx / A if A != 0 else 0
                    values.append(sigma)

            return x_coords.tolist(), values

        except (ValueError, ZeroDivisionError, OverflowError) as e:
            # В случае ошибки возвращаем пустые данные
            print(f"Ошибка при вычислении эпюры для стержня {bar['barNumber']}: {e}")
            return [], []

    def get_epure_color(self, epure_type):
        """Возвращает цвет для разных типов эпюр"""
        colors = {
            "displacement": QColor(0, 100, 0),  # Темно-зеленый
            "force": QColor(200, 0, 0),  # Красный
            "stress": QColor(0, 0, 200)  # Синий
        }
        return colors.get(epure_type, QColor(0, 0, 0))