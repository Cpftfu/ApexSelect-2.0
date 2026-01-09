import os
import re


def find_namespace_usage():
    project_root = os.path.dirname(os.path.abspath(__file__))

    for root, dirs, files in os.walk(project_root):
        for file in files:
            if file.endswith(('.html', '.py', '.txt')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'apexSelect' in content:
                            print(f"\n=== Найдено в файле: {filepath} ===")
                            lines = content.split('\n')
                            for i, line in enumerate(lines, 1):
                                if 'apexSelect' in line.lower():
                                    print(f"Строка {i}: {line.strip()}")
                except Exception as e:
                    print(f"Ошибка чтения файла {filepath}: {e}")


if __name__ == "__main__":
    find_namespace_usage()