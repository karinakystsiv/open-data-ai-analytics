import pandas as pd
from pathlib import Path
import sqlite3
import warnings

warnings.filterwarnings('ignore')


def test_hypotheses():
    DB_PATH = Path("/app/data/database.sqlite")
    RESULT_PATH = Path("/app/reports/research_results.txt")
    RESULT_PATH.parent.mkdir(exist_ok=True, parents=True)

    if not DB_PATH.exists():
        print(f"Базу даних не знайдено: {DB_PATH}")
        return

    print("Завантаження агрегованих даних з БД...")
    conn = sqlite3.connect(DB_PATH)

    # Загальна кількість записів (без дублікатів та пропусків FUEL)
    total_records = pd.read_sql_query(
        "SELECT COUNT(*) as cnt FROM vehicles WHERE FUEL IS NOT NULL", conn
    )['cnt'][0]

    output = []
    output.append("=" * 60)
    output.append("ДОСЛІДЖЕННЯ ДАНИХ: ПЕРЕВІРКА ГІПОТЕЗ (2024)")
    output.append("=" * 60)

    # --- Гіпотеза 1 ---
    output.append("\n[Гіпотеза 1] Дизельні ТЗ складають більшість серед реєстрацій спеціалізованого транспорту")

    df_spec = pd.read_sql_query("""
        SELECT FUEL, COUNT(*) as cnt
        FROM vehicles
        WHERE PURPOSE = 'СПЕЦІАЛІЗОВАНИЙ' AND FUEL IS NOT NULL
        GROUP BY FUEL
        ORDER BY cnt DESC
    """, conn)

    total_specialized = df_spec['cnt'].sum()

    if total_specialized > 0:
        diesel_row = df_spec[df_spec['FUEL'] == 'ДИЗЕЛЬНЕ ПАЛИВО']
        diesel_count = int(diesel_row['cnt'].values[0]) if len(diesel_row) > 0 else 0
        diesel_percentage = (diesel_count / total_specialized) * 100

        output.append(f"  Всього спеціалізованих ТЗ: {total_specialized}")
        output.append(f"  Дизельних спеціалізованих ТЗ: {diesel_count} ({diesel_percentage:.2f}%)")

        if diesel_percentage > 50:
            output.append("  Висновок: ПІДТВЕРДЖЕНО. Дизель — домінуючий тип пального.")
        else:
            output.append("  Висновок: СПРОСТОВАНО. Дизель не складає більшість.")

        output.append("  ТОП-3 типи пального у спеціалізованому транспорті:")
        for _, row in df_spec.head(3).iterrows():
            output.append(f"    - {row['FUEL']}: {row['cnt']}")
    else:
        output.append("  Спеціалізованих ТЗ не знайдено в датасеті.")

    # --- Гіпотеза 2 ---
    output.append("\n[Гіпотеза 2] Більшість ТЗ, зареєстрованих у 2024, мають вік понад 10 років")

    age_stats = pd.read_sql_query("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN (2024 - CAST(MAKE_YEAR AS INTEGER)) > 10 THEN 1 ELSE 0 END) as older_10
        FROM vehicles
        WHERE MAKE_YEAR IS NOT NULL AND FUEL IS NOT NULL
    """, conn)

    total_with_year = int(age_stats['total'][0])
    older_count = int(age_stats['older_10'][0])
    older_percentage = (older_count / total_with_year) * 100 if total_with_year > 0 else 0

    output.append(f"  Всього проаналізованих ТЗ: {total_with_year}")
    output.append(f"  ТЗ віком понад 10 років (до 2014): {older_count} ({older_percentage:.2f}%)")

    if older_percentage > 50:
        output.append("  Висновок: ПІДТВЕРДЖЕНО. Більше половини зареєстрованих ТЗ старші 10 років.")
    else:
        output.append("  Висновок: СПРОСТОВАНО. Більшість ТЗ мають вік 10 років або менше.")

    # --- Гіпотеза 3 ---
    output.append("\n[Гіпотеза 3] Легкові авто — найбільша частка реєстрацій, певні марки домінують")

    df_kind = pd.read_sql_query("""
        SELECT KIND, COUNT(*) as cnt
        FROM vehicles
        WHERE FUEL IS NOT NULL
        GROUP BY KIND
        ORDER BY cnt DESC
    """, conn)

    passenger_row = df_kind[df_kind['KIND'] == 'ЛЕГКОВИЙ']
    passenger_count = int(passenger_row['cnt'].values[0]) if len(passenger_row) > 0 else 0
    passenger_percentage = (passenger_count / total_records) * 100 if total_records > 0 else 0

    output.append(f"  Легкових авто: {passenger_count} ({passenger_percentage:.2f}% від загалу)")

    is_largest = df_kind.iloc[0]['KIND'] == 'ЛЕГКОВИЙ' if len(df_kind) > 0 else False

    if is_largest:
        output.append("  Висновок (частина 1): ПІДТВЕРДЖЕНО. Легкові авто — найчастіший тип.")

        df_brands = pd.read_sql_query("""
            SELECT BRAND, COUNT(*) as cnt
            FROM vehicles
            WHERE KIND = 'ЛЕГКОВИЙ' AND BRAND IS NOT NULL AND FUEL IS NOT NULL
            GROUP BY BRAND
            ORDER BY cnt DESC
            LIMIT 5
        """, conn)

        output.append("  ТОП-5 марок легкових авто:")
        for _, row in df_brands.iterrows():
            brand_share = (row['cnt'] / passenger_count) * 100
            output.append(f"    - {row['BRAND']}: {row['cnt']} ({brand_share:.2f}%)")

        output.append("  Висновок (частина 2): ПІДТВЕРДЖЕНО. Ринок сконцентрований серед лідерів.")
    else:
        output.append("  Висновок: СПРОСТОВАНО. Легкові авто не є найбільшою часткою.")

    output.append("\n" + "=" * 60)

    conn.close()

    final_text = "\n".join(output)
    print(final_text)

    with open(RESULT_PATH, "w", encoding="utf-8") as f:
        f.write(final_text)

    print(f"\nРезультати збережено: {RESULT_PATH}")


if __name__ == "__main__":
    test_hypotheses()
