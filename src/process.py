from typing import List, Union, Any
from src.contract import TaskSource, Task


class TaskProcessor:
    def __init__(self):
        self.sources: List[TaskSource] = []

    def add_source(self, source: Any) -> bool:
        if isinstance(source, TaskSource): # runtime-проверка
            self.sources.append(source)
            print(f"Источник {source.__class__.__name__} успешно добавлен")
            return True
        else:
            print(f"Ошибка: {source.__class__.__name__} не реализует контракт TaskSource")
            return False

    def collect_all_tasks(self) -> List[Task]:
        all_tasks = []

        for source in self.sources:
            try:
                tasks = source.get_tasks()
                print(f"Получено {len(tasks)} задач из {source.__class__.__name__}")
                all_tasks.extend(tasks)
            except Exception as e:
                print(f"Ошибка при получении задач из {source.__class__.__name__}: {e}")

        return all_tasks

    def get_source_count(self) -> int:
        return len(self.sources)