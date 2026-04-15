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
import psycopg2
import redis

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
    def _connection_string(self) -> str:
        cfg = self.config
        return f"postgresql://{cfg.get('user')}:***@{cfg.get('host')}:{cfg.get('port')}/{cfg.get('database')}"

    def fetch_employees(self) -> list[Employee]:
        from employees import Manager, OfficeClerk, SalesManager, SysAdmin
        cfg = self.config
        # Підключення до бази, яку ми створили в Docker/CMD
        conn = psycopg2.connect(
            host=cfg.get('host'),
            port=cfg.get('port'),
            database=cfg.get('database'),
            user=cfg.get('user'),
            password=cfg.get('password')
        )
        employees = []
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, department, role, base_salary, bonus, hourly_rate, hours_per_month, commission_rate, monthly_sales, on_call_hours, on_call_rate FROM employees")
            for row in cur.fetchall():
                # Логіка створення об'єктів залежно від ролі (role)
                eid, name, dept, role, sal, bonus, h_rate, h_month, c_rate, sales, oc_h, oc_r = row
                if role == "Manager":
                    employees.append(Manager(eid, name, dept, float(sal), float(bonus)))
                elif role == "SysAdmin":
                    employees.append(SysAdmin(eid, name, dept, float(sal), float(oc_h), float(oc_r)))
                # Додайте інші ролі аналогічно
        conn.close()
        return employees

class RedisConnection(DatabaseConnection):
    def _connection_string(self) -> str:
        cfg = self.config
        return f"redis://{cfg.get('host')}:{cfg.get('port')}/db{cfg.get('db', 0)}"

    def fetch_employees(self) -> list[Employee]:
        from employees import Manager, SalesManager, SysAdmin
        cfg = self.config
        r = redis.Redis(host=cfg.get('host'), port=cfg.get('port'), db=cfg.get('db', 0), decode_responses=True)

        employees = []
        # Шукаємо всі ключі співробітників, які ми вводили через HSET
        for key in r.scan_iter("employee:*"):
            data = r.hgetall(key)
            eid = int(key.split(":")[-1])
            role = data.get("role")

            if role == "Manager":
                employees.append(Manager(eid, data['name'], data['dept'], float(data['salary']), float(data['bonus'])))
            elif role == "SalesManager":
                employees.append(SalesManager(eid, data['name'], data['dept'], float(data['salary']), float(data['commission']), float(data['sales'])))
            elif role == "SysAdmin":
                employees.append(SysAdmin(eid, data['name'], data['dept'], float(data['salary']), float(data['on_call_hours']), float(data['on_call_rate'])))
        return employees


import pandas as pd


class ExcelConnection(DatabaseConnection):


    def fetch_employees(self) -> list[Employee]:
        from employees import Manager, OfficeClerk, SalesManager, SysAdmin


        file_path = self.config.get('file_path', 'data/Finance.xlsx')
        # Читаємо Excel через pandas
        df = pd.read_excel(file_path, sheet_name=self.config.get('sheet_name', 0))

        employees = []
        for _, row in df.iterrows():
            role = row['role']
            eid, name, dept = int(row['id']), str(row['name']), str(row['department'])

            if role == "Manager":
                employees.append(Manager(eid, name, dept, float(row['base_salary']), float(row['bonus'])))
            elif role == "OfficeClerk":
                employees.append(OfficeClerk(eid, name, dept, float(row['hourly_rate']), float(row['hours_per_month'])))
            elif role == "SalesManager":
                employees.append(SalesManager(eid, name, dept, float(row['base_salary']), float(row['commission_rate']),
                                              float(row['monthly_sales'])))
            elif role == "SysAdmin":
                employees.append(SysAdmin(eid, name, dept, float(row['base_salary']), float(row['on_call_hours']),
                                          float(row['on_call_rate'])))

        return employees

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
