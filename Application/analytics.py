"""
Business Logic Layer — EmployeeAnalyticsService.
Статистичний аналіз по співробітниках різних відділів.
"""

from __future__ import annotations
import statistics
from collections import defaultdict
from typing import NamedTuple
from employees import Employee


class DepartmentStats(NamedTuple):
    department: str
    count: int
    avg_compensation: float
    total_compensation: float
    min_compensation: float
    max_compensation: float
    median_compensation: float
    roles_breakdown: dict[str, int]


class EmployeeAnalyticsService:
    """Сервіс аналітики персоналу."""

    def __init__(self, employees: list[Employee]):
        self._employees = employees

    # ── Базова статистика ──────────────────────────────────────

    def average_compensation(self, employees: list[Employee] | None = None) -> float:
        pool = employees or self._employees
        if not pool:
            return 0.0
        return statistics.mean(e.compensation() for e in pool)

    def total_compensation(self, employees: list[Employee] | None = None) -> float:
        pool = employees or self._employees
        return sum(e.compensation() for e in pool)

    def median_compensation(self, employees: list[Employee] | None = None) -> float:
        pool = employees or self._employees
        if not pool:
            return 0.0
        return statistics.median(e.compensation() for e in pool)

    def compensation_stdev(self, employees: list[Employee] | None = None) -> float:
        pool = employees or self._employees
        if len(pool) < 2:
            return 0.0
        return statistics.stdev(e.compensation() for e in pool)

    # ── Групування ────────────────────────────────────────────

    def by_department(self) -> dict[str, list[Employee]]:
        result: dict[str, list[Employee]] = defaultdict(list)
        for emp in self._employees:
            result[emp.department].append(emp)
        return dict(result)

    def by_role(self) -> dict[str, list[Employee]]:
        result: dict[str, list[Employee]] = defaultdict(list)
        for emp in self._employees:
            result[emp.role].append(emp)
        return dict(result)

    # ── Звіти ─────────────────────────────────────────────────

    def department_stats(self) -> list[DepartmentStats]:
        result = []
        for dept, emps in self.by_department().items():
            comps = [e.compensation() for e in emps]
            roles: dict[str, int] = defaultdict(int)
            for e in emps:
                roles[e.role] += 1
            result.append(DepartmentStats(
                department=dept,
                count=len(emps),
                avg_compensation=round(statistics.mean(comps), 2),
                total_compensation=round(sum(comps), 2),
                min_compensation=round(min(comps), 2),
                max_compensation=round(max(comps), 2),
                median_compensation=round(statistics.median(comps), 2),
                roles_breakdown=dict(roles),
            ))
        return sorted(result, key=lambda s: s.avg_compensation, reverse=True)

    def role_stats(self) -> dict[str, dict]:
        result = {}
        for role, emps in self.by_role().items():
            comps = [e.compensation() for e in emps]
            result[role] = {
                "count": len(emps),
                "avg": round(statistics.mean(comps), 2),
                "min": round(min(comps), 2),
                "max": round(max(comps), 2),
                "total": round(sum(comps), 2),
            }
        return result

    def top_earners(self, n: int = 5) -> list[Employee]:
        return sorted(self._employees, key=lambda e: e.compensation(), reverse=True)[:n]

    def bottom_earners(self, n: int = 5) -> list[Employee]:
        return sorted(self._employees, key=lambda e: e.compensation())[:n]

    def compensation_percentile(self, percentile: float) -> float:
        """Обчислює p-й перцентиль зарплат (0..100)."""
        comps = sorted(e.compensation() for e in self._employees)
        if not comps:
            return 0.0
        idx = (percentile / 100) * (len(comps) - 1)
        lower = int(idx)
        upper = min(lower + 1, len(comps) - 1)
        return round(comps[lower] + (comps[upper] - comps[lower]) * (idx - lower), 2)

    def salary_distribution_buckets(self, buckets: int = 5) -> dict[str, int]:
        """Розподіл зарплат по рівних інтервалах."""
        comps = [e.compensation() for e in self._employees]
        if not comps:
            return {}
        lo, hi = min(comps), max(comps)
        step = (hi - lo) / buckets if hi != lo else 1
        dist: dict[str, int] = {}
        for i in range(buckets):
            low = lo + i * step
            high = low + step
            label = f"{int(low):,}–{int(high):,}"
            dist[label] = sum(1 for c in comps if low <= c < high)
        return dist
