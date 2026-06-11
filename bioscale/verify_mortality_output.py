import pandas as pd

# Verify mortality-augmented file
df_mort = pd.read_parquet("data/processed/nhanes_1999_2002_with_mortality.parquet")

print("Mortality-augmented dataset:")
print(f"Shape: {df_mort.shape}")
print(f"\nColumns: {df_mort.columns.tolist()}")
print(f"\nKey statistics:")
print(f"  - SEQN unique: {df_mort['SEQN'].nunique()}")
print(f"  - Cycles: {df_mort['cycle'].unique()}")
print(f"  - duration_months: {df_mort['duration_months'].notna().sum()} non-null")
print(f"    Min: {df_mort['duration_months'].min()}, Max: {df_mort['duration_months'].max()}")
print(f"  - event (MORTSTAT): {df_mort['event'].notna().sum()} non-null")
if df_mort['event'].notna().sum() > 0:
    print(f"    Unique values: {df_mort['event'].unique()}")

# Compare with model input file
df_model = pd.read_parquet("data/processed/nhanes_1999_2002_model_input.parquet")
print(f"\nModel input dataset (for comparison):")
print(f"Shape: {df_model.shape}")
print(f"Has duration_months: {'duration_months' in df_model.columns}")
print(f"Has event: {'event' in df_model.columns}")

# Show sample records
print(f"\nSample records from mortality-augmented dataset:")
cols_to_show = ['SEQN', 'cycle', 'RIDAGEYR', 'BMXBMI', 'duration_months', 'event']
available_cols = [c for c in cols_to_show if c in df_mort.columns]
print(df_mort[available_cols].head(10))
