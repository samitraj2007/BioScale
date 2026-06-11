"""
SHAP Explainability Script for BioScale Lifestyle Model.

Computes global and per-sample SHAP values for the trained LifestyleRegressor
on real NHANES data.

Outputs:
- data/processed/shap_global_importance.csv: Feature importance (mean absolute SHAP)
- data/processed/shap_values_sample.parquet: Per-sample SHAP values
"""

import logging
from pathlib import Path

import numpy as np
import pandas as pd
import shap

from bioscale import config
from bioscale.models.lifestyle_regressor import LifestyleRegressor
from bioscale.data.load_nhanes_real import load_nhanes_model_input
from bioscale.data.nhanes_mapping import split_nhanes_to_stage1_stage2

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")


def main():
    """Run SHAP explainability computation on real NHANES data."""
    
    print("=" * 80)
    print("BioScale SHAP Explainability Script")
    print("=" * 80)
    
    # Load the trained model
    print("\n[1] Loading trained LifestyleRegressor model...")
    model_path = config.MODELS_DIR / "lifestyle_regressor.joblib"
    
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found at {model_path}. "
            "Please run train_pipeline.py first to train the model."
        )
    
    model = LifestyleRegressor.load(model_path)
    print(f"  OK: Model loaded from {model_path}")
    
    # Load real NHANES data
    print("\n[2] Loading real NHANES data...")
    
    try:
        df_nhanes = load_nhanes_model_input()
    except FileNotFoundError:
        raise FileNotFoundError(
            "Data not found at data/processed/nhanes_1999_2002_model_input.parquet. "
            "Please run Phase 1 ETL or Phase 2 training first."
        )
    
    # Split into Stage 2 (lifestyle features)
    print("\n[3] Mapping NHANES data to Stage 2 schema...")
    _, stage2_df = split_nhanes_to_stage1_stage2(df_nhanes)
    
    # Subsample for speed
    sample_size = min(1000, len(stage2_df))
    df_sample = stage2_df.sample(n=sample_size, random_state=42)
    print(f"  OK: Loaded {len(stage2_df)} total Stage 2 records, using {len(df_sample)} for SHAP")
    
    # Prepare feature matrix
    print("\n[4] Preparing feature matrix...")
    
    # Extract feature columns that the model was trained on
    # Filter to only columns that exist in stage2_df
    available_feature_cols = [col for col in config.LIFESTYLE_FEATURE_COLS if col in stage2_df.columns]
    
    if not available_feature_cols:
        raise ValueError(
            f"No feature columns found. Expected {config.LIFESTYLE_FEATURE_COLS}, "
            f"but Stage 2 has: {list(stage2_df.columns)}"
        )
    
    X_raw = df_sample[available_feature_cols].copy()
    
    # Transform using the model's preprocessor (same as during training)
    X_transformed = model.preprocessor_.transform(X_raw)
    
    # Get feature names after preprocessing (including one-hot encoded features)
    feature_names = model.preprocessor_.get_feature_names_out(available_feature_cols)
    
    print(f"  OK: Original features: {len(available_feature_cols)}")
    print(f"  OK: Features after preprocessing: {len(feature_names)}")
    
    # Get the underlying XGBoost booster and create SHAP explainer
    print("\n[5] Computing SHAP values...")
    
    booster = model.booster_
    explainer = shap.TreeExplainer(booster)
    
    # Compute SHAP values for the sample
    shap_values = explainer.shap_values(X_transformed)
    
    # Handle both single-output (regression) and multi-output cases
    if isinstance(shap_values, list):
        # Multi-output case (shouldn't happen for regression, but handle it)
        shap_values = shap_values[0]
    
    print(f"  OK: SHAP values computed: shape {shap_values.shape}")
    
    # Compute global feature importance (mean absolute SHAP value)
    print("\n[6] Computing global feature importance...")
    
    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    
    global_importance_df = pd.DataFrame({
        "feature_name": feature_names,
        "mean_abs_shap_value": mean_abs_shap,
    }).sort_values("mean_abs_shap_value", ascending=False)
    
    print(f"  OK: Top 5 features by importance:")
    for idx, row in global_importance_df.head(5).iterrows():
        print(f"      {row['feature_name']:30s}: {row['mean_abs_shap_value']:.6f}")
    
    # Save global importance
    output_global = Path("data/processed/shap_global_importance.csv")
    output_global.parent.mkdir(parents=True, exist_ok=True)
    global_importance_df.to_csv(output_global, index=False)
    print(f"\n  OK: Saved global importance to {output_global}")
    
    # Create per-sample SHAP values table
    print("\n[7] Creating per-sample SHAP values table...")
    
    # Long format: seqn, feature_name, shap_value
    shap_long_rows = []
    
    for i, seqn in enumerate(df_sample["seqn"].values):
        for j, feature_name in enumerate(feature_names):
            shap_long_rows.append({
                "seqn": seqn,
                "feature_name": feature_name,
                "shap_value": shap_values[i, j],
            })
    
    shap_values_df = pd.DataFrame(shap_long_rows)
    
    print(f"  OK: Created {len(shap_values_df)} SHAP entries")
    print(f"     ({len(df_sample)} samples x {len(feature_names)} features)")
    
    # Save per-sample SHAP values
    output_sample = Path("data/processed/shap_values_sample.parquet")
    output_sample.parent.mkdir(parents=True, exist_ok=True)
    shap_values_df.to_parquet(output_sample, index=False)
    print(f"  OK: Saved per-sample SHAP values to {output_sample}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SHAP Explainability Computation Complete")
    print("=" * 80)
    print(f"\nSummary:")
    print(f"  Total samples analyzed: {len(df_sample)}")
    print(f"  Total features: {len(feature_names)}")
    print(f"  Total SHAP entries: {len(shap_values_df)}")
    print(f"\nOutput files:")
    print(f"  1. {output_global} (global importance)")
    print(f"  2. {output_sample} (per-sample values)")
    print(f"\nTop 3 most important features:")
    for idx, (_, row) in enumerate(global_importance_df.head(3).iterrows(), 1):
        print(f"  {idx}. {row['feature_name']}: {row['mean_abs_shap_value']:.6f}")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
