import requests
from pathlib import Path
import zipfile
import pandas as pd
import sqlite3

DATA_URL = "https://data.gov.ua/dataset/0ffd8b75-0628-48cc-952a-9302f9799ec0/resource/c3ffecc4-bb5c-4102-b761-6dcfeb60b4fe/download/reestrtz2024.zip"

DATA_DIR = Path("/app/data")
RAW_DIR = DATA_DIR / "raw"
DB_PATH = DATA_DIR / "database.sqlite"
ZIP_PATH = RAW_DIR / "dataset2024.zip"
CSV_PATH = RAW_DIR / "dataset2024.csv"


def download_and_store():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    try:
        print(f"Завантаження датасету...")
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(DATA_URL, stream=True, timeout=120, headers=headers)
        response.raise_for_status()

        with open(ZIP_PATH, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"ZIP збережено: {ZIP_PATH}")

        # Розпакування CSV з архіву
        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
            csv_files = [f for f in zip_ref.namelist() if f.endswith(".csv")]
            if not csv_files:
                print("CSV файл не знайдено в архіві!")
                return
            with zip_ref.open(csv_files[0]) as source, open(CSV_PATH, "wb") as target:
                target.write(source.read())
        print(f"CSV розпаковано: {CSV_PATH}")

        # Імпорт у SQLite
        print("Імпортуємо дані в SQLite...")
        df = pd.read_csv(CSV_PATH, sep=';', encoding='utf-8', low_memory=False)

        conn = sqlite3.connect(DB_PATH)
        df.to_sql('vehicles', conn, if_exists='replace', index=False)
        conn.close()

        print(f"БД успішно створена: {DB_PATH} ({len(df)} записів)")

    except Exception as e:
        print(f"Помилка завантаження: {e}")


if __name__ == "__main__":
    download_and_store()