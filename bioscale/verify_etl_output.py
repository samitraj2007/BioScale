#!/usr/bin/env python
"""Quick verification of NHANES ETL output."""

import pandas as pd

df = pd.read_parquet('data/processed/nhanes_1999_2002_model_input.parquet')

print("=" * 70)
print("NHANES ETL - Data Verification")
print("=" * 70)

print(f"\nDataset Shape: {df.shape[0]} rows × {df.shape[1]} columns")

print(f"\nCycles represented:")
for cycle, count in sorted(df["cycle"].value_counts().items()):
    pct = 100 * count / len(df)
    print(f"  {cycle}: {count:5d} ({pct:.1f}%)")

print(f"\nSurvey weight statistics:")
print(f"  Min:    {df['survey_weight'].min():.2f}")
print(f"  Max:    {df['survey_weight'].max():.2f}")
print(f"  Mean:   {df['survey_weight'].mean():.2f}")

print(f"\nKey phenotypic age markers (completeness):")
key_markers = ['LBXALB', 'LBXCR', 'LBXGLU', 'LBXWBC', 'LBXRDW', 'LBXCRP']
for marker in key_markers:
    if marker in df.columns:
        non_null = df[marker].notna().sum()
        pct = 100 * non_null / len(df)
        print(f"  {marker:10s}: {non_null:5d}/{len(df)} ({pct:5.1f}%)")

print(f"\nDemographic information:")
if 'RIDAGEYR' in df.columns:
    print(f"  Age - Mean: {df['RIDAGEYR'].mean():.1f} (SD: {df['RIDAGEYR'].std():.1f})")
if 'RIDSEX' in df.columns:
    print(f"  Sex - Males: {(df['RIDSEX']==1).sum()}, Females: {(df['RIDSEX']==2).sum()}")
if 'BMXBMI' in df.columns:
    print(f"  BMI - Mean: {df['BMXBMI'].mean():.1f} (SD: {df['BMXBMI'].std():.1f})")

print(f"\nColumns in model input:")
cols = df.columns.tolist()
print(f"  {', '.join(cols)}")

print("\n" + "=" * 70)
print("ETL pipeline completed successfully!")
print("=" * 70)
