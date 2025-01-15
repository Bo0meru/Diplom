import os
import re

# Функция для подсчета строк кода, классов и методов в файле
def analyze_file(file_path, file_type):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    line_count = len(lines)
    class_count = 0
    method_count = 0

    for line in lines:
        # Убираем лишние пробелы
        stripped_line = line.strip()
        
        # Считаем классы и методы в зависимости от типа файла
        if file_type == "python" and stripped_line.startswith("class "):
            class_count += 1
        elif file_type == "python" and stripped_line.startswith("def "):
            method_count += 1
        elif file_type == "javascript" and re.search(r'function\s+\w+|\w+\s*=\s*\(.*\)\s*=>', stripped_line):
            method_count += 1
        elif file_type == "css" and stripped_line.endswith("{"):
            class_count += 1
        elif file_type == "django" and re.search(r'\{%\s+(block|extends|include)', stripped_line):
            method_count += 1

    return line_count, class_count, method_count

# Основная функция для анализа директории
def analyze_directory(directory):
    stats = {
        'python': {'lines': 0, 'classes': 0, 'methods': 0},
        'javascript': {'lines': 0, 'classes': 0, 'methods': 0},
        'css': {'lines': 0, 'classes': 0, 'methods': 0},
        'django': {'lines': 0, 'classes': 0, 'methods': 0},
    }

    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)

            if file.endswith('.py'):
                file_type = 'python'
            elif file.endswith('.js'):
                file_type = 'javascript'
            elif file.endswith('.css'):
                file_type = 'css'
            elif file.endswith('.html'):
                file_type = 'django'
            else:
                continue

            lines, classes, methods = analyze_file(file_path, file_type)
            stats[file_type]['lines'] += lines
            stats[file_type]['classes'] += classes
            stats[file_type]['methods'] += methods

    return stats

# Тестирование скрипта
def main():
    directory = input("Введите путь к директории для анализа: ")
    stats = analyze_directory(directory)

    for lang, data in stats.items():
        print(f"\nЯзык: {lang}")
        print(f"Строк кода: {data['lines']}")
        print(f"Классов: {data['classes']}")
        print(f"Методов: {data['methods']}")

if __name__ == "__main__":
    main()
