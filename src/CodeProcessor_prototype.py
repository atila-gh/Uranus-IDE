import os
import re

class CodeProcessor():
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'text.txt')

        with open(file_path, mode='r', encoding='utf-8') as f:
            self.code = f.readlines()

        self.main = {}
        self.process()

    def process(self):
        class_pattern = re.compile(r'^\s*class\s+(\w+)\s*(?:\(|:)')
        for line in self.code:
            match = class_pattern.match(line)
            if match:
                class_name = match.group(1)
                print(class_name)

obj = CodeProcessor()