"""
Prototype Pattern — EmployeePrototypeRegistry.
Зберігає еталонні об'єкти та клонує їх для створення нових співробітників.
"""

from __future__ import annotations
from typing import Any
from employees import Employee, Manager, OfficeClerk, SalesManager, SysAdmin


class EmployeePrototypeRegistry:
    """Реєстр прототипів співробітників."""

    _prototypes: dict[str, Employee] = {}

    @classmethod
    def register(cls, role: str, prototype: Employee) -> None:
        cls._prototypes[role] = prototype

    @classmethod
    def clone(cls, role: str, **overrides: Any) -> Employee:
        if role not in cls._prototypes:
            raise KeyError(f"Немає прототипу для ролі: {role!r}")
        obj = cls._prototypes[role].clone()
        for key, value in overrides.items():
            setattr(obj, key, value)
        return obj

    @classmethod
    def registered_roles(cls) -> list[str]:
        return list(cls._prototypes.keys())


# Реєструємо еталонні прототипи
EmployeePrototypeRegistry.register("Manager",
    Manager(0, "", "", base_salary=5000.0, bonus=0.20))

EmployeePrototypeRegistry.register("OfficeClerk",
    OfficeClerk(0, "", "", hourly_rate=22.0, hours_per_month=168.0))

EmployeePrototypeRegistry.register("SalesManager",
    SalesManager(0, "", "", base_salary=3000.0, commission_rate=0.05, monthly_sales=50000.0))

EmployeePrototypeRegistry.register("SysAdmin",
    SysAdmin(0, "", "", base_salary=4000.0, on_call_hours=20.0, on_call_rate=28.0))
