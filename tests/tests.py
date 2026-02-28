"""
Тесты для различных источников задач
"""
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock
from typing import List

from src.process import TaskProcessor
from src.contract import TaskSource, Task
from src.sources.filesrc import FileTaskSource
from src.sources.gensrc import GenTaskSource
from src.sources.apisrc import APITaskSource

class TestFileTaskSource:
    """Тесты для файлового источника задач"""

    @pytest.fixture
    def temp_json_file(self):
        test_data = [
            {"payload": "Task 1", "id": "id1"},
            {"payload": "Task 2"},
            {"payload": "Task 3", "id": "id3"}
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(test_data, f)
            temp_path = f.name

        yield Path(temp_path)

    def test_get_tasks_from_valid_file(self, temp_json_file):
        source = FileTaskSource(str(temp_json_file))
        tasks = source.get_tasks()

        assert len(tasks) == 3
        assert all(isinstance(t, Task) for t in tasks)
        assert tasks[0].payload == "Task 1"
        assert tasks[1].payload == "Task 2"

    def test_file_not_found(self):
        source = FileTaskSource("non_existent_file.json")

        with pytest.raises(FileNotFoundError):
            source.get_tasks()

    def test_invalid_json_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json {")
            temp_path = f.name

        source = FileTaskSource(temp_path)

        with pytest.raises(json.JSONDecodeError):
            source.get_tasks()

        Path(temp_path).unlink()

    def test_empty_json_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("[]")
            temp_path = f.name

        source = FileTaskSource(temp_path)
        tasks = source.get_tasks()

        assert len(tasks) == 0

        Path(temp_path).unlink()


class TestGeneratorTaskSource:
    """Тесты для генератора задач"""

    def test_default_generation(self):
        source = GenTaskSource()
        tasks = source.get_tasks()

        assert len(tasks) == 10
        assert all(isinstance(t, Task) for t in tasks)

    def test_custom_count(self):
        """Указанное количество задач"""
        count = 5
        source = GenTaskSource(count=count)
        tasks = source.get_tasks()

        assert len(tasks) == count

    def test_custom_prefix(self):
        """Uспользование префикса в данных"""
        prefix = "test_prefix"
        source = GenTaskSource(count=3, prefix=prefix)
        tasks = source.get_tasks()

        for task in tasks:
            assert task.payload.startswith(prefix)

    def test_generated_tasks_have_unique_ids(self):
        """Уникальность ID в сгенерированных тасках"""
        source = GenTaskSource(count=100)
        tasks = source.get_tasks()

        ids = [t.id for t in tasks]
        assert len(ids) == len(set(ids))

    def test_generate_different_payloads(self):
        """Проверка, что генерируются разные payload"""
        source = GenTaskSource(count=50)
        tasks = source.get_tasks()

        payloads = [t.payload for t in tasks]
        assert len(set(payloads)) > 1


class TestAPITaskSource:
    def test_get_tasks_from_stub(self):
        """Тест получения задач из API-заглушки"""
        source = APITaskSource()
        tasks = source.get_tasks()

        assert len(tasks) == 3
        assert all(isinstance(t, Task) for t in tasks)

    def test_custom_endpoint(self):
        """Тест с пользовательским endpoint"""
        custom_endpoint = "https://custom-api.example.com"
        source = APITaskSource(endpoint=custom_endpoint)
        tasks = source.get_tasks()

        assert len(tasks) == 3
        assert custom_endpoint in tasks[0].payload

    @patch('time.sleep')
    def test_simulate_api_call(self, mock_sleep):
        """Uмитация вызова API"""
        source = APITaskSource()
        api_data = source._simulate_api_call()

        assert len(api_data) == 3
        mock_sleep.assert_called_once_with(0.5)

    def test_consistent_data(self):
        source = APITaskSource()

        tasks1 = source.get_tasks()
        tasks2 = source.get_tasks()

        # Данные должны быть одинаковыми (заглушка)
        assert len(tasks1) == len(tasks2)
        for t1, t2 in zip(tasks1, tasks2):
            assert t1.payload == t2.payload
            assert t1.id != t2.id


class TestTaskProcessor:
    """Тесты для TaskProcessor"""

    @pytest.fixture
    def processor(self):
        return TaskProcessor()

    @pytest.fixture
    def valid_source(self):
        source = Mock(spec=TaskSource)
        source.get_tasks.return_value = [
            Task.create("test1"),
            Task.create("test2")
        ]
        source.__class__.__name__ = "MockSource"
        return source

    @pytest.fixture
    def invalid_source(self):
        source = Mock()
        # Не имеет метода get_tasks
        del source.get_tasks
        source.__class__.__name__ = "InvalidSource"
        return source

    def test_add_valid_source(self, processor, valid_source):
        result = processor.add_source(valid_source)

        assert result is True
        assert processor.get_source_count() == 1

    def test_add_invalid_source(self, processor, invalid_source):
        result = processor.add_source(invalid_source)

        assert result is False
        assert processor.get_source_count() == 0

    def test_collect_from_single_source(self, processor, valid_source):
        processor.add_source(valid_source)
        tasks = processor.collect_all_tasks()

        assert len(tasks) == 2
        valid_source.get_tasks.assert_called_once()

    def test_collect_from_multiple_sources(self, processor):
        sources = []
        for i in range(3):
            source = Mock(spec=TaskSource)
            source.get_tasks.return_value = [Task.create(f"test{i}_1"), Task.create(f"test{i}_2")]
            source.__class__.__name__ = f"MockSource{i}"
            sources.append(source)
            processor.add_source(source)

        tasks = processor.collect_all_tasks()

        assert len(tasks) == 6  # 3 источника * 2 задачи
        for source in sources:
            source.get_tasks.assert_called_once()

    def test_collect_from_empty_processor(self, processor):
        tasks = processor.collect_all_tasks()
        assert len(tasks) == 0

    def test_source_count(self, processor):
        assert processor.get_source_count() == 0

        for i in range(5):
            source = Mock(spec=TaskSource)
            processor.add_source(source)
            assert processor.get_source_count() == i + 1


class TestArchitectureExtensibility:
    def test_new_source_without_changing_existing_code(self):
        class DatabaseTaskSource:
            def __init__(self, connection_string: str):
                self.connection_string = connection_string
                self._mock_data = ["db_item1", "db_item2", "db_item3"]

            def get_tasks(self) -> List[Task]:
                return [Task.create(payload=item) for item in self._mock_data]

        processor = TaskProcessor()
        db_source = DatabaseTaskSource("sqlite://test.db")

        assert isinstance(db_source, TaskSource)

        result = processor.add_source(db_source)
        assert result is True

        tasks = processor.collect_all_tasks()
        assert len(tasks) == 3
        assert all(t.payload.startswith("db_item") for t in tasks)

    def test_multiple_new_sources(self):
        class RedisTaskSource:
            def __init__(self, host: str):
                self.host = host

            def get_tasks(self) -> List[Task]:
                return [Task.create("redis_data")]

        class KafkaTaskSource:
            def __init__(self, topic: str):
                self.topic = topic

            def get_tasks(self) -> List[Task]:
                return [Task.create("kafka_msg1"), Task.create("kafka_msg2")]

        class GraphQLSource:
            def __init__(self, endpoint: str):
                self.endpoint = endpoint

            def get_tasks(self) -> List[Task]:
                return [Task.create("graphql_data")]

        processor = TaskProcessor()

        sources = [
            RedisTaskSource("localhost"),
            KafkaTaskSource("tasks-topic"),
            GraphQLSource("http://graphql.example.com")
        ]
        for source in sources:
            assert processor.add_source(source) is True

        assert processor.get_source_count() == 3

        tasks = processor.collect_all_tasks()
        assert len(tasks) == 4

        payloads = [t.payload for t in tasks]
        assert "redis_data" in payloads
        assert "kafka_msg1" in payloads
        assert "kafka_msg2" in payloads
        assert "graphql_data" in payloads


class TestIntegration:
    """Интеграционные тесты всей системы"""

    @pytest.fixture
    def test_file(self):
        """Создание тестового файла"""
        data = [
            {"payload": "file_task_1"},
            {"payload": "file_task_2"}
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            path = f.name

        yield Path(path)
        Path(path).unlink()

    def test_full_pipeline_with_all_sources(self, test_file):
        """
        Тест полного цикла работы со всеми источниками
        """
        processor = TaskProcessor()

        # Добавляем все типы источников
        sources = [
            FileTaskSource(str(test_file)),
            GenTaskSource(count=3, prefix="gen"),
            APITaskSource(endpoint="https://test-api.example.com")
        ]

        for source in sources:
            assert processor.add_source(source) is True

        assert processor.get_source_count() == 3

        all_tasks = processor.collect_all_tasks()

        assert len(all_tasks) == 8

        payloads = [t.payload for t in all_tasks]

        assert "file_task_1" in payloads
        assert "file_task_2" in payloads

        gen_tasks = [p for p in payloads if p.startswith("gen_")]
        assert len(gen_tasks) == 3

        api_tasks = [p for p in payloads if "test-api" in p]
        assert len(api_tasks) == 3

    def test_duck_typing_in_action(self, test_file):
        class DuckSource:
            def __init__(self, data):
                self.data = data

            def get_tasks(self):
                return [Task.create(d) for d in self.data]

        processor = TaskProcessor()

        duck = DuckSource(["quack1", "quack2", "quack3"])

        assert processor.add_source(duck) is True

        tasks = processor.collect_all_tasks()
        assert len(tasks) == 3
        assert all("quack" in t.payload for t in tasks)
