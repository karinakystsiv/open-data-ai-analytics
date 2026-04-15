import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
from pathlib import Path


def run_visualization():
    DB_PATH = Path("/app/data/database.sqlite")
    OUTPUT_PATH = Path("/app/reports/figures")
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    if not DB_PATH.exists():
        print(f"Базу даних не знайдено: {DB_PATH}")
        return

    print("Завантаження даних з БД для візуалізації...")
    conn = sqlite3.connect(DB_PATH)

    sns.set_theme(style="whitegrid")
    print("Генерація візуалізацій...")

    # --- Графік 1: Гіпотеза 1 (Дизель у спеціалізованому транспорті) ---
    # Агрегуємо на рівні SQL — не тягнемо весь датасет у пам'ять
    df_fuel = pd.read_sql_query("""
        SELECT FUEL, COUNT(*) as cnt
        FROM vehicles
        WHERE PURPOSE = 'СПЕЦІАЛІЗОВАНИЙ' AND FUEL IS NOT NULL
        GROUP BY FUEL
        ORDER BY cnt DESC
        LIMIT 5
    """, conn)

    plt.figure(figsize=(10, 6))
    sns.barplot(x='cnt', y='FUEL', data=df_fuel, palette="viridis")
    plt.title("ТОП-5 типів пального у спеціалізованому транспорті (2024)", fontsize=14)
    plt.xlabel("Кількість реєстрацій", fontsize=12)
    plt.ylabel("Тип пального", fontsize=12)
    plt.tight_layout()

    file1 = OUTPUT_PATH / "h1_specialized_fuel.png"
    plt.savefig(file1, dpi=150)
    plt.close()
    print(f"- Збережено: {file1}")

    # --- Графік 2: Гіпотеза 2 (Розподіл віку ТЗ) ---
    # Обчислюємо вік та групуємо на рівні SQL
    df_age = pd.read_sql_query("""
        SELECT (2024 - CAST(MAKE_YEAR AS INTEGER)) as VEHICLE_AGE, COUNT(*) as cnt
        FROM vehicles
        WHERE MAKE_YEAR IS NOT NULL
          AND CAST(MAKE_YEAR AS INTEGER) >= 1974
          AND CAST(MAKE_YEAR AS INTEGER) <= 2024
        GROUP BY VEHICLE_AGE
        ORDER BY VEHICLE_AGE
    """, conn)

    plt.figure(figsize=(10, 6))
    plt.bar(df_age['VEHICLE_AGE'], df_age['cnt'], color="royalblue", width=0.8)
    plt.axvline(x=10, color='red', linestyle='--', linewidth=2, label='Поріг 10 років')
    plt.title("Розподіл віку зареєстрованих ТЗ (2024)", fontsize=14)
    plt.xlabel("Вік ТЗ (роки)", fontsize=12)
    plt.ylabel("Частота", fontsize=12)
    plt.legend()
    plt.tight_layout()

    file2 = OUTPUT_PATH / "h2_vehicle_age_distribution.png"
    plt.savefig(file2, dpi=150)
    plt.close()
    print(f"- Збережено: {file2}")

    # --- Графік 3: Гіпотеза 3 (ТОП марки легкових авто) ---
    df_brands = pd.read_sql_query("""
        SELECT BRAND, COUNT(*) as cnt
        FROM vehicles
        WHERE KIND = 'ЛЕГКОВИЙ' AND BRAND IS NOT NULL
        GROUP BY BRAND
        ORDER BY cnt DESC
        LIMIT 10
    """, conn)

    plt.figure(figsize=(12, 7))
    sns.barplot(x='cnt', y='BRAND', data=df_brands, palette="mako")
    plt.title("ТОП-10 марок легкових авто, зареєстрованих у 2024", fontsize=14)
    plt.xlabel("Кількість реєстрацій", fontsize=12)
    plt.ylabel("Марка", fontsize=12)
    plt.tight_layout()

    file3 = OUTPUT_PATH / "h3_top_passenger_brands.png"
    plt.savefig(file3, dpi=150)
    plt.close()
    print(f"- Збережено: {file3}")

    conn.close()
    print(f"\nВсі візуалізації збережено у: {OUTPUT_PATH}")


if __name__ == "__main__":
    run_visualization()
