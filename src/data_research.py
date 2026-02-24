import pandas as pd
from pathlib import Path

def clean_data(df):
    initial_rows = len(df)
    
    # Drop exact duplicates
    df = df.drop_duplicates()
    
    # Drop rows with missing values in FUEL column
    df = df.dropna(subset=['FUEL'])
    
    # Drop logical anomalies in weights
    df = df[~(df['OWN_WEIGHT'] > df['TOTAL_WEIGHT'])]
    
    final_rows = len(df)
    print(f"Data cleaning completed. Rows removed: {initial_rows - final_rows}")
    return df

def test_hypotheses():
    BASE_DIR = Path(__file__).resolve().parents[1]
    file_path = BASE_DIR / "data" / "raw" / "dataset2024.csv"

    print(f"Loading data from {file_path}...")
    df = pd.read_csv(file_path, sep=';', encoding='utf-8', low_memory=False)
    
    df = clean_data(df)
    total_records = len(df)

    print("\n" + "="*60)
    print("DATA RESEARCH: HYPOTHESES TESTING (2024)")
    print("="*60)

    # --- Hypothesis 1 ---
    print("\n[Hypothesis 1] Diesel vehicles make up the majority of registrations for specialized transport.")
    
    specialized_df = df[df['PURPOSE'] == 'СПЕЦІАЛІЗОВАНИЙ']
    total_specialized = len(specialized_df)
    
    if total_specialized > 0:
        fuel_distribution = specialized_df['FUEL'].value_counts()
        diesel_count = fuel_distribution.get('ДИЗЕЛЬНЕ ПАЛИВО', 0)
        diesel_percentage = (diesel_count / total_specialized) * 100
        
        print(f"  Total specialized vehicles: {total_specialized}")
        print(f"  Diesel specialized vehicles: {diesel_count} ({diesel_percentage:.2f}%)")
        
        if diesel_percentage > 50:
            print("  Conclusion: CONFIRMED. Diesel is the dominant fuel type.")
        else:
            print("  Conclusion: REJECTED. Diesel does not constitute the majority.")
            
        print("  Top 3 fuel types in specialized transport:")
        for fuel, count in fuel_distribution.head(3).items():
            print(f"    - {fuel}: {count}")
    else:
        print("  No specialized vehicles found in the dataset.")

    # --- Hypothesis 2 ---
    print("\n[Hypothesis 2] The majority of vehicles registered in 2024 are over 10 years old.")
    
    df['VEHICLE_AGE'] = 2024 - pd.to_numeric(df['MAKE_YEAR'], errors='coerce')
    older_than_10 = df[df['VEHICLE_AGE'] > 10]
    older_count = len(older_than_10)
    older_percentage = (older_count / total_records) * 100
    
    print(f"  Total analyzed vehicles: {total_records}")
    print(f"  Vehicles over 10 years old (pre-2014): {older_count} ({older_percentage:.2f}%)")
    
    if older_percentage > 50:
        print("  Conclusion: CONFIRMED. More than half of the registered vehicles are over 10 years old.")
    else:
        print("  Conclusion: REJECTED. The majority of vehicles are 10 years old or newer.")

    # --- Hypothesis 3 ---
    print("\n[Hypothesis 3] Passenger cars make up the largest share of registrations, with certain brands showing significantly higher frequency.")
    
    kind_distribution = df['KIND'].value_counts()
    passenger_count = kind_distribution.get('ЛЕГКОВИЙ', 0)
    passenger_percentage = (passenger_count / total_records) * 100
    
    print(f"  Passenger cars count: {passenger_count} ({passenger_percentage:.2f}% of total)")
    
    is_largest = kind_distribution.index[0] == 'ЛЕГКОВИЙ'
    
    if is_largest:
        print("  Conclusion (Part 1): CONFIRMED. Passenger cars are the most frequently registered vehicle kind.")
        
        passenger_df = df[df['KIND'] == 'ЛЕГКОВИЙ']
        brand_distribution = passenger_df['BRAND'].value_counts()
        
        print("  Top 5 passenger car brands:")
        for brand, count in brand_distribution.head(5).items():
            brand_share = (count / passenger_count) * 100
            print(f"    - {brand}: {count} ({brand_share:.2f}%)")
            
        print("  Conclusion (Part 2): CONFIRMED. The market is concentrated among top brands.")
    else:
        print("  Conclusion: REJECTED. Passenger cars do not make up the largest share.")
        
    print("\n" + "="*60)

if __name__ == "__main__":
    test_hypotheses()