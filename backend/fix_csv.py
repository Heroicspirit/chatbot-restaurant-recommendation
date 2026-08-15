import pandas as pd
import os

# Load the CSV
csv_path = os.path.join(os.path.dirname(__file__), "../data/processed/restaurants_clean.csv")
df = pd.read_csv(csv_path)
print(f"Loaded CSV from: {csv_path}")

# Fix price_level: convert numbers to strings
def fix_price_level(val):
    if pd.isna(val):
        return "medium"
    if isinstance(val, (int, float)):
        if val <= 1:
            return "low"
        elif val == 2:
            return "medium"
        else:
            return "high"
    return str(val).lower()

df["price_level"] = df["price_level"].apply(fix_price_level)

# Fix veg_available: convert strings to boolean and add serves_both field
def fix_veg_available(val):
    if pd.isna(val):
        return False, False
    if isinstance(val, bool):
        return val, False
    val_str = str(val).lower()
    if val_str in ["true", "yes", "veg", "veg_only", "vegetarian"]:
        return True, False
    if val_str in ["veg_and_non_veg", "both", "non_veg_and_veg"]:
        return True, True  # Serves both
    return False, False

# Apply the fix and create two columns
df["veg_available"], df["serves_both"] = zip(*df["veg_available"].apply(fix_veg_available))

# Save the fixed CSV to a temp file first
output_path = os.path.join(os.path.dirname(__file__), "../data/processed/restaurants_clean_fixed.csv")
df.to_csv(output_path, index=False)
print(f"Fixed {len(df)} rows")
print(f"Saved to: {output_path}")
print("price_level values:", df["price_level"].value_counts().to_dict())
print("veg_available values:", df["veg_available"].value_counts().to_dict())
print("\nManually replace restaurants_clean.csv with restaurants_clean_fixed.csv")
