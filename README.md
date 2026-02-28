# Лабораторная работа №1. Источники задач и контракты
---
## Цель:
Освоить duck typing и контрактное программирование на примере источников задач.
---
## Структура
```
sem2lab1/
├── src/
│   ├── __init__.py
│   ├── contract.py
│   ├── main.py
│   ├── process.py
│   │
│   └── sources/
│       ├── __init__.py
│       ├── apisrc.py
│       ├── filesrc.py
│       └── gensrc.py
├── tests/
│   ├── test_files/
│   │   └── test_tasks.json
│   └── tests.py
├── .gitignore
└── README.md
```
## Реализовано:
- Контракт TaskSource с использованием typing.Protocol и runtime_checkable
- Источники задач (файловый, генератор, API)
- Процессор задач с runtime-проверкой соблюдения контракта
---
## Используемые библиотеки:
- typing
- dataclasses
- uuid
- time
- random
- pytest
- json
---
## Запуск
```
python -m src.main
```
## Вывод
В ходе выполнения лабораторной работы была разработана подсистема приёма задач, основанная на принципах duck typing и контрактного программирования.
