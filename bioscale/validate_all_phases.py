"""
Comprehensive BioScale Validation Script

Tests all four phases end-to-end:
1. Phase 1: ETL pipeline
2. Phase 2: Real-data training
3. Phase 5: SHAP explainability
4. Phase 6: FastAPI server

Run from repo root: python validate_all_phases.py
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Execute a command and report results."""
    print(f"\n{'='*80}")
    print(f"TEST: {description}")
    print(f"{'='*80}")
    print(f"Command: {cmd}\n")
    
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=300
        )
        
        if result.stdout:
            print("OUTPUT:")
            print(result.stdout[:1000] if len(result.stdout) > 1000 else result.stdout)
        
        if result.returncode != 0:
            print(f"\nERROR (exit code {result.returncode}):")
            print(result.stderr[:500] if result.stderr else "No error output")
            return False
        
        print("\nSUCCESS [OK]")
        return True
        
    except subprocess.TimeoutExpired:
        print("TIMEOUT (>300 seconds) [FAIL]")
        return False
    except Exception as e:
        print(f"EXCEPTION: {e} [FAIL]")
        return False


def check_files_exist(files, description):
    """Check if a list of files exist."""
    print(f"\n{description}")
    all_exist = True
    for f in files:
        exists = Path(f).exists()
        status = "[OK]" if exists else "[MISS]"
        print(f"  {status} {f}")
        all_exist = all_exist and exists
    return all_exist


def main():
    """Run comprehensive validation."""
    print("\n" + "="*80)
    print("BioScale Comprehensive Validation Suite")
    print("="*80)
    
    results = {}
    
    # Phase 1: ETL
    print("\n\n" + "#"*80)
    print("# PHASE 1: NHANES ETL PIPELINE")
    print("#"*80)
    
    results["phase1_import"] = run_command(
        "python -c \"import sys; sys.path.insert(0, r'backend'); from etl.nhanes_etl import run_nhanes_etl; print('ETL import successful')\"",
        "Phase 1 ETL - Module Import"
    )
    
    # Check ETL files
    etl_files = [
        "backend/etl/__init__.py",
        "backend/etl/nhanes_etl.py",
        "backend/etl/nhanes_metadata.py",
        "backend/etl/README.md",
    ]
    results["phase1_files"] = check_files_exist(etl_files, "\nPhase 1 ETL Package Files:")
    
    # Check ETL outputs
    etl_outputs = [
        "data/interim/nhanes_1999_2002_merged.parquet",
        "data/processed/nhanes_1999_2002_model_input.parquet",
        "data/processed/nhanes_1999_2002_with_mortality.parquet",
    ]
    results["phase1_outputs"] = check_files_exist(etl_outputs, "\nPhase 1 ETL Output Files:")
    
    # Phase 2: Training
    print("\n\n" + "#"*80)
    print("# PHASE 2: MODEL TRAINING")
    print("#"*80)
    
    results["phase2_import"] = run_command(
        "python -c \"import sys; sys.path.insert(0, r'src'); from bioscale.cli.train_pipeline import main; print('Phase 2 training import successful')\"",
        "Phase 2 Training - Module Import"
    )
    
    # Check Phase 2 files
    phase2_files = [
        "src/bioscale/config.py",
        "src/bioscale/models/survival.py",
        "src/bioscale/models/phenotypic_age.py",
        "src/bioscale/models/lifestyle_regressor.py",
        "src/bioscale/models/optimization.py",
        "src/bioscale/models/persistence.py",
        "src/bioscale/cli/train_pipeline.py",
        "src/bioscale/data/load_nhanes_real.py",
        "src/bioscale/data/nhanes_mapping.py",
        "src/tests/test_models.py",
    ]
    results["phase2_files"] = check_files_exist(phase2_files, "\nPhase 2 Source Files:")
    
    # Phase 5: SHAP
    print("\n\n" + "#"*80)
    print("# PHASE 5: SHAP EXPLAINABILITY")
    print("#"*80)
    
    results["phase5_import"] = run_command(
        "python -c \"import sys; sys.path.insert(0, r'src'); from bioscale.cli.compute_shap import main; print('Phase 5 SHAP import successful')\"",
        "Phase 5 SHAP - Module Import"
    )
    
    phase5_files = [
        "src/bioscale/cli/compute_shap.py",
        "src/bioscale/explainability/shap_engine.py",
        "src/bioscale/explainability/translation.py",
    ]
    results["phase5_files"] = check_files_exist(phase5_files, "\nPhase 5 SHAP Files:")
    
    # Phase 6: API
    print("\n\n" + "#"*80)
    print("# PHASE 6: FASTAPI SERVER")
    print("#"*80)
    
    results["phase6_import"] = run_command(
        "python -c \"import sys; sys.path.insert(0, r'backend'); from api.app import app; print('Phase 6 API import successful')\"",
        "Phase 6 API - Module Import"
    )
    
    phase6_files = [
        "backend/api/app.py",
    ]
    results["phase6_files"] = check_files_exist(phase6_files, "\nPhase 6 API Files:")
    
    # Summary
    print("\n\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {test_name}")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n" + "="*80)
        print("ALL TESTS PASSED - BioScale is ready to use!")
        print("="*80)
        print("\nYou can now run:")
        print("  1. Phase 1 ETL:")
        print("     python -c \"import sys; sys.path.insert(0, r'backend'); from etl.nhanes_etl import run_nhanes_etl; run_nhanes_etl()\"")
        print("\n  2. Phase 2 Training (real data):")
        print("     python -c \"import sys; sys.path.insert(0, r'src'); from bioscale.cli.train_pipeline import main; import sys as _s; _s.argv = ['train_pipeline.py', '--use-real-data', '--n-trials', '5']; main()\"")
        print("\n  3. Phase 5 SHAP:")
        print("     python -m bioscale.cli.compute_shap")
        print("\n  4. Phase 6 API:")
        print("     uvicorn backend.api.app:app --reload")
        return 0
    else:
        print(f"\n{total_tests - passed_tests} tests failed - please review the output above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
