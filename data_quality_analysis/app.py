import pandas as pd
from pathlib import Path
import sqlite3


def analyze_data_quality():
    DB_PATH = Path("/app/data/database.sqlite")
    REPORT_PATH = Path("/app/reports/data_quality_report.md")
    REPORT_PATH.parent.mkdir(exist_ok=True, parents=True)

    if not DB_PATH.exists():
        print(f"Базу даних не знайдено: {DB_PATH}")
        return

    print(f"Читання даних з бази: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)

    # Загальна кількість записів
    total_rows = pd.read_sql_query("SELECT COUNT(*) as cnt FROM vehicles", conn)['cnt'][0]
    columns = pd.read_sql_query("PRAGMA table_info(vehicles)", conn)['name'].tolist()

    report = ["# Звіт про якість даних: Реєстрація ТЗ (2024)\n"]

    # 1. Загальна інформація
    report.append("## 1. Загальна інформація")
    report.append(f"- **Кількість записів (рядків):** {total_rows}")
    report.append(f"- **Кількість колонок:** {len(columns)}")

    # Таблиця статистики — рахуємо через SQL
    stats_table = "| Колонка | Заповненість | Унікальних значень |\n|---|---|---|"
    for col in columns:
        non_null = pd.read_sql_query(
            f'SELECT COUNT("{col}") as cnt FROM vehicles WHERE "{col}" IS NOT NULL', conn
        )['cnt'][0]
        unique = pd.read_sql_query(
            f'SELECT COUNT(DISTINCT "{col}") as cnt FROM vehicles', conn
        )['cnt'][0]
        stats_table += f"\n| {col} | {non_null}/{total_rows} | {unique} |"
    report.append(stats_table)

    # 2. Аналіз дублікатів
    report.append("\n## 2. Аналіз дублікатів")
    distinct_rows = pd.read_sql_query("SELECT COUNT(*) as cnt FROM (SELECT DISTINCT * FROM vehicles)", conn)['cnt'][0]
    duplicates = total_rows - distinct_rows
    report.append(f"- Точних дублікатів знайдено: **{duplicates}**")
    if duplicates > 0:
        report.append("  - Рекомендація: застосувати `df.drop_duplicates()` під час очищення.")

    # 3. Аналіз пропусків
    report.append("\n## 3. Аналіз пропущених значень (NaN)")
    total_missing = 0
    for col in columns:
        null_count = pd.read_sql_query(
            f'SELECT COUNT(*) as cnt FROM vehicles WHERE "{col}" IS NULL OR "{col}" = ""', conn
        )['cnt'][0]
        total_missing += null_count
    report.append(f"- Загальна кількість пропусків у датасеті: **{total_missing}**")

    critical_cols = ['BRAND', 'MAKE_YEAR', 'FUEL', 'KIND', 'PURPOSE']
    report.append("- Пропуски у критичних колонках:")
    for col in critical_cols:
        if col in columns:
            missing_count = pd.read_sql_query(
                f'SELECT COUNT(*) as cnt FROM vehicles WHERE "{col}" IS NULL OR "{col}" = ""', conn
            )['cnt'][0]
            report.append(f"  - `{col}`: {missing_count} пропусків")

    # 4. Структурні аномалії
    report.append("\n## 4. Структурні аномалії та логічні перевірки")

    numeric_cols = ['CAPACITY', 'OWN_WEIGHT', 'TOTAL_WEIGHT']
    report.append("- Перевірка від'ємних значень:")
    for col in numeric_cols:
        if col in columns:
            negative_count = pd.read_sql_query(
                f'SELECT COUNT(*) as cnt FROM vehicles WHERE CAST("{col}" AS REAL) < 0', conn
            )['cnt'][0]
            report.append(f"  - `{col}` < 0: {negative_count} записів")

    if 'OWN_WEIGHT' in columns and 'TOTAL_WEIGHT' in columns:
        invalid_weight = pd.read_sql_query(
            'SELECT COUNT(*) as cnt FROM vehicles WHERE CAST(OWN_WEIGHT AS REAL) > CAST(TOTAL_WEIGHT AS REAL) AND OWN_WEIGHT IS NOT NULL AND TOTAL_WEIGHT IS NOT NULL',
            conn
        )['cnt'][0]
        report.append(f"- Записи де OWN_WEIGHT > TOTAL_WEIGHT: **{invalid_weight}**")

    if 'MAKE_YEAR' in columns:
        invalid_years = pd.read_sql_query(
            'SELECT COUNT(*) as cnt FROM vehicles WHERE CAST(MAKE_YEAR AS INTEGER) < 1900 OR CAST(MAKE_YEAR AS INTEGER) > 2024',
            conn
        )['cnt'][0]
        report.append(f"- Записи з некоректним MAKE_YEAR (< 1900 або > 2024): **{invalid_years}**")

    conn.close()

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(report))

    print(f"Звіт про якість даних збережено: {REPORT_PATH}")


if __name__ == "__main__":
    analyze_data_quality()
