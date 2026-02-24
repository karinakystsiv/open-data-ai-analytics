# Data Quality Report: Vehicle Registrations (2024)

## 1. General Information
- Total records (rows): 2344544
- Total columns: 20

## 2. Duplicates Analysis
- Exact duplicate rows found: 5593
  - Recommendation: Apply `df.drop_duplicates()` during the data cleaning phase.

## 3. Missing Values (NaN) Analysis
- Total missing values in the entire dataset: 308049
- Missing values in critical columns (for hypotheses testing):
  - `BRAND`: 0 missing values
  - `MAKE_YEAR`: 0 missing values
  - `FUEL`: 86113 missing values
  - `KIND`: 0 missing values
  - `PURPOSE`: 0 missing values

## 4. Structural Anomalies & Logical Checks
- Negative values check:
  - `CAPACITY` < 0: 0 records
  - `OWN_WEIGHT` < 0: 0 records
  - `TOTAL_WEIGHT` < 0: 0 records
- Records where OWN_WEIGHT > TOTAL_WEIGHT: 2131
- Records with invalid MAKE_YEAR (< 1900 or > 2024): 0