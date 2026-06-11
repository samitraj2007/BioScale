"""Quick verification of Phase 1 ETL package."""
import sys
sys.path.insert(0, 'backend')
from etl import run_nhanes_etl
from pathlib import Path
import pandas as pd

print("PHASE 1 ETL PACKAGE - QUICK VERIFICATION")
print("="*80)

# Check that files exist
print("\n1. Package Files:")
files_to_check = [
    "backend/etl/__init__.py",
    "backend/etl/nhanes_etl.py",
    "backend/etl/nhanes_metadata.py",
    "backend/etl/README.md"
]
for f in files_to_check:
    exists = Path(f).exists()
    status = "OK" if exists else "MISSING"
    print(f"   {f}: {status}")

# Check outputs
print("\n2. Output Files:")
outputs = [
    "data/interim/nhanes_1999_2002_merged.parquet",
    "data/processed/nhanes_1999_2002_model_input.parquet",
    "data/processed/nhanes_1999_2002_with_mortality.parquet"
]
for f in outputs:
    p = Path(f)
    if p.exists():
        df = pd.read_parquet(f)
        print(f"   {f}: {df.shape[0]} rows x {df.shape[1]} cols")
    else:
        print(f"   {f}: MISSING")

print("\n3. Function Import:")
print(f"   run_nhanes_etl: {run_nhanes_etl}")

print("\n" + "="*80)
print("READY TO USE: python backend/etl/nhanes_etl.py")
print("="*80)
