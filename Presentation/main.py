"""
main.py — Точка входу програми.

СТРУКТУРА ПРОЄКТУ (всі файли в одній папці):
  employee/
  ├── main.py
  ├── singleton.py
  ├── builder.py
  ├── factory.py
  ├── prototype.py
  ├── employees.py
  ├── repository.py
  ├── analytics.py
  ├── charts.py
  └── requirements.txt
"""

import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from Infrastructure.singleton import ConnectionRegistry
from Infrastructure.builder import ConnectionBuilder
from Infrastructure.factory import DBConnectionFactory
from Application.prototype import EmployeePrototypeRegistry
from Application.repository import EmployeeRepository
from Application.analytics import EmployeeAnalyticsService
from Presentation.charts import (
    plot_headcount_by_department,
    plot_avg_salary_by_department,
    plot_role_distribution,
    plot_salary_range_by_department,
    plot_role_composition_by_department,
    print_full_report,
)


# ══════════════════════════════════════════════════════════════
# 1. SINGLETON — реєстр підключень
# ══════════════════════════════════════════════════════════════
registry  = ConnectionRegistry()
registry2 = ConnectionRegistry()
assert registry is registry2, "Singleton порушено!"
print("[Singleton] ConnectionRegistry — той самий об'єкт:", id(registry))

# PostgreSQL (Engineering)
pg_config = (ConnectionBuilder()
             .set_type("postgresql")
             .set_host("localhost")
             .set_port(5432)
             .set_database("postgres")
             .set_credentials("postgres", "123 ")
             .build())

# Redis (Marketing)
redis_config = (ConnectionBuilder()
                .set_type("redis")
                .set_host("localhost")
                .set_port(6379)
                .set_option("db", 0)
                .build())
excel_config = (ConnectionBuilder()
                .set_type("excel")
                .set_option("file_path", "data/Finance.xlsx")
                .set_option("sheet_name", "Employees")
                .build())

registry.register("PostgreSQL (Engineering)", pg_config)
registry.register("Redis (Marketing)",        redis_config)
registry.register("Excel (Finance)",          excel_config)

# ══════════════════════════════════════════════════════════════
# 3. FACTORY — отримуємо дані з трьох БД
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 60)
print("[Factory] Завантаження даних з баз даних...")
print("─" * 60)

db_employees = []
for conn_name in registry.all_names():
    cfg  = registry.get(conn_name)
    conn = DBConnectionFactory.create(cfg)
    repo = EmployeeRepository(conn)
    emps = repo.get_all()
    db_employees.extend(emps)
    print(f"  {conn_name}: отримано {len(emps)} записів")

# ══════════════════════════════════════════════════════════════
# 4. PROTOTYPE — створюємо два нові відділи клонуванням
# ══════════════════════════════════════════════════════════════
print("\n[Prototype] Створення відділів HR та R&D через клонування прототипів...")

hr_dept = [
    EmployeePrototypeRegistry.clone("Manager",
        id=18, name="Larysa Bondar",      department="HR",
        base_salary=4600.0, bonus=0.15),
    EmployeePrototypeRegistry.clone("OfficeClerk",
        id=19, name="Halyna Savych",      department="HR",
        hourly_rate=21.0, hours_per_month=168),
    EmployeePrototypeRegistry.clone("OfficeClerk",
        id=20, name="Petro Semenko",      department="HR",
        hourly_rate=19.0, hours_per_month=176),
    EmployeePrototypeRegistry.clone("SalesManager",
        id=21, name="Zoryana Prokopenko", department="HR",
        base_salary=2500.0, commission_rate=0.03, monthly_sales=40_000),
    EmployeePrototypeRegistry.clone("SysAdmin",
        id=22, name="Dmytro Volkov",      department="HR",
        base_salary=4100.0, on_call_hours=25, on_call_rate=26.0),
]

rnd_dept = [
    EmployeePrototypeRegistry.clone("Manager",
        id=23, name="Orest Kovalchuk",   department="R&D",
        base_salary=6000.0, bonus=0.30),
    EmployeePrototypeRegistry.clone("Manager",
        id=24, name="Vira Sydorenko",    department="R&D",
        base_salary=5800.0, bonus=0.28),
    EmployeePrototypeRegistry.clone("SysAdmin",
        id=25, name="Artem Bilyk",       department="R&D",
        base_salary=5000.0, on_call_hours=60, on_call_rate=35.0),
    EmployeePrototypeRegistry.clone("SysAdmin",
        id=26, name="Nadiia Horbach",    department="R&D",
        base_salary=4800.0, on_call_hours=55, on_call_rate=33.0),
    EmployeePrototypeRegistry.clone("OfficeClerk",
        id=27, name="Taras Kryvenko",    department="R&D",
        hourly_rate=28.0, hours_per_month=168),
    EmployeePrototypeRegistry.clone("SalesManager",
        id=28, name="Olena Lysak",       department="R&D",
        base_salary=3500.0, commission_rate=0.08, monthly_sales=150_000),
]

print(f"  HR : {len(hr_dept)} співробітників")
print(f"  R&D: {len(rnd_dept)} співробітників")

# ══════════════════════════════════════════════════════════════
# 5. Об'єднуємо всі дані
# ══════════════════════════════════════════════════════════════
all_employees = db_employees + hr_dept + rnd_dept
print(f"\n[Main] Всього співробітників у системі: {len(all_employees)}")

# ══════════════════════════════════════════════════════════════
# 6. BUSINESS LOGIC — аналітика
# ══════════════════════════════════════════════════════════════
service = EmployeeAnalyticsService(all_employees)

# ══════════════════════════════════════════════════════════════
# 7. PRESENTATION — текстовий звіт + графіки
# ══════════════════════════════════════════════════════════════
print_full_report(all_employees, service)

print("[Charts] Генерація графіків...")
plot_headcount_by_department(service)
plot_avg_salary_by_department(service)
plot_role_distribution(service)
plot_salary_range_by_department(service)
plot_role_composition_by_department(service)

print("\n[Done] Всі графіки збережено у папці output/")

# ══════════════════════════════════════════════════════════════
# 8. Демонстрація розширюваності Factory (нова БД)
# ══════════════════════════════════════════════════════════════
print("\n[Factory] Демонстрація додавання нового типу БД (MongoDB)...")

from factory import DatabaseConnection

class MongoDBConnection(DatabaseConnection):
    def _connection_string(self):
        return f"mongodb://{self.config.get('host')}:{self.config.get('port')}"
    def fetch_employees(self):
        return []

DBConnectionFactory.register_type("mongodb", MongoDBConnection)
print(f"  Підтримувані типи БД: {DBConnectionFactory.supported_types()}")
