from PyQt5.QtWidgets import (QGraphicsScene, QGraphicsView, QGraphicsLineItem,
                             QGraphicsEllipseItem, QGraphicsTextItem, QToolBar, QAction, QGraphicsRectItem,
                             QGraphicsItemGroup, QGraphicsItem, QGraphicsPixmapItem, QGridLayout)
from PyQt5.QtCore import Qt, QRectF, QTimer
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter, QPixmap, QMouseEvent


class BarGraphicsItem(QGraphicsRectItem):
    def __init__(self, x1, y1, x2, y2, bar_number):
        super().__init__(x1, y1, x2, y2)
        self.bar_number = bar_number
        self.setup_appearance()

    def setup_appearance(self):
        self.setPen(QPen(Qt.black, 4))  # Steel blue


class NodeGraphicsItem(QGraphicsItemGroup):
    def __init__(self, x, y, node_number, is_support=False):
        super().__init__()
        self.node_number = node_number
        self.is_support = is_support

        # Создаем элементы и добавляем в группу
        if len(str(node_number)) == 1:
            self.rect_item = QGraphicsRectItem(-10, -10, 18, 18)
        else:
            self.rect_item = QGraphicsRectItem(-12, -10, 24, 18)
        self.text_item = QGraphicsTextItem(f"{node_number}")
        self.text_item.setScale(1.5)

        self.addToGroup(self.rect_item)
        self.addToGroup(self.text_item)

        # Позиционируем текст
        if len(str(node_number)) > 1:
            self.text_item.setPos(-14, -18)
        else:
            self.text_item.setPos(-11, -18)

        self.setPos(x, y)  # Устанавливаем позицию всей группы
        self.setup_appearance()

    def setup_appearance(self):
        self.rect_item.setPen(QPen(QColor("#245AC7"), 1.5))
        self.rect_item.setBrush(QBrush(QColor(255, 255, 255)))

        self.text_item.setDefaultTextColor(QColor("#245AC7"))


class LengthBarGraphicsItem(QGraphicsItemGroup):
    def __init__(self, x1, x2, y, length):
        super().__init__()
        self.line = QGraphicsLineItem(3, 0, x2 - 3, 0)

        self.length = length
        if str(self.length)[-2:] == ".0":
            self.length = int(str(self.length)[:-2])
        if len(str(self.length)) > 5:
            self.length = "{:.1e}".format(self.length)
        self.text_item = QGraphicsTextItem(str(self.length))
        self.text_item.setScale(1.5)

        self.left_arrow_top = QGraphicsLineItem(2, 0, 10, -4)
        self.left_arrow_bottom = QGraphicsLineItem(2, 0, 10, 4)
        self.right_arrow_top = QGraphicsLineItem(x2 - 2, 0, x2 - 10, -4)
        self.right_arrow_bottom = QGraphicsLineItem(x2 - 2, 0, x2 - 10, 4)

        self.line.setPen(QPen(QColor("#000"), 2))
        self.left_arrow_bottom.setPen(QPen(QColor("#000"), 1.5))
        self.left_arrow_top.setPen(QPen(QColor("#000"), 1.5))
        self.right_arrow_top.setPen(QPen(QColor("#000"), 1.5))
        self.right_arrow_bottom.setPen(QPen(QColor("#000"), 1.5))

        self.addToGroup(self.line)
        self.addToGroup(self.left_arrow_top)
        self.addToGroup(self.left_arrow_bottom)
        self.addToGroup(self.right_arrow_top)
        self.addToGroup(self.right_arrow_bottom)

        if len(str(self.length)) == 1:
            self.addToGroup(self.text_item)
            self.text_item.setPos(x2 / 2 - 12, -30)
        if len(str(self.length)) == 2:
            self.addToGroup(self.text_item)
            self.text_item.setPos(x2 / 2 - 17, -30)
        if len(str(self.length)) == 3:
            self.addToGroup(self.text_item)
            self.text_item.setPos(x2 / 2 - 20, -30)
        if len(str(self.length)) == 4:
            self.addToGroup(self.text_item)
            self.text_item.setPos(x2 / 2 - 25, -30)
        if len(str(self.length)) == 5:
            self.addToGroup(self.text_item)
            self.text_item.setPos(x2 / 2 - 28, -30)
        if len(str(self.length)) > 5:
            self.addToGroup(self.text_item)
            self.text_item.setPos(x2 / 2 - 35, -30)



        self.setPos(x1, y - 2)


class BarNumber(QGraphicsItemGroup):
    def __init__(self, x, y, bar_number):
        super().__init__()
        if len(str(bar_number)) == 1:
            self.circle = QGraphicsEllipseItem(-11, -11, 19, 19)
        else:
            self.circle = QGraphicsEllipseItem(-14, -14, 22, 22)
        self.text_item = QGraphicsTextItem(f"{bar_number}")
        self.text_item.setScale(1.5)
        self.addToGroup(self.circle)
        self.addToGroup(self.text_item)

        if len(str(bar_number)) > 1:
            self.text_item.setPos(-18, -19)
        else:
            self.text_item.setPos(-12, -18)
        self.setPos(x, y)
        self.setup_appearance()

    def setup_appearance(self):
        self.circle.setPen(QPen(QColor("#C05"), 1.5))

        self.text_item.setDefaultTextColor(QColor("#C05"))


class SupportGraphicsItem(QGraphicsItemGroup):
    def __init__(self, x, y, is_left_support=True, height=60):
        super().__init__()

        self.x = x
        self.y = y
        self.height = height
        self.is_left_support = is_left_support
        self.support_width = self.height/10

        self.create_support()
        self.setPos(x, y)

    def create_support(self):
        """Создает графическое представление заделки"""

        # Основная вертикальная полоса (стенка)
        main_line = QGraphicsLineItem(0, -self.height / 2, 0, self.height / 2)
        main_line.setPen(QPen(Qt.black, 4))
        self.addToGroup(main_line)

        # Штрихи (треугольники или линии)
        self.create_hatching()


    def create_hatching(self):
        """Создает штриховку в зависимости от типа заделки"""
        hatch_spacing = self.height // 6
        num_hatches = int(self.height // hatch_spacing)
        y_ = self.height/9


        for i in range(num_hatches):
            y_pos = i * hatch_spacing
            if self.is_left_support:
                # Штрихи справа от основной линии
                hatch = QGraphicsLineItem(-self.support_width, -self.height/2 + y_pos + y_, 0, -self.height/2 + y_pos)
            else:
                # Штрихи слева от основной линии
                hatch = QGraphicsLineItem(0, -self.height/2 + y_pos + y_, self.support_width, -self.height/2 + y_pos)

            hatch.setPen(QPen(Qt.black, 3))
            self.addToGroup(hatch)


class NodeLoad(QGraphicsItemGroup):
    def __init__(self, x, y, force_value):
        super().__init__()
        if str(force_value)[-2:] == ".0":
            force_value = int(str(force_value)[:-2])

        x_main1 = 0
        x_main2 = 30
        x_top1 = 22
        x_top2 = 30
        y_top1 = -5
        y_top2 = 5
        x_text = 0

        if force_value < 0:
            x_main1 = -30
            x_main2 = 0
            x_top1 = -22
            x_top2 = -30
            y_top1 = -5
            y_top2 = 5
            x_text = -25
        value = abs(force_value)
        if len(str(value)) > 6:
            value = "{:.1e}".format(value)

        self.text_item = QGraphicsTextItem(f"{value}")
        self.text_item.setScale(1.5)
        font = self.text_item.font()
        font.setPointSize(6)  # Размер в пунктах
        self.text_item.setFont(font)


        main_lime = QGraphicsLineItem(x_main1, 0, x_main2, 0)
        arrow_top_line = QGraphicsLineItem(x_top1, y_top1, x_top2, 0)
        arrow_bot_line = QGraphicsLineItem(x_top1, y_top2, x_top2, 0)
        main_lime.setPen(QPen(QColor("#C05"), 3))
        arrow_top_line.setPen(QPen(QColor("#C05"), 3))
        arrow_bot_line.setPen(QPen(QColor("#C05"), 3))
        self.addToGroup(main_lime)
        self.addToGroup(arrow_top_line)
        self.addToGroup(arrow_bot_line)
        self.text_item.setDefaultTextColor(QColor("#C05"))
        x_ = 0
        if len(str(value)) < 7:
            if force_value < 0:
                if len(str(value)) == 3:
                    x_ = 4
                if len(str(value)) == 4:
                    x_ = 12
                if len(str(value)) == 5:
                    x_ = 15
                if len(str(value)) == 6:
                    x_ = 21
                if force_value < 0:
                    self.text_item.setPos(x_text - x_, -26)
                self.addToGroup(self.text_item)

            else:
                if len(str(value)) == 3:
                    x_ = 4
                if len(str(value)) > 3:
                    x_ = 6

                self.text_item.setPos(x_text + 5 - x_, -26)
                self.addToGroup(self.text_item)



        self.setPos(x, y)


class DistributedLoad(QGraphicsItemGroup):
    def __init__(self, x1, x2, length, value):
        super().__init__()
        count_arrow = 4
        current_x = 0
        self.length = length
        spacing = 5
        self.value = value
        if str(self.value)[-2:] == ".0":
            self.value = int(str(self.value)[:-2])


        length_arrow = 15
        if self.length < 60:

            spacing = (self.length) / 16
            length_arrow = (self.length - count_arrow * spacing + spacing) / count_arrow
            for i in range(count_arrow):

                main_arrow = QGraphicsLineItem(current_x, 0, current_x + length_arrow, 0)
                main_arrow.setPen(QPen(QColor("#245AC7"), 2))
                if self.value > 0:
                    top_arrow = QGraphicsLineItem(current_x + length_arrow - 4, -3, current_x + length_arrow, 0)
                    top_arrow.setPen(QPen(QColor("#245AC7"), 2))
                    self.addToGroup(top_arrow)
                    bot_arrow = QGraphicsLineItem(current_x + length_arrow - 4, 3, current_x + length_arrow, 0)
                    bot_arrow.setPen(QPen(QColor("#245AC7"), 2))
                    self.addToGroup(bot_arrow)
                else:
                    top_arrow = QGraphicsLineItem(current_x, 0, current_x + 4, -3)
                    top_arrow.setPen(QPen(QColor("#245AC7"), 2))
                    self.addToGroup(top_arrow)
                    bot_arrow = QGraphicsLineItem(current_x, 0, current_x + 4, 3)
                    bot_arrow.setPen(QPen(QColor("#245AC7"), 2))
                    self.addToGroup(bot_arrow)
                self.addToGroup(main_arrow)
                current_x += length_arrow + spacing
        else:
            count_arrow = 0
            while (current_x + length_arrow  < self.length):
                count_arrow += 1
                current_x += length_arrow + spacing
            length_arrow = (self.length - count_arrow * spacing + spacing)/count_arrow
            current_x = 0
            for i in range(count_arrow):
                main_arrow = QGraphicsLineItem(current_x, 0, current_x + length_arrow, 0)
                main_arrow.setPen(QPen(QColor("#245AC7"), 2))
                self.addToGroup(main_arrow)
                if self.value > 0:
                    top_arrow = QGraphicsLineItem(current_x + length_arrow - 4, -3, current_x + length_arrow, 0)
                    top_arrow.setPen(QPen(QColor("#245AC7"), 2))
                    self.addToGroup(top_arrow)
                    bot_arrow = QGraphicsLineItem(current_x + length_arrow - 4, 3, current_x + length_arrow, 0)
                    bot_arrow.setPen(QPen(QColor("#245AC7"), 2))
                    self.addToGroup(bot_arrow)
                else:
                    top_arrow = QGraphicsLineItem(current_x, 0, current_x + 4, -3)
                    top_arrow.setPen(QPen(QColor("#245AC7"), 2))
                    self.addToGroup(top_arrow)
                    bot_arrow = QGraphicsLineItem(current_x, 0, current_x + 4, 3)
                    bot_arrow.setPen(QPen(QColor("#245AC7"), 2))
                    self.addToGroup(bot_arrow)
                current_x += length_arrow + spacing
        self.value = abs(self.value)
        if len(str(self.value)) > 4:
            self.value = "{:.2e}".format(self.value)
        self.text_item = QGraphicsTextItem(f"{self.value}")
        font = self.text_item.font()
        font.setPointSize(11)  # Размер в пунктах
        self.text_item.setFont(font)
        self.setPos(x1, 0)
        x_ = 5
        if len(str(self.value)) != 1:
            x_ = (len(str(self.value)) + 3) * 3
        self.text_item.setDefaultTextColor(QColor("#245AC7"))
        self.addToGroup(self.text_item)

        self.text_item.setPos(length / 2 - x_, 2)


class ConstructionGraphicsView(QGraphicsView):
    def __init__(self, scene):
        super().__init__()
        self.setScene(scene)
        self.setMinimumHeight(200)
        self.graphics_manager = None
        self.setRenderHint(QPainter.Antialiasing)  # Включаем сглаживание
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # self.setup_view()
        self.construction_center_x = 0  # Добавляем переменную для центра конструкции

    def set_graphics_manager(self, manager):
        self.graphics_manager = manager

    def resizeEvent(self, event):
        """Обработка изменения размера"""
        super().resizeEvent(event)
        # Обновляем конструкцию при изменении размера
        if self.graphics_manager:
            QTimer.singleShot(50, self.graphics_manager.update_construction)

    # def setup_view(self):
    #     self.setRenderHint(QPainter.Antialiasing)
    #     self.setDragMode(QGraphicsView.ScrollHandDrag)
    #     self.setDragMode(QGraphicsView.RubberBandDrag)

    def wheelEvent(self, event):
        """Масштабирование колесом мыши"""
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            self.scale(zoom_in_factor, zoom_in_factor)
        else:
            self.scale(zoom_out_factor, zoom_out_factor)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            # Сбрасываем трансформацию к исходному состоянию
            self.resetTransform()
            # Центрируем вид на конструкции
            if self.scene() and self.scene().itemsBoundingRect().isValid():
                self.centerOn(self.construction_center_x, 0)
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            fake_event = QMouseEvent(
                event.type(), event.localPos(), event.screenPos(),
                Qt.LeftButton, Qt.LeftButton, event.modifiers()
            )
            super().mousePressEvent(fake_event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):

        if event.button() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.RubberBandDrag)
        super().mouseReleaseEvent(event)


class ConstructionGraphicsManager:
    def __init__(self):
        self.scene = QGraphicsScene()
        self.view = ConstructionGraphicsView(self.scene)
        self.setup_graphics()
        self.max_width = 700
        self.max_height = 250
        self.current_data = None

    def setup_graphics(self):
        # Настройка сцены
        self.scene.setBackgroundBrush(QBrush(QColor(250, 250, 250)))

        self.view.set_graphics_manager(self)

    def draw_construction(self, data, draw_loads=True):
        """Отрисовка стержней и сил"""
        self.clear_construction()
        self.current_data = data

        if data and data.get("Objects") and data["Objects"][0]["list_of_values"] and data["Objects"][0]['quantity'] != 0:
            if draw_loads:
                self.draw_loads(data)
            self.draw_bar(data)

            # Центрируем конструкцию после отрисовки
            self.center_construction()

    def draw_bar(self, data):
        """Отрисовка стержней"""
        current_x = 0
        first_bar = True
        if not data:
            self.clear_construction()
            return

        max_cross_section = 250

        for i, (scaled_width, scaled_height) in enumerate(self.bar_scaling(data)):
            real_width = data["Objects"][0]["list_of_values"][i]["length"]
            bar_number = data["Objects"][0]["list_of_values"][i]["barNumber"]

            bar_item = BarGraphicsItem(current_x, -scaled_height / 2, scaled_width, scaled_height, bar_number)
            self.scene.addItem(bar_item)

            bar_Number = BarNumber(current_x + (scaled_width) / 2, scaled_height / 2 + 25, bar_number)
            self.scene.addItem(bar_Number)

            LengthBarLine = LengthBarGraphicsItem(current_x, scaled_width, (max_cross_section / 2) + 80, real_width)
            self.scene.addItem(LengthBarLine)

            if first_bar:
                left_line = QGraphicsLineItem(0, scaled_height / 2, 0, (max_cross_section / 2) + 80)
                right_line = QGraphicsLineItem(current_x + scaled_width, scaled_height / 2, current_x + scaled_width,
                                               (max_cross_section / 2) + 80)
                left_line.setPen(QPen(QColor("#0"), 1.5))
                right_line.setPen(QPen(QColor("#0"), 1.5))
                self.scene.addItem(left_line)
                self.scene.addItem(right_line)

                left_node_item = NodeGraphicsItem(0, (max_cross_section / 2) + 50, 1)
                right_node_item = NodeGraphicsItem(current_x + scaled_width, (max_cross_section / 2) + 50, 2)
                self.scene.addItem(left_node_item)
                self.scene.addItem(right_node_item)
            else:
                line = QGraphicsLineItem(current_x + scaled_width,
                                         scaled_height / 2,
                                         current_x + scaled_width,
                                         (max_cross_section / 2) + 80)
                line.setPen(QPen(QColor("#0"), 1.5))
                self.scene.addItem(line)
                node_item = NodeGraphicsItem(current_x + scaled_width,
                                             (max_cross_section / 2) + 50, bar_number + 1)
                self.scene.addItem(node_item)
            current_x += scaled_width
            first_bar = False

        is_left_support = data["Left_support"]
        is_right_support = data["Right_support"]
        length_construction = current_x  # Используем реальную длину конструкции

        if is_left_support:
            left_support = SupportGraphicsItem(0, 0, True, max_cross_section + 20)
            self.scene.addItem(left_support)
        if is_right_support:
            right_support = SupportGraphicsItem(length_construction, 0, False, max_cross_section + 20)
            self.scene.addItem(right_support)

    def draw_loads(self, data):
        """Отрисовка нагрузок"""
        max_node = data["Objects"][0]["quantity"] + 1
        lengths = []
        for length in self.bar_scaling(data):
            lengths.append(length[0])
        bar_numbers = [bar_number["barNumber"] for bar_number in data["Objects"][0]["list_of_values"]]

        for distributed_load in data["Objects"][2]["list_of_values"]:
            current_x = 0
            for i in range(len(bar_numbers)):
                if distributed_load["bar_number"] == bar_numbers[i]:
                    distrload = DistributedLoad(current_x, current_x + lengths[i], lengths[i], distributed_load["distributed_value"])
                    self.scene.addItem(distrload)

                current_x += lengths[i]


        for node_load in data["Objects"][1]["list_of_values"]:
            node_number = node_load["node_number"]
            x_ = 0
            for i in range(len(bar_numbers)):
                if bar_numbers[i] < node_number:
                    x_ += lengths[i]
            if not ((node_number == 1 and data["Left_support"] == 1) or (node_number == max_node and data["Right_support"] == 1)):
                load = NodeLoad(x_, 0, node_load["force_value"])
                self.scene.addItem(load)

    def bar_scaling(self, data):
        # Получаем реальные размеры viewport (учитывая только видимую область)
        viewport_size = self.view.viewport().size()

        # Уменьшаем отступы для лучшего использования пространства
        self.max_width = max(viewport_size.width() - 65, 125)  # Минимальная ширина 100
        self.max_height = 250  # Фиксированная высота для элементов конструкции

        bars_widths = [bars["length"] for bars in data["Objects"][0]["list_of_values"]]
        bars_heights = [bars["cross_section"] for bars in data["Objects"][0]["list_of_values"]]
        sum_width = sum(bars_widths)

        if sum_width == 0:
            return []

        # Масштабируем ширину
        width_scale = self.max_width / sum_width
        scaled_width = [width * width_scale for width in bars_widths]

        # Масштабируем высоту
        max_height = max(bars_heights) if bars_heights else 1
        height_scale = self.max_height / max_height
        scaled_height = [height * height_scale for height in bars_heights]

        # Минимальные размеры
        min_width = 100
        min_height = 50

        scaled_width = [max(min_width, width) for width in scaled_width]
        scaled_height = [max(min_height, height) for height in scaled_height]

        # Проверяем, не превысили ли максимальную ширину
        sum_scaled_width = sum(scaled_width)
        if sum_scaled_width > self.max_width:
            new_width_scale = self.max_width / sum_scaled_width
            scaled_width = [width * new_width_scale for width in scaled_width]

        gain_width = self.correcting_difference_small_values(scaled_width, True)
        gain_height = self.correcting_difference_small_values(scaled_height, False)

        if sum(gain_width) != self.max_width:
            final_width = self.normalization_amounts(gain_width, self.max_width)
        else:
            final_width = gain_width

        return list(zip(final_width, gain_height))

    def correcting_difference_small_values(self, values, is_width):
        if len(values) < 2:
            return values
        else:
            max_value = max(values)
            min_value = min(values)
            if (max_value - min_value) < (0.02 * max_value):
                ratio = 3 if is_width else 2
                avg_value = sum(values) / len(values)
                new_values = list()
                for value in values:
                    if value > avg_value:
                        new_values.append(value * (1 + ratio * (value - avg_value)/avg_value))
                    else:
                        new_values.append(value * (1 - ratio * (value - avg_value) / avg_value))
                if is_width:
                    return self.normalization_amounts(new_values, sum(values))
                else:
                    max_new_value = max(new_values)
                    ratio = max(values)/max_new_value if max_new_value > 0 else 1
                    return [value * ratio for value in new_values]
            return values


    def normalization_amounts(self, values, sum_past_values):
        sum_values = sum(values)
        if sum_values == 0:
            return [sum_past_values/len(values)] * len(values)
        else:
            ratio = sum_past_values / sum_values
            return [value * ratio for value in values]

    def center_construction(self):
        """Центрирует конструкцию в viewport"""
        if self.scene.items():
            # Получаем bounding rect всей сцены
            rect = self.scene.itemsBoundingRect()
            self.view.setSceneRect(rect)

            # Вычисляем центр конструкции по X
            self.view.construction_center_x = rect.center().x()

            # Центрируем view на конструкции
            self.view.centerOn(rect.center())

    def update_construction(self):
        """Перерисовывает конструкцию с текущими данными"""
        if self.current_data and self.current_data["Objects"][0]['quantity'] != 0:
            self.draw_construction(self.current_data)

    def clear_construction(self):
        """Очистка сцены"""
        self.scene.clear()

    def save_construction_image(self, filename):
        """Сохранить изображение конструкции в файл"""
        try:
            # Создаем pixmap из graphics view
            pixmap = self.view.grab()
            pixmap.save(filename, "PNG")
            return True
        except Exception as e:
            print(f"Ошибка сохранения изображения: {e}")
            return False
