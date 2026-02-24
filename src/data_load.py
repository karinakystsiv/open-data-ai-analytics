import requests
from pathlib import Path

DATA_URL = "https://data.gov.ua/dataset/06779371-308f-42d7-895e-5a39833375f0/resource/c3ffecc4-bb5c-4102-b761-6dcfeb60b4fe"
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)
FILE_NAME = "dataset2024.csv"
FILE_PATH = DATA_DIR / FILE_NAME

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

if __name__ == "__main__":
    download_dataset(DATA_URL, FILE_PATH)