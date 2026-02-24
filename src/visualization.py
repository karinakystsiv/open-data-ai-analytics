import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def clean_data(df):
    df = df.drop_duplicates()
    df = df.dropna(subset=['FUEL'])
    df = df[~(df['OWN_WEIGHT'] > df['TOTAL_WEIGHT'])]
    return df

def create_visualizations():
    # 1. Setup paths
    BASE_DIR = Path(__file__).resolve().parents[1]
    file_path = BASE_DIR / "data" / "raw" / "dataset2024.csv"
    figures_dir = BASE_DIR / "reports" / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading data from {file_path}...")
    df = pd.read_csv(file_path, sep=';', encoding='utf-8', low_memory=False)
    df = clean_data(df)

    # Calculate vehicle age for Hypothesis 2
    df['VEHICLE_AGE'] = 2024 - pd.to_numeric(df['MAKE_YEAR'], errors='coerce')

    # Set visualization style
    sns.set_theme(style="whitegrid")
    
    # Optional: Configure font to support Cyrillic characters if needed by matplotlib
    # plt.rcParams['font.family'] = 'DejaVu Sans'

    print("Generating visualizations...")

    # --- Plot 1: Hypothesis 1 (Diesel in Specialized Transport) ---
    plt.figure(figsize=(10, 6))
    specialized_df = df[df['PURPOSE'] == 'СПЕЦІАЛІЗОВАНИЙ']
    fuel_counts = specialized_df['FUEL'].value_counts().head(3)
    
    sns.barplot(x=fuel_counts.values, y=fuel_counts.index, palette="viridis")
    plt.title("Top 3 Fuel Types in Specialized Transport (2024)", fontsize=14)
    plt.xlabel("Number of Registrations", fontsize=12)
    plt.ylabel("Fuel Type", fontsize=12)
    plt.tight_layout()
    plt.savefig(figures_dir / "h1_specialized_fuel.png", dpi=300)
    plt.close()
    print("- Saved: h1_specialized_fuel.png")

    # --- Plot 2: Hypothesis 2 (Vehicle Age Distribution) ---
    plt.figure(figsize=(10, 6))
    # Filter out extreme outliers for a cleaner histogram (e.g., age > 50)
    age_data = df[df['VEHICLE_AGE'] <= 50]['VEHICLE_AGE']
    
    sns.histplot(age_data, bins=30, kde=False, color="royalblue")
    # Add a red dashed line at 10 years to visually separate the groups
    plt.axvline(x=10, color='red', linestyle='--', linewidth=2, label='10 Years Threshold')
    
    plt.title("Distribution of Registered Vehicle Ages (2024)", fontsize=14)
    plt.xlabel("Vehicle Age (Years)", fontsize=12)
    plt.ylabel("Frequency", fontsize=12)
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / "h2_vehicle_age_distribution.png", dpi=300)
    plt.close()
    print("- Saved: h2_vehicle_age_distribution.png")

    # --- Plot 3: Hypothesis 3 (Top Brands among Passenger Cars) ---
    plt.figure(figsize=(12, 7))
    passenger_df = df[df['KIND'] == 'ЛЕГКОВИЙ']
    brand_counts = passenger_df['BRAND'].value_counts().head(10)
    
    sns.barplot(x=brand_counts.values, y=brand_counts.index, palette="mako")
    plt.title("Top 10 Passenger Car Brands Registered in 2024", fontsize=14)
    plt.xlabel("Number of Registrations", fontsize=12)
    plt.ylabel("Brand", fontsize=12)
    plt.tight_layout()
    plt.savefig(figures_dir / "h3_top_passenger_brands.png", dpi=300)
    plt.close()
    print("- Saved: h3_top_passenger_brands.png")

    print(f"\nAll visualizations successfully saved to: {figures_dir}")

if __name__ == "__main__":
    create_visualizations()