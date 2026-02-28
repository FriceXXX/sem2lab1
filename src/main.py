import json
import tempfile
from pathlib import Path

from typing import List
from src.contract import Task
from src.process import TaskProcessor
from sources import FileTaskSource, GenTaskSource, APITaskSource


def create_test_file() -> Path: # файл для демонстрации
    """временный файл с тестовыми задачами."""
    test_data = [
        {"payload": "Task from file 1"},
        {"payload": "Task from file 2"},
        {"payload": "Task from file 3"}
    ]

    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump(test_data, temp_file)
    temp_file.close()
    return Path(temp_file.name)


def main():
    processor = TaskProcessor()
    test_file = create_test_file()

    # пока демонстрация
    try:
        sources = [
            FileTaskSource(str(test_file)),
            GenTaskSource(count=5, prefix="test"),
            APITaskSource(endpoint="https://demo-api.example.com")
        ]

        print("\nДобавление источников:")
        for source in sources:
            processor.add_source(source)

        print(f"\nВсего активных источников: {processor.get_source_count()}")

        print("\nСбор задач из всех источников:")
        all_tasks = processor.collect_all_tasks()

        print(f"\nВсего собрано задач: {len(all_tasks)}")

    finally:
        test_file.unlink()


def demonstrate_extension(): # демонстрация здесь и в тестах
    class CustomSource:
        def __init__(self, custom_data: list):
            self.custom_data = custom_data

        def get_tasks(self) -> List[Task]:
            return [Task.create(payload=item) for item in self.custom_data]

    processor = TaskProcessor()
    custom_source = CustomSource(["custom1", "custom2", "custom3"])

    processor.add_source(custom_source)

    tasks = processor.collect_all_tasks()
    print(f"\nПолучено задач из пользовательского источника: {len(tasks)}")
    for task in tasks:
        print(f"  - {task.payload}")


if __name__ == "__main__":
    main()
    demonstrate_extension()