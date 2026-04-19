"""
Domain Layer — Employee entities.
Кожен клас є прототипом (підтримує copy/clone через Prototype патерн).
"""

from __future__ import annotations
import copy
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


class Employee(ABC):
    """Базовий абстрактний клас для всіх типів співробітників."""

    def __init__(self, id: int, name: str, department: str):
        self.id = id
        self.name = name
        self.department = department

    @property
    @abstractmethod
    def role(self) -> str: ...

    @abstractmethod
    def compensation(self) -> float: ...

    def clone(self) -> "Employee":
        """Prototype: повертає глибоку копію об'єкта."""
        return copy.deepcopy(self)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "department": self.department,
            "role": self.role,
            "compensation": round(self.compensation(), 2),
        }

    def __repr__(self) -> str:
        return f"{self.role}(id={self.id}, name={self.name!r}, dept={self.department!r}, salary={self.compensation():.2f})"


class Manager(Employee):
    """
    Менеджер відділу.
    compensation = base_salary + base_salary * bonus
    """

    def __init__(self, id: int, name: str, department: str,
                 base_salary: float, bonus: float):
        super().__init__(id, name, department)
        self.base_salary = base_salary
        self.bonus = bonus          # відсоток премії, напр. 0.2 = 20%

    @property
    def role(self) -> str:
        return "Manager"

    def compensation(self) -> float:
        return self.base_salary + self.base_salary * self.bonus

    def to_dict(self) -> dict:
        return {**super().to_dict(),
                "base_salary": self.base_salary,
                "bonus": self.bonus}


class OfficeClerk(Employee):
    """
    Офісний працівник (погодинна оплата).
    compensation = hourly_rate * hours_per_month
    """

    def __init__(self, id: int, name: str, department: str,
                 hourly_rate: float, hours_per_month: float):
        super().__init__(id, name, department)
        self.hourly_rate = hourly_rate
        self.hours_per_month = hours_per_month

    @property
    def role(self) -> str:
        return "OfficeClerk"

    def compensation(self) -> float:
        return self.hourly_rate * self.hours_per_month

    def to_dict(self) -> dict:
        return {**super().to_dict(),
                "hourly_rate": self.hourly_rate,
                "hours_per_month": self.hours_per_month}


class SalesManager(Employee):
    """
    Менеджер з продажів.
    compensation = base_salary + monthly_sales * commission_rate
    """

    def __init__(self, id: int, name: str, department: str,
                 base_salary: float, commission_rate: float, monthly_sales: float):
        super().__init__(id, name, department)
        self.base_salary = base_salary
        self.commission_rate = commission_rate   # частка від продажів
        self.monthly_sales = monthly_sales       # обсяг продажів за місяць

    @property
    def role(self) -> str:
        return "SalesManager"

    def compensation(self) -> float:
        return self.base_salary + self.monthly_sales * self.commission_rate

    def to_dict(self) -> dict:
        return {**super().to_dict(),
                "base_salary": self.base_salary,
                "commission_rate": self.commission_rate,
                "monthly_sales": self.monthly_sales}


class SysAdmin(Employee):
    """
    Системний адміністратор.
    compensation = base_salary + on_call_hours * on_call_rate * 1.5
    (коефіцієнт 1.5 — понаднормова ставка)
    """

    def __init__(self, id: int, name: str, department: str,
                 base_salary: float, on_call_hours: float, on_call_rate: float):
        super().__init__(id, name, department)
        self.base_salary = base_salary
        self.on_call_hours = on_call_hours   # кількість чергових годин
        self.on_call_rate = on_call_rate     # тариф за чергову годину

    @property
    def role(self) -> str:
        return "SysAdmin"

    def compensation(self) -> float:
        return self.base_salary + self.on_call_hours * self.on_call_rate * 1.5

    def to_dict(self) -> dict:
        return {**super().to_dict(),
                "base_salary": self.base_salary,
                "on_call_hours": self.on_call_hours,
                "on_call_rate": self.on_call_rate}
