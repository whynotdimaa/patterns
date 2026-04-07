"""
Factory Method Pattern — DBConnectionFactory.
Створює конкретні підключення до БД за типом.
Підтримує реєстрацію нових типів без зміни коду фабрики.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable, Type
from builder import ConnectionConfig
from employees import Employee


class DatabaseConnection(ABC):
    """Абстрактний клас підключення до БД."""

    def __init__(self, config: ConnectionConfig):
        self.config = config
        self._connected = False

    def connect(self) -> None:
        self._connected = True
        print(f"[{self.__class__.__name__}] Підключено: {self._connection_string()}")

    def disconnect(self) -> None:
        self._connected = False
        print(f"[{self.__class__.__name__}] Відключено")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *_):
        self.disconnect()

    @abstractmethod
    def fetch_employees(self) -> list[Employee]:
        """Отримує список співробітників з джерела даних."""
        ...

    @abstractmethod
    def _connection_string(self) -> str: ...

    @property
    def db_type(self) -> str:
        return self.config.get("type", "unknown")


# ──────────────────────────────────────────────
# Конкретні реалізації
# ──────────────────────────────────────────────

class PostgreSQLConnection(DatabaseConnection):
    """
    Підключення до PostgreSQL.
    У реальному проєкті використовується psycopg2 або asyncpg.
    Тут емулюємо дані відділу Engineering.
    """

    def _connection_string(self) -> str:
        cfg = self.config
        return (f"postgresql://{cfg.get('user')}:***@"
                f"{cfg.get('host')}:{cfg.get('port')}/{cfg.get('database')}")

    def fetch_employees(self) -> list[Employee]:
        from employees import Manager, OfficeClerk, SalesManager, SysAdmin
        # Симуляція SQL-запиту: SELECT * FROM employees WHERE department='Engineering'
        return [
            Manager(1,  "Alice Koval",       "Engineering", 5000, 0.20),
            Manager(2,  "Borys Shevchenko",  "Engineering", 5500, 0.18),
            OfficeClerk(3,  "Daryna Melnyk",     "Engineering", 25.0, 168),
            OfficeClerk(4,  "Oleh Bondarenko",   "Engineering", 22.0, 160),
            SysAdmin(5,  "Ivan Pavlenko",     "Engineering", 4500, 40, 30),
            SysAdmin(6,  "Natalia Kravchenko","Engineering", 4200, 35, 28),
            SalesManager(7, "Yulia Fedorenko",  "Engineering", 3000, 0.05, 80_000),
        ]


class RedisConnection(DatabaseConnection):
    """
    Підключення до Redis.
    У реальному проєкті використовується redis-py.
    Redis зберігає JSON-хеші, тут емулюємо відділ Marketing.
    """

    def _connection_string(self) -> str:
        cfg = self.config
        return f"redis://{cfg.get('host')}:{cfg.get('port')}/db{cfg.get('db', 0)}"

    def fetch_employees(self) -> list[Employee]:
        from employees import Manager, OfficeClerk, SalesManager, SysAdmin
        # Симуляція: HGETALL employee:* з Redis
        return [
            Manager(8,  "Andriy Tkachenko",  "Marketing", 4800, 0.25),
            OfficeClerk(9,  "Svitlana Kovalenko","Marketing", 20.0, 176),
            SalesManager(10, "Roman Petrenko",   "Marketing", 2800, 0.07, 120_000),
            SalesManager(11, "Kateryna Lysenko",  "Marketing", 3200, 0.06,  95_000),
            SysAdmin(12, "Mykola Moroz",      "Marketing", 4000, 20, 32),
        ]


class ExcelConnection(DatabaseConnection):
    """
    Підключення до Excel-файлу.
    У реальному проєкті використовується openpyxl або pandas.
    Тут емулюємо читання аркуша Finance.xlsx.
    """

    def _connection_string(self) -> str:
        return f"excel://{self.config.get('file_path', 'employees.xlsx')}"

    def fetch_employees(self) -> list[Employee]:
        from employees import Manager, OfficeClerk, SalesManager, SysAdmin
        # Симуляція читання рядків з Excel-аркуша
        return [
            Manager(13, "Iryna Savchenko",   "Finance", 5200, 0.22),
            OfficeClerk(14, "Vasyl Rudenko",     "Finance", 24.0, 172),
            OfficeClerk(15, "Oksana Karpenko",   "Finance", 23.0, 168),
            SalesManager(16, "Serhiy Hrytsenko",  "Finance", 3100, 0.04, 60_000),
            SysAdmin(17, "Tetyana Marchenko", "Finance", 4300, 50, 27),
        ]


# ──────────────────────────────────────────────
# Фабрика
# ──────────────────────────────────────────────

class DBConnectionFactory:
    """
    Factory Method: створює DatabaseConnection за полем type у конфігурації.
    Нові типи реєструються через register_type() — без змін коду фабрики.
    """

    _registry: dict[str, Callable[[ConnectionConfig], DatabaseConnection]] = {
        "postgresql": PostgreSQLConnection,
        "redis":      RedisConnection,
        "excel":      ExcelConnection,
    }

    @classmethod
    def register_type(cls,
                      type_name: str,
                      creator: Callable[[ConnectionConfig], DatabaseConnection]) -> None:
        """Розширення фабрики новим типом БД."""
        cls._registry[type_name.lower()] = creator
        print(f"[Factory] Зареєстровано новий тип: {type_name!r}")

    @classmethod
    def create(cls, config: ConnectionConfig) -> DatabaseConnection:
        db_type = config.get("type", "").lower()
        creator = cls._registry.get(db_type)
        if creator is None:
            known = list(cls._registry.keys())
            raise ValueError(
                f"Невідомий тип БД: {db_type!r}. Відомі типи: {known}")
        return creator(config)

    @classmethod
    def supported_types(cls) -> list[str]:
        return list(cls._registry.keys())
