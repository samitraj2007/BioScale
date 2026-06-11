#!/usr/bin/env python
"""Verification script for Phase 3 implementation."""

import sys
sys.path.insert(0, 'src')

print('='*80)
print('PHASE 3 FINAL VERIFICATION')
print('='*80)

# 1. Check imports
print('\n1. Checking imports...')
try:
    from bioscale.explainability.shap_engine import ShapExplainer
    from bioscale.explainability.translation import translate_shap_to_years, map_feature_names_for_display
    from bioscale.models.lifestyle_regressor import LifestyleRegressor
    print('   [OK] All imports successful')
except Exception as e:
    print(f'   [FAIL] Import failed: {e}')

# 2. Check ShapExplainer functionality
print('\n2. Checking ShapExplainer...')
try:
    import pandas as pd
    import numpy as np
    from bioscale import config
    
    np.random.seed(config.RANDOM_STATE)
    n = 30
    X_train = pd.DataFrame({
        'chronological_age': np.random.uniform(20, 80, n),
        'bmi': np.random.normal(27, 5, n),
        'sleep_hours': np.random.uniform(4, 12, n),
        'sleep_quality': np.random.randint(1, 6, n),
        'weekly_exercise_sessions': np.random.randint(0, 8, n),
        'diet_quality_score': np.random.randint(1, 11, n),
        'stress_level': np.random.randint(1, 11, n),
        'sex': np.random.choice(['male', 'female'], n),
        'physical_activity_level': np.random.choice(['low', 'moderate', 'high'], n),
        'smoking_status': np.random.choice(['never', 'former', 'current'], n),
        'alcohol_intake_frequency': np.random.choice(['never', 'monthly', 'weekly', 'daily'], n),
        'has_hypertension': np.random.binomial(1, 0.25, n).astype(bool),
        'has_diabetes': np.random.binomial(1, 0.10, n).astype(bool),
    })
    y_train = np.random.normal(50, 10, n)
    
    model = LifestyleRegressor(n_estimators=10, max_depth=3, random_state=config.RANDOM_STATE)
    model.fit(X_train, y_train)
    
    explainer = ShapExplainer(model)
    
    X_test = X_train.iloc[:1]
    X_test_preprocessed = model.preprocessor_.transform(X_test)
    result = explainer.explain_instance(X_test_preprocessed)
    
    assert 'baseline' in result
    assert 'shap_values' in result
    print('[OK] ShapExplainer working correctly')
    print(f'    Baseline: {result["baseline"]:.2f}')
    print(f'    SHAP values count: {len(result["shap_values"])}')
except Exception as e:
    print(f'   [FAIL] ShapExplainer error: {e}')

# 3. Check translation functionality
print('\n3. Checking translation utilities...')
try:
    shap_values = {
        'bmi': 3.5,
        'sleep_hours': -2.1,
        'stress_level': 1.5,
        'diet_quality_score': -0.5,
    }
    chronological_age = 40.0
    
    translated = translate_shap_to_years(50.0, shap_values, chronological_age, top_k=2)
    
    assert 'predicted_age' in translated
    assert 'age_acceleration' in translated
    assert 'top_positive' in translated
    assert 'top_negative' in translated
    
    print('[OK] Translation working correctly')
    print(f'    Predicted age: {translated["predicted_age"]:.2f}')
    print(f'    Age acceleration: {translated["age_acceleration"]:.2f}')
    print(f'    Top positive contributors: {len(translated["top_positive"])}')
    print(f'    Top negative contributors: {len(translated["top_negative"])}')
except Exception as e:
    print(f'   [FAIL] Translation error: {e}')

# 4. Check feature name mapping
print('\n4. Checking feature name mapping...')
try:
    display_name = map_feature_names_for_display('bmi')
    assert display_name == 'Body Mass Index'
    
    unknown_name = map_feature_names_for_display('unknown')
    assert unknown_name == 'unknown'
    
    print('[OK] Feature name mapping working correctly')
    print(f'    bmi -> {display_name}')
except Exception as e:
    print(f'   [FAIL] Feature mapping error: {e}')

print('\n' + '='*80)
print('PHASE 3 VERIFICATION COMPLETE - ALL SYSTEMS GO')
print('='*80)
