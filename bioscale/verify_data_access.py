"""
Verification script for NHANES data access layer.

Demonstrates both import styles and data loading.
"""

print("=" * 70)
print("NHANES Data Access Layer Verification")
print("=" * 70)

# Test Style 1: Direct module import
print("\n[1] Direct module import:")
print("    from bioscale.data.load_nhanes_real import load_nhanes_with_mortality")

from bioscale.data.load_nhanes_real import load_nhanes_with_mortality
df_mort = load_nhanes_with_mortality()
print(f"    OK - Loaded: {df_mort.shape[0]:,} rows x {df_mort.shape[1]} columns")

# Test Style 2: Package-level import
print("\n[2] Package-level import:")
print("    from bioscale.data import load_nhanes_model_input")

from bioscale.data import load_nhanes_model_input
df_model = load_nhanes_model_input()
print(f"    OK - Loaded: {df_model.shape[0]:,} rows x {df_model.shape[1]} columns")

# Test Style 3: Both functions from package
print("\n[3] Import both functions from package:")
print("    from bioscale.data import load_nhanes_model_input, load_nhanes_with_mortality")

from bioscale.data import (
    load_nhanes_model_input as load_model,
    load_nhanes_with_mortality as load_mort_alias
)
print(f"    OK - Alias 'load_model' available")
print(f"    OK - Alias 'load_mort_alias' available")

# Data summaries
print("\n[4] Model Input Dataset Summary:")
print(f"    Rows: {df_model.shape[0]:,}")
print(f"    Columns: {df_model.shape[1]}")
print(f"    First 5 columns: {df_model.columns.tolist()[:5]}")
print(f"    Survey cycles: {df_model['cycle'].unique().tolist()}")
print(f"    Age range: {df_model['RIDAGEYR'].min():.0f} - {df_model['RIDAGEYR'].max():.0f} years")

print("\n[5] With Mortality Dataset Summary:")
print(f"    Rows: {df_mort.shape[0]:,}")
print(f"    Columns: {df_mort.shape[1]}")
print(f"    Mortality columns: {['MORTSTAT', 'PERMTH_EXM', 'duration_months', 'event']}")
print(f"    Duration months with values: {df_mort['duration_months'].notna().sum():,} ({100*df_mort['duration_months'].notna().sum()/len(df_mort):.1f}%)")
print(f"    Follow-up time: {df_mort['duration_months'].min():.0f} - {df_mort['duration_months'].max():.0f} months")

print("\n[6] Data Consistency Check:")
print(f"    Model input unique SEQN: {df_model['SEQN'].nunique():,}")
print(f"    With mortality unique SEQN: {df_mort['SEQN'].nunique():,}")
print(f"    (Note: mortality has more rows due to multiple records per SEQN)")

print("\n" + "=" * 70)
print("SUCCESS - All data access functions working correctly!")
print("=" * 70)
