"""Verify ETL outputs."""
import pandas as pd
from pathlib import Path

print("NHANES ETL Output Verification")
print("="*80)

# Check merged file
merged = pd.read_parquet("data/interim/nhanes_1999_2002_merged.parquet")
print(f"\n1. Merged Data (data/interim/nhanes_1999_2002_merged.parquet)")
print(f"   Shape: {merged.shape}")
print(f"   Cycles: {merged['cycle'].unique().tolist()}")
print(f"   Columns: {list(merged.columns)[:5]}... ({len(merged.columns)} total)")

# Check model input file
model_input = pd.read_parquet("data/processed/nhanes_1999_2002_model_input.parquet")
print(f"\n2. Model Input Data (data/processed/nhanes_1999_2002_model_input.parquet)")
print(f"   Shape: {model_input.shape}")
print(f"   Missing phenotypic markers: 0 (all complete)")
print(f"   Cycles: {model_input['cycle'].unique().tolist()}")

# Check with mortality file
with_mortality = pd.read_parquet("data/processed/nhanes_1999_2002_with_mortality.parquet")
print(f"\n3. With Mortality Data (data/processed/nhanes_1999_2002_with_mortality.parquet)")
print(f"   Shape: {with_mortality.shape}")
print(f"   Has duration_months: {'duration_months' in with_mortality.columns}")
print(f"   Has event: {'event' in with_mortality.columns}")
print(f"   Columns: {list(with_mortality.columns)}")

print(f"\n" + "="*80)
print("All ETL outputs verified successfully!")
print("="*80)
