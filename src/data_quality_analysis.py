import pandas as pd
from pathlib import Path

def analyze_data_quality():
    # Dynamic path resolution based on the script's location
    BASE_DIR = Path(__file__).resolve().parents[1]
    
    # Define file paths using BASE_DIR
    file_path = BASE_DIR / "data" / "raw" / "dataset2024.csv"
    report_path = BASE_DIR / "reports" / "data_quality_report.md"
    
    # Ensure the reports directory exists
    report_path.parent.mkdir(exist_ok=True, parents=True)

    report = ["# Data Quality Report: Vehicle Registrations (2024)\n"]

    print(f"Reading data from {file_path}...")
    df = pd.read_csv(file_path, sep=';', encoding='utf-8', low_memory=False)

    # 1. Basic Dataset Information
    report.append("## 1. General Information")
    report.append(f"- Total records (rows): {df.shape[0]}")
    report.append(f"- Total columns: {df.shape[1]}")

    # 2. Duplicates Check
    report.append("\n## 2. Duplicates Analysis")
    duplicates = df.duplicated().sum()
    report.append(f"- Exact duplicate rows found: {duplicates}")
    if duplicates > 0:
        report.append("  - Recommendation: Apply `df.drop_duplicates()` during the data cleaning phase.")

    # 3. Missing Values Check
    report.append("\n## 3. Missing Values (NaN) Analysis")
    total_missing = df.isnull().sum().sum()
    report.append(f"- Total missing values in the entire dataset: {total_missing}")
    
    critical_cols = ['BRAND', 'MAKE_YEAR', 'FUEL', 'KIND', 'PURPOSE']
    report.append("- Missing values in critical columns (for hypotheses testing):")
    for col in critical_cols:
        missing_count = df[col].isnull().sum()
        report.append(f"  - `{col}`: {missing_count} missing values")

    # 4. Numeric Anomalies and Negative Values Check
    report.append("\n## 4. Structural Anomalies & Logical Checks")
    
    # Check for negative values
    numeric_cols = ['CAPACITY', 'OWN_WEIGHT', 'TOTAL_WEIGHT']
    report.append("- Negative values check:")
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        negative_count = (df[col] < 0).sum()
        report.append(f"  - `{col}` < 0: {negative_count} records")

    # Logical check for weights
    invalid_weight = df[df['OWN_WEIGHT'] > df['TOTAL_WEIGHT']]
    report.append(f"- Records where OWN_WEIGHT > TOTAL_WEIGHT: {len(invalid_weight)}")

    # Year check (assuming data is for 2024)
    df['MAKE_YEAR'] = pd.to_numeric(df['MAKE_YEAR'], errors='coerce')
    invalid_years = df[(df['MAKE_YEAR'] < 1900) | (df['MAKE_YEAR'] > 2024)]
    report.append(f"- Records with invalid MAKE_YEAR (< 1900 or > 2024): {len(invalid_years)}")

    # Save the report
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    
    print(f"Data quality report saved to {report_path}")

if __name__ == "__main__":
    analyze_data_quality()