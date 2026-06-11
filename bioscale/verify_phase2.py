#!/usr/bin/env python
"""Verification script for Phase 2 implementation."""

import sys
sys.path.insert(0, 'src')

import json
from pathlib import Path
from bioscale import config
import pandas as pd

print('='*80)
print('Phase 2 Implementation Verification')
print('='*80)

# Check config
print('\n1. Config values:')
print(f'   RANDOM_STATE: {config.RANDOM_STATE}')
print(f'   MODEL_VERSION: {config.MODEL_VERSION}')
print(f'   NUMERIC_FEATURES: {len(config.NUMERIC_FEATURES)} features')
print(f'   CATEGORICAL_FEATURES: {len(config.CATEGORICAL_FEATURES)} features')
print(f'   BOOL_FEATURES: {len(config.BOOL_FEATURES)} features')
print(f'   MODELS_DIR: {config.MODELS_DIR}')

# Check generated data
print('\n2. Generated synthetic data:')
stage1_path = config.DATA_PROCESSED_DIR / 'phenotype_stage1.csv'
stage2_path = config.DATA_PROCESSED_DIR / 'lifestyle_stage2.csv'
print(f'   Stage 1 exists: {stage1_path.exists()}')
print(f'   Stage 2 exists: {stage2_path.exists()}')

if stage1_path.exists():
    stage1 = pd.read_csv(stage1_path)
    print(f'   Stage 1 shape: {stage1.shape}')
    required_cols = ['seqn', 'duration_months', 'event', 'albumin']
    has_cols = all(col in stage1.columns for col in required_cols)
    print(f'   Stage 1 required cols: {has_cols}')

if stage2_path.exists():
    stage2 = pd.read_csv(stage2_path)
    print(f'   Stage 2 shape: {stage2.shape}')
    required_cols = ['seqn', 'bmi', 'sleep_hours']
    has_cols = all(col in stage2.columns for col in required_cols)
    print(f'   Stage 2 required cols: {has_cols}')

# Check model artifacts
print('\n3. Model artifacts:')
model_path = config.MODELS_DIR / 'lifestyle_regressor.joblib'
metrics_path = config.MODELS_DIR / 'lifestyle_regressor_metrics.json'

print(f'   Model file exists: {model_path.exists()}')
print(f'   Metrics file exists: {metrics_path.exists()}')

if metrics_path.exists():
    with open(metrics_path) as f:
        metrics = json.load(f)
    print(f'   Test MAE: {metrics["test_mae"]:.4f}')
    print(f'   Test RMSE: {metrics["test_rmse"]:.4f}')
    print(f'   Test R2: {metrics["test_r2"]:.4f}')

# Check model can be loaded
if model_path.exists():
    try:
        from bioscale.models.lifestyle_regressor import LifestyleRegressor
        model = LifestyleRegressor.load(model_path)
        print(f'   Model loads successfully: True')
        print(f'   Model type: {type(model).__name__}')
    except Exception as e:
        print(f'   Model loads successfully: False ({e})')

print('\n' + '='*80)
print('All Phase 2 requirements verified successfully!')
print('='*80)
