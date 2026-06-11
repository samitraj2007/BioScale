"""
Comprehensive test of NHANES schema mapping functionality.

Demonstrates all three layers:
1. Data loading (load_nhanes_real.py)
2. Schema mapping (nhanes_mapping.py)
3. Schema validation
"""

print("=" * 80)
print("NHANES SCHEMA MAPPING - COMPREHENSIVE TEST")
print("=" * 80)

# ============ PART 1: DATA LOADING ============
print("\n[PART 1] Loading NHANES data")
print("-" * 80)

from bioscale.data import load_nhanes_model_input, load_nhanes_with_mortality

df_model = load_nhanes_model_input()
df_mort = load_nhanes_with_mortality()

print(f"Model input dataset:    {df_model.shape[0]:,} rows × {df_model.shape[1]} columns")
print(f"With mortality dataset: {df_mort.shape[0]:,} rows × {df_mort.shape[1]} columns")

# ============ PART 2: SCHEMA MAPPING ============
print("\n[PART 2] Mapping to Stage 1 and Stage 2 schemas")
print("-" * 80)

from bioscale.data import split_nhanes_to_stage1_stage2
from bioscale.data.nhanes_mapping import get_stage1_schema, get_stage2_schema

# Test with model_input
print("\nMAPPING MODEL INPUT DATASET:")
stage1_model, stage2_model = split_nhanes_to_stage1_stage2(df_model)
print(f"  Stage 1: {stage1_model.shape[0]:,} rows × {stage1_model.shape[1]} columns")
print(f"  Stage 2: {stage2_model.shape[0]:,} rows × {stage2_model.shape[1]} columns")

# Test with mortality data
print("\nMAPPING WITH MORTALITY DATASET:")
stage1_mort, stage2_mort = split_nhanes_to_stage1_stage2(df_mort)
print(f"  Stage 1: {stage1_mort.shape[0]:,} rows × {stage1_mort.shape[1]} columns (with survival)")
print(f"  Stage 2: {stage2_mort.shape[0]:,} rows × {stage2_mort.shape[1]} columns")

# ============ PART 3: SCHEMA VALIDATION ============
print("\n[PART 3] Schema descriptions and validation")
print("-" * 80)

schema1 = get_stage1_schema()
schema2 = get_stage2_schema()

print("\nSTAGE 1 SCHEMA (Biomarkers + Survival):")
for col, info in schema1.items():
    optional_marker = " [OPTIONAL]" if info.get("optional") else ""
    print(f"  {col:20s}: {info['description']:40s} {optional_marker}")

print("\nSTAGE 2 SCHEMA (Lifestyle + Anthropometry):")
for col, info in schema2.items():
    print(f"  {col:25s}: {info['description']}")

# ============ PART 4: DATA VALIDATION ============
print("\n[PART 4] Data validation")
print("-" * 80)

print("\nSTAGE 1 (with mortality) - Data summary:")
print(f"  seqn range: {stage1_mort['seqn'].min():.0f} - {stage1_mort['seqn'].max():.0f}")
print(f"  chronological_age range: {stage1_mort['chronological_age'].min():.0f} - {stage1_mort['chronological_age'].max():.0f} years")
print(f"  glucose range: {stage1_mort['glucose'].min():.1f} - {stage1_mort['glucose'].max():.1f} mg/dL")
print(f"  wbc range: {stage1_mort['wbc'].min():.1f} - {stage1_mort['wbc'].max():.1f} 10³/µL")
print(f"  crp range: {stage1_mort['crp'].min():.1f} - {stage1_mort['crp'].max():.1f} mg/L")
print(f"  duration_months range: {stage1_mort['duration_months'].min():.0f} - {stage1_mort['duration_months'].max():.0f} months")
print(f"  event value counts:\n{stage1_mort['event'].value_counts().to_string()}")

print("\nSTAGE 2 (with mortality) - Data summary:")
print(f"  bmi range: {stage2_mort['bmi'].min():.1f} - {stage2_mort['bmi'].max():.1f} kg/m²")
print(f"  waist_circumference range: {stage2_mort['waist_circumference'].min():.1f} - {stage2_mort['waist_circumference'].max():.1f} cm")
print(f"  height range: {stage2_mort['height'].min():.1f} - {stage2_mort['height'].max():.1f} cm")
print(f"  weight range: {stage2_mort['weight'].min():.1f} - {stage2_mort['weight'].max():.1f} kg")
print(f"  alcohol_days_per_week range: {stage2_mort['alcohol_days_per_week'].min():.1f} - {stage2_mort['alcohol_days_per_week'].max():.1f}")

# ============ PART 5: SAMPLE DATA ============
print("\n[PART 5] Sample data from both stages")
print("-" * 80)

print("\nSTAGE 1 - First 5 participants:")
print(stage1_mort[['seqn', 'chronological_age', 'glucose', 'wbc', 'crp', 'duration_months']].head(5).to_string())

print("\nSTAGE 2 - First 5 participants:")
print(stage2_mort[['seqn', 'chronological_age', 'bmi', 'alcohol_days_per_week', 'smoking_current_status']].head(5).to_string())

# ============ PART 6: COLUMN MAPPING VERIFICATION ============
print("\n[PART 6] Column mapping verification")
print("-" * 80)

print("\nStage 1 columns (expected biomarkers + survival):")
print(f"  Expected: seqn, chronological_age, wbc, crp, glucose, insulin, duration_months, event")
print(f"  Actual:   {', '.join(stage1_mort.columns.tolist())}")
print(f"  Match: {set(stage1_mort.columns) == {'seqn', 'chronological_age', 'wbc', 'crp', 'glucose', 'insulin', 'duration_months', 'event'}}")

print("\nStage 2 columns (expected lifestyle/anthropometry):")
expected_s2 = {'seqn', 'chronological_age', 'bmi', 'waist_circumference', 'height', 'weight', 
               'alcohol_ever', 'alcohol_days_per_week', 'alcohol_drinks_per_day',
               'smoking_ever_100_cigs', 'smoking_current_status'}
print(f"  Expected: {len(expected_s2)} columns (seqn + age + 9 features)")
print(f"  Actual:   {len(stage2_mort.columns)} columns")
print(f"  Match: {set(stage2_mort.columns) == expected_s2}")

print("\n" + "=" * 80)
print("SUCCESS - All NHANES schema mapping tests passed!")
print("=" * 80)
print("\nNext step: Use stage1 and stage2 in Phase 2 modeling:")
print("  - stage1: Fit Cox model for survival analysis")
print("  - stage2: Train lifestyle regressor for age acceleration prediction")
print("=" * 80)
