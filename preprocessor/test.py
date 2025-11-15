from processor.processor import Processor
import json

path = r'D:\SAPR\projects\6.json'
with open(path, 'r', encoding='utf-8') as file:
    data = json.load(file)
processor = Processor(data)
processor.displacement_vectors()
