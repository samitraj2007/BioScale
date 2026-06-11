"""
Training pipeline CLI for the BioScale ML models.

This module orchestrates the full pipeline:
1. Generate or load stage 1 and stage 2 data.
2. Build Phenotypic Age targets from stage 1.
3. Join targets into stage 2.
4. Optimize and train the lifestyle regressor.
5. Evaluate on test set and save artifacts.

Supports two modes:
- Default (synthetic): Uses generate_synthetic_nhanes() or loads from CSV
- Real data (--use-real-data): Uses Phase 1 NHANES ETL output with optional mortality
"""

import argparse
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from bioscale import config
from bioscale.models.phenotypic_age import (
    build_phenotypic_age_target,
    mortality_risk_to_age,
    risk_to_age_anchored,
)
from bioscale.models.optimization import optimize_lifestyle_regressor
from bioscale.models.survival import fit_cox_model, predict_risk
from bioscale.data.load_nhanes_real import (
    load_nhanes_model_input,
    load_nhanes_with_mortality,
)
from bioscale.data.nhanes_mapping import split_nhanes_to_stage1_stage2

logger = logging.getLogger(__name__)


def generate_synthetic_nhanes(n: int = 500, seed: int = 42) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate synthetic NHANES-like data for development and testing.

    Parameters
    ----------
    n : int, default=500
        Number of records to generate.
    seed : int, default=42
        Random seed for reproducibility.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        (stage1_df, stage2_df) with appropriate columns and distributions.
    """
    np.random.seed(seed)

    seqn = np.arange(1, n + 1)
    chronological_age = np.random.uniform(20, 80, n)
    sex = np.random.choice(["male", "female"], n)

    stage1_data = {
        "seqn": seqn,
        "chronological_age": chronological_age,
        "sex": sex,
        "albumin": np.random.normal(4.0, 0.5, n),
        "creatinine": np.random.normal(0.9, 0.2, n),
        "glucose": np.random.normal(95, 15, n),
        "crp": np.random.lognormal(0, 1, n),
        "lymphocyte_pct": np.random.normal(28, 6, n),
        "mcv": np.random.normal(90, 5, n),
        "rdw": np.random.normal(13.5, 1.2, n),
        "alkaline_phosphatase": np.random.normal(70, 20, n),
        "wbc": np.random.normal(7.0, 1.5, n),
        "duration_months": np.random.uniform(12, 120, n),
        "event": np.random.binomial(1, 0.15, n),
    }
    stage1_df = pd.DataFrame(stage1_data)

    stage2_data = {
        "seqn": seqn,
        "chronological_age": chronological_age,
        "sex": sex,
        "bmi": np.clip(np.random.normal(27, 5, n), 15, 50),
        "sleep_hours": np.clip(np.random.normal(7, 1.2, n), 4, 12),
        "sleep_quality": np.random.randint(1, 6, n),
        "physical_activity_level": np.random.choice(["low", "moderate", "high"], n),
        "weekly_exercise_sessions": np.random.randint(0, 8, n),
        "smoking_status": np.random.choice(["never", "former", "current"], n),
        "alcohol_intake_frequency": np.random.choice(
            ["never", "monthly", "weekly", "daily"], n
        ),
        "diet_quality_score": np.random.randint(1, 11, n),
        "stress_level": np.random.randint(1, 11, n),
        "has_hypertension": np.random.binomial(1, 0.25, n).astype(bool),
        "has_diabetes": np.random.binomial(1, 0.10, n).astype(bool),
    }
    stage2_df = pd.DataFrame(stage2_data)

    return stage1_df, stage2_df


def load_or_generate_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load processed data if it exists, otherwise generate synthetic data.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        (stage1_df, stage2_df)
    """
    config.DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    stage1_path = config.DATA_PROCESSED_DIR / "phenotype_stage1.csv"
    stage2_path = config.DATA_PROCESSED_DIR / "lifestyle_stage2.csv"

    if stage1_path.exists() and stage2_path.exists():
        print(f"Loading processed data from {config.DATA_PROCESSED_DIR}...")
        stage1_df = pd.read_csv(stage1_path)
        stage2_df = pd.read_csv(stage2_path)
    else:
        print(f"Processed data not found. Generating synthetic NHANES data...")
        stage1_df, stage2_df = generate_synthetic_nhanes(n=500, seed=config.RANDOM_STATE)
        stage1_df.to_csv(stage1_path, index=False)
        stage2_df.to_csv(stage2_path, index=False)
        print(f"Saved synthetic data to {config.DATA_PROCESSED_DIR}")

    return stage1_df, stage2_df


def main():
    """Run the full training pipeline."""
    parser = argparse.ArgumentParser(description="Train BioScale models")
    parser.add_argument(
        "--use-real-data",
        action="store_true",
        help="Use real NHANES ETL output instead of synthetic data. Requires Phase 1 ETL to be run.",
    )
    parser.add_argument(
        "--n-trials",
        type=int,
        default=50,
        help="Number of Optuna trials for hyperparameter optimization.",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=config.TEST_SIZE,
        help="Test set fraction.",
    )
    parser.add_argument(
        "--val-size",
        type=float,
        default=config.VAL_SIZE,
        help="Validation set fraction.",
    )
    args = parser.parse_args()

    print("=" * 80)
    print("BioScale Training Pipeline")
    if args.use_real_data:
        print("Mode: Real NHANES data")
    else:
        print("Mode: Synthetic data (default)")
    print("=" * 80)

    # Load or generate data based on mode
    if args.use_real_data:
        print("\n[Real NHANES Mode]")
        print("Loading real NHANES data from Phase 1 ETL...")
        
        # Try to load with mortality first, fall back to model_input
        try:
            df_nhanes = load_nhanes_with_mortality()
            print(f"  Loaded NHANES with mortality: {df_nhanes.shape}")
        except FileNotFoundError:
            print("  Mortality-augmented file not found; falling back to model_input.")
            df_nhanes = load_nhanes_model_input()
            print(f"  Loaded NHANES model_input: {df_nhanes.shape}")
        
        # Split into Stage 1 and Stage 2 schemas
        print("  Mapping to Stage 1 and Stage 2 schemas...")
        stage1_df, stage2_df = split_nhanes_to_stage1_stage2(df_nhanes)
        print(f"  Stage 1: {stage1_df.shape}")
        print(f"  Stage 2: {stage2_df.shape}")
        
        # Define biomarker columns available in real data
        biomarker_cols = [col for col in ["wbc", "crp", "glucose", "insulin"] 
                         if col in stage1_df.columns]
        print(f"  Available biomarkers: {biomarker_cols}")
        
        # Build phenotypic age from available data
        if {"duration_months", "event"}.issubset(stage1_df.columns):
            print("  Building phenotypic age from Cox model with mortality data...")
            feature_cols = biomarker_cols + ["chronological_age"]
            
            try:
                cox = fit_cox_model(
                    df=stage1_df,
                    duration_col="duration_months",
                    event_col="event",
                    feature_cols=feature_cols,
                )
                risk = predict_risk(cox, stage1_df[feature_cols], horizon_years=10.0)
                # Age-anchored target: phenotypic age stays tied to chronological
                # age, with a bounded acceleration from (standardized) risk.
                phenotypic_age = risk_to_age_anchored(
                    risk, stage1_df["chronological_age"].values
                )
                print(f"  Phenotypic Age range: {phenotypic_age.min():.1f} - {phenotypic_age.max():.1f} years")
            except Exception as e:
                print(f"  Warning: Cox model fitting failed ({e}); using biomarker-based age.")
                z = stage1_df[biomarker_cols].apply(lambda x: (x - x.mean()) / (x.std() + 1e-8))
                risk_idx = z.mean(axis=1)
                phenotypic_age = risk_to_age_anchored(
                    risk_idx.values, stage1_df["chronological_age"].values
                )
                print(f"  Phenotypic Age (biomarker-based) range: {phenotypic_age.min():.1f} - {phenotypic_age.max():.1f} years")
        else:
            print("  No mortality data; using biomarker-based phenotypic age...")
            z = stage1_df[biomarker_cols].apply(lambda x: (x - x.mean()) / (x.std() + 1e-8))
            risk_idx = z.mean(axis=1)
            phenotypic_age = risk_to_age_anchored(
                risk_idx.values, stage1_df["chronological_age"].values
            )
            print(f"  Phenotypic Age range: {phenotypic_age.min():.1f} - {phenotypic_age.max():.1f} years")
        
        # Join phenotypic age to stage2
        stage2_df = stage2_df.copy()
        stage2_df["phenotypic_age"] = np.asarray(phenotypic_age)
        
    else:
        # Original synthetic data path (unchanged)
        stage1_df, stage2_df = load_or_generate_data()

        print(f"\nStage 1 data shape: {stage1_df.shape}")
        print(f"Stage 2 data shape: {stage2_df.shape}")

        biomarker_cols = [
            "albumin",
            "creatinine",
            "glucose",
            "crp",
            "lymphocyte_pct",
            "mcv",
            "rdw",
            "alkaline_phosphatase",
            "wbc",
        ]

        print("\nBuilding Phenotypic Age target...")
        phenotypic_age = build_phenotypic_age_target(stage1_df, biomarker_cols)
        print(f"Phenotypic Age range: {phenotypic_age.min():.1f} - {phenotypic_age.max():.1f} years")

        stage2_df = stage2_df.merge(
            phenotypic_age.reset_index().rename(columns={"index": "seqn"}),
            on="seqn",
            how="left",
        )

    stage2_df = stage2_df.dropna(subset=[config.TARGET_COL])

    # Determine which feature columns are available
    if args.use_real_data:
        # For real data, use only columns that are actually present
        available_features = [col for col in config.LIFESTYLE_FEATURE_COLS if col in stage2_df.columns]
        print(f"\nAvailable lifestyle features: {available_features}")
    else:
        # For synthetic data, use all configured features
        available_features = config.LIFESTYLE_FEATURE_COLS
    
    y = stage2_df[config.TARGET_COL].values
    X = stage2_df[available_features].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=config.RANDOM_STATE
    )

    val_size_adjusted = args.val_size / (1.0 - args.test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=val_size_adjusted, random_state=config.RANDOM_STATE
    )

    print(f"\nData split:")
    print(f"  Train: {X_train.shape[0]}")
    print(f"  Val:   {X_val.shape[0]}")
    print(f"  Test:  {X_test.shape[0]}")

    print(f"\nOptimizing lifestyle regressor with {args.n_trials} trials...")
    
    # Determine numeric and categorical columns for this dataset
    if args.use_real_data:
        # For real data, filter to available columns
        numeric_cols = [col for col in config.NUMERIC_FEATURES if col in available_features]
        categorical_cols = [col for col in config.CATEGORICAL_FEATURES if col in available_features]
    else:
        # For synthetic, use all configured columns
        numeric_cols = config.NUMERIC_FEATURES
        categorical_cols = config.CATEGORICAL_FEATURES
    
    optimization_result = optimize_lifestyle_regressor(
        X_train,
        y_train,
        X_val,
        y_val,
        numeric_cols=numeric_cols,
        categorical_cols=categorical_cols,
        n_trials=args.n_trials,
        random_state=config.RANDOM_STATE,
    )

    best_params = optimization_result["best_params"]
    best_model = optimization_result["best_model"]
    best_val_mae = optimization_result["best_mae"]

    print(f"\nBest hyperparameters:")
    for key, value in best_params.items():
        print(f"  {key}: {value}")
    print(f"  Best validation MAE: {best_val_mae:.4f}")

    print("\nEvaluating on test set...")
    y_test_pred = best_model.predict(X_test)
    test_mae = mean_absolute_error(y_test, y_test_pred)
    test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
    test_r2 = r2_score(y_test, y_test_pred)

    print(f"  Test MAE:  {test_mae:.4f}")
    print(f"  Test RMSE: {test_rmse:.4f}")
    print(f"  Test R²:   {test_r2:.4f}")

    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model_path = config.MODELS_DIR / "lifestyle_regressor.joblib"
    best_model.save(model_path)
    print(f"\nModel saved to {model_path}")

    metrics = {
        "test_mae": float(test_mae),
        "test_rmse": float(test_rmse),
        "test_r2": float(test_r2),
        "best_val_mae": float(best_val_mae),
        "best_hyperparameters": best_params,
    }
    metrics_path = config.MODELS_DIR / "lifestyle_regressor_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {metrics_path}")

    print("\n" + "=" * 80)
    print("Training pipeline completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
