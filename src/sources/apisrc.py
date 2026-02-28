from typing import List, Optional
import time

from src.contract import Task, TaskSource


class APITaskSource:
    def __init__(self, endpoint: str = "http://stub-api.example.com/tasks"):
        self.endpoint = endpoint
        self._mock_data = [
            {"payload": f"API data from {endpoint} - item 1"},
            {"payload": f"API data from {endpoint} - item 2"},
            {"payload": f"API data from {endpoint} - item 3"},
        ]

    def _simulate_api_call(self) -> List[dict]:
        time.sleep(0.5)  # тип задержка
        return self._mock_data

    def get_tasks(self) -> List[Task]:
        print(f"API call example: {self.endpoint}")
        api_data = self._simulate_api_call()

        tasks = []
        for item in api_data:
            task = Task.create(payload=item['payload'])
            tasks.append(task)

        return tasks