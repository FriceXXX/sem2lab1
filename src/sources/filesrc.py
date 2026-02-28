import json
from typing import List, Optional
from pathlib import Path
from uuid import uuid4

from src.contract import Task, TaskSource


class FileTaskSource:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def get_tasks(self) -> List[Task]:
        """
        Expected format:
        [
            {"payload": "task1 data"},
            {"payload": "task2 data"}
        ]
        :return: List[Task]
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"Файл {self.file_path} не найден")

        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        tasks = []
        for item in data:
            # Если в файле указан id, используем его, иначе генерируем новый
            if isinstance(item, dict) and 'payload' in item:
                task = Task(
                    id=item.get('id', str(uuid4())),
                    payload=item['payload']
                )
                tasks.append(task)

        return tasks