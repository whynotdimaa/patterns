"""
Presentation Layer — звіти та графіки.
Використовує matplotlib для побудови візуалізацій.
"""

from __future__ import annotations
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path
from analytics import EmployeeAnalyticsService, DepartmentStats
from employees import Employee

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

PALETTE = {
    "Manager":      "#534AB7",
    "OfficeClerk":  "#0F6E56",
    "SalesManager": "#993C1D",
    "SysAdmin":     "#185FA5",
}
DEPT_COLORS = ["#534AB7", "#0F6E56", "#993C1D", "#185FA5", "#854F0B"]
FMT = lambda n: f"₴{n:,.0f}"


def _style():
    plt.rcParams.update({
        "font.family":       "DejaVu Sans",
        "axes.spines.top":   False,
        "axes.spines.right": False,
        "axes.grid":         True,
        "grid.alpha":        0.3,
        "grid.linestyle":    "--",
        "figure.facecolor":  "white",
        "axes.facecolor":    "#fafafa",
    })


# ──────────────────────────────────────────────────────────────
# 1. Bar: кількість співробітників по відділах
# ──────────────────────────────────────────────────────────────

def plot_headcount_by_department(service: EmployeeAnalyticsService,
                                  save: bool = True) -> Path:
    _style()
    dept_data = service.by_department()
    depts = list(dept_data.keys())
    counts = [len(dept_data[d]) for d in depts]
    colors = [DEPT_COLORS[i % len(DEPT_COLORS)] for i in range(len(depts))]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(depts, counts, color=colors, width=0.55, zorder=3)
    ax.bar_label(bars, labels=[str(c) for c in counts], padding=4, fontsize=11)
    ax.set_title("Кількість співробітників по відділах", fontsize=14, pad=12)
    ax.set_ylabel("Кількість осіб")
    ax.set_ylim(0, max(counts) * 1.25)
    fig.tight_layout()

    path = OUTPUT_DIR / "01_headcount_by_dept.png"
    if save:
        fig.savefig(path, dpi=150)
        plt.close(fig)
        print(f"[Chart] Збережено: {path}")
    return path


# ──────────────────────────────────────────────────────────────
# 2. Horizontal bar: середня зарплата по відділах
# ──────────────────────────────────────────────────────────────

def plot_avg_salary_by_department(service: EmployeeAnalyticsService,
                                   save: bool = True) -> Path:
    _style()
    stats = service.department_stats()
    depts = [s.department for s in stats]
    avgs  = [s.avg_compensation for s in stats]
    colors = [DEPT_COLORS[i % len(DEPT_COLORS)] for i in range(len(depts))]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(depts, avgs, color=colors, height=0.55, zorder=3)
    ax.bar_label(bars, labels=[FMT(v) for v in avgs], padding=6, fontsize=10)
    ax.set_title("Середня зарплата по відділах (₴/міс)", fontsize=14, pad=12)
    ax.set_xlabel("Середня зарплата (₴)")
    ax.set_xlim(0, max(avgs) * 1.2)
    ax.invert_yaxis()
    fig.tight_layout()

    path = OUTPUT_DIR / "02_avg_salary_by_dept.png"
    if save:
        fig.savefig(path, dpi=150)
        plt.close(fig)
        print(f"[Chart] Збережено: {path}")
    return path


# ──────────────────────────────────────────────────────────────
# 3. Pie: розподіл за ролями
# ──────────────────────────────────────────────────────────────

def plot_role_distribution(service: EmployeeAnalyticsService,
                            save: bool = True) -> Path:
    _style()
    by_role = service.by_role()
    roles  = list(by_role.keys())
    counts = [len(by_role[r]) for r in roles]
    colors = [PALETTE.get(r, "#888") for r in roles]

    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax.pie(
        counts, labels=None, colors=colors,
        autopct="%1.1f%%", startangle=140,
        pctdistance=0.75,
        wedgeprops={"edgecolor": "white", "linewidth": 2},
    )
    for at in autotexts:
        at.set_fontsize(11)
        at.set_color("white")
        at.set_fontweight("bold")

    legend_labels = [f"{r} ({c} ос.)" for r, c in zip(roles, counts)]
    ax.legend(wedges, legend_labels, loc="lower center",
              bbox_to_anchor=(0.5, -0.12), ncol=2, fontsize=10,
              frameon=False)
    ax.set_title("Розподіл співробітників за ролями", fontsize=14, pad=16)
    fig.tight_layout()

    path = OUTPUT_DIR / "03_role_distribution.png"
    if save:
        fig.savefig(path, dpi=150)
        plt.close(fig)
        print(f"[Chart] Збережено: {path}")
    return path


# ──────────────────────────────────────────────────────────────
# 4. Grouped bar: мін/сер/макс зарплата по відділах
# ──────────────────────────────────────────────────────────────

def plot_salary_range_by_department(service: EmployeeAnalyticsService,
                                     save: bool = True) -> Path:
    _style()
    stats = service.department_stats()
    depts = [s.department for s in stats]
    mins  = [s.min_compensation for s in stats]
    avgs  = [s.avg_compensation  for s in stats]
    maxs  = [s.max_compensation  for s in stats]

    x  = np.arange(len(depts))
    w  = 0.25
    fig, ax = plt.subplots(figsize=(11, 5))

    b1 = ax.bar(x - w, mins, w, label="Мін",   color="#AFA9EC", zorder=3)
    b2 = ax.bar(x,     avgs, w, label="Сер.",  color="#534AB7", zorder=3)
    b3 = ax.bar(x + w, maxs, w, label="Макс",  color="#26215C", zorder=3)

    ax.set_xticks(x)
    ax.set_xticklabels(depts)
    ax.set_title("Діапазон зарплат по відділах (₴/міс)", fontsize=14, pad=12)
    ax.set_ylabel("Зарплата (₴)")
    ax.legend(frameon=False)
    fig.tight_layout()

    path = OUTPUT_DIR / "04_salary_range.png"
    if save:
        fig.savefig(path, dpi=150)
        plt.close(fig)
        print(f"[Chart] Збережено: {path}")
    return path


# ──────────────────────────────────────────────────────────────
# 5. Stacked bar: склад відділів за ролями
# ──────────────────────────────────────────────────────────────

def plot_role_composition_by_department(service: EmployeeAnalyticsService,
                                         save: bool = True) -> Path:
    _style()
    dept_data = service.by_department()
    all_roles = list(PALETTE.keys())
    depts = list(dept_data.keys())

    role_counts = {role: [] for role in all_roles}
    for dept in depts:
        role_map = {e.role: 0 for e in dept_data[dept]}
        for e in dept_data[dept]:
            role_map[e.role] = role_map.get(e.role, 0) + 1
        for role in all_roles:
            role_counts[role].append(role_map.get(role, 0))

    fig, ax = plt.subplots(figsize=(11, 5))
    bottom = np.zeros(len(depts))
    for role in all_roles:
        vals = np.array(role_counts[role])
        ax.bar(depts, vals, bottom=bottom, label=role,
               color=PALETTE[role], zorder=3)
        bottom += vals

    ax.set_title("Склад відділів за ролями", fontsize=14, pad=12)
    ax.set_ylabel("Кількість осіб")
    ax.legend(frameon=False, loc="upper right")
    fig.tight_layout()

    path = OUTPUT_DIR / "05_role_composition.png"
    if save:
        fig.savefig(path, dpi=150)
        plt.close(fig)
        print(f"[Chart] Збережено: {path}")
    return path


# ──────────────────────────────────────────────────────────────
# 6. Текстовий звіт
# ──────────────────────────────────────────────────────────────

def print_full_report(employees: list[Employee],
                      service: EmployeeAnalyticsService) -> None:
    SEP = "─" * 72
    print(f"\n{'═' * 72}")
    print("  ЗВІТ ПО ПЕРСОНАЛУ ПІДПРИЄМСТВА")
    print(f"{'═' * 72}\n")

    print(f"  Всього співробітників : {len(employees)}")
    print(f"  Загальний ФОП         : {FMT(service.total_compensation())}/міс")
    print(f"  Середня зарплата      : {FMT(service.average_compensation())}/міс")
    print(f"  Медіана зарплат       : {FMT(service.median_compensation())}/міс")
    print(f"  Стандартне відхилення : {FMT(service.compensation_stdev())}")
    print(f"  P25 / P75             : {FMT(service.compensation_percentile(25))} / "
          f"{FMT(service.compensation_percentile(75))}")
    print()

    print(SEP)
    print("  СТАТИСТИКА ПО ВІДДІЛАХ")
    print(SEP)
    for s in service.department_stats():
        print(f"\n  {s.department}")
        print(f"    Осіб     : {s.count}")
        print(f"    Сер.зп   : {FMT(s.avg_compensation)}")
        print(f"    ФОП      : {FMT(s.total_compensation)}")
        print(f"    Мін–Макс : {FMT(s.min_compensation)} – {FMT(s.max_compensation)}")
        rb = ", ".join(f"{r}: {c}" for r, c in s.roles_breakdown.items())
        print(f"    Ролі     : {rb}")

    print(f"\n{SEP}")
    print("  СТАТИСТИКА ПО РОЛЯХ")
    print(SEP)
    for role, st in service.role_stats().items():
        print(f"\n  {role}")
        print(f"    Осіб : {st['count']}")
        print(f"    Сер. : {FMT(st['avg'])}")
        print(f"    Мін  : {FMT(st['min'])}   Макс : {FMT(st['max'])}")

    print(f"\n{SEP}")
    print("  ТОП-5 НАЙВИЩИХ ЗАРПЛАТ")
    print(SEP)
    for i, e in enumerate(service.top_earners(5), 1):
        print(f"  {i}. {e.name:<25} {e.role:<14} {e.department:<14} {FMT(e.compensation())}")

    print(f"\n{SEP}")
    print("  РОЗПОДІЛ ЗАРПЛАТ (BUCKETS)")
    print(SEP)
    for bucket, cnt in service.salary_distribution_buckets().items():
        bar = "█" * cnt
        print(f"  {bucket:>20}  {bar:<20} {cnt}")

    print(f"\n{'═' * 72}\n")
