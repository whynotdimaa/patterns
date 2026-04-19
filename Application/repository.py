"""
Data Access Layer — EmployeeRepository.
Абстрагує джерело даних від бізнес-логіки.
"""

from __future__ import annotations
from factory import DatabaseConnection
from employees import Employee


class EmployeeRepository:
    """Репозиторій для отримання співробітників через будь-яке підключення."""

    def __init__(self, connection: DatabaseConnection):
        self._connection = connection

    def get_all(self) -> list[Employee]:
        with self._connection:
            return self._connection.fetch_employees()

    def get_by_department(self, department: str) -> list[Employee]:
        return [e for e in self.get_all() if e.department == department]

    def get_by_role(self, role: str) -> list[Employee]:
        return [e for e in self.get_all() if e.role == role]
