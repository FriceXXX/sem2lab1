from typing import List, Generator
import random
import string

from src.contract import Task, TaskSource

class GenTaskSource:
    def __init__(self, count: int = 10, prefix: str = "gen"):
        self.count = count
        self.prefix = prefix

    def _generate_payload(self) -> str:
        length = random.randint(5, 20)
        return f"{self.prefix}_{''.join(random.choices(string.ascii_letters, k=length))}"

    def get_tasks(self) -> List[Task]:
        tasks = []
        for i in range(self.count):
            task = Task.create(payload=self._generate_payload())
            tasks.append(task)
        return tasks