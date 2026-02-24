import requests
from pathlib import Path
import zipfile

DATA_URL = "https://data.gov.ua/dataset/0ffd8b75-0628-48cc-952a-9302f9799ec0/resource/c3ffecc4-bb5c-4102-b761-6dcfeb60b4fe/download/reestrtz2024.zip"
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)

ZIP_FILE_NAME = "dataset2024.zip"
ZIP_FILE_PATH = DATA_DIR / ZIP_FILE_NAME
CSV_FILE_NAME = "dataset2024.csv"
CSV_FILE_PATH = DATA_DIR / CSV_FILE_NAME

def download_dataset(url: str, path: Path):
    try:
        print(f"Downloading dataset from {url} ...")
        with requests.get(url, stream=True, timeout=60) as response:
            response.raise_for_status()
            with open(path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        print(f"Dataset successfully saved to {path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading data: {e}")


def unzip_dataset(zip_path: Path, csv_path: Path):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            csv_files = [f for f in zip_ref.namelist() if f.endswith(".csv")]
            if not csv_files:
                print("No CSV file found in the zip archive!")
                return
            with zip_ref.open(csv_files[0]) as source, open(csv_path, "wb") as target:
                target.write(source.read())
        print(f"CSV successfully extracted to {csv_path}")
    except zipfile.BadZipFile:
        print("Error: The file is not a valid zip archive")
    except Exception as e:
        print(f"Error extracting CSV: {e}")


if __name__ == "__main__":
    download_dataset(DATA_URL, ZIP_FILE_PATH)
    unzip_dataset(ZIP_FILE_PATH, CSV_FILE_PATH)