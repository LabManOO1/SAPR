class Validator:
    def __init__(self, main_window):
        self.main_window = main_window

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
                    self.main_window.starus_bar_label.setText(
                        "Есть распределенная нагрузка на несуществующий стержень!")
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