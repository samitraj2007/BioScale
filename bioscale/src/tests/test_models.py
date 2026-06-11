"""
Tests for the BioScale ML models.

This module contains unit tests for survival, phenotypic age, and
lifestyle regressor modules.
"""

import numpy as np
import pandas as pd
import pytest

from bioscale import config
from bioscale.models.lifestyle_regressor import LifestyleRegressor
from bioscale.models.phenotypic_age import (
    build_phenotypic_age_target,
    compute_linear_predictor,
    mortality_risk_to_age,
)
from bioscale.models.survival import fit_cox_model, predict_risk


class TestSurvivalModule:
    """Tests for survival.py functions."""

    @pytest.fixture
    def synthetic_survival_data(self):
        """Create a tiny synthetic survival dataset."""
        np.random.seed(config.RANDOM_STATE)
        n = 50
        df = pd.DataFrame({
            "duration_months": np.random.uniform(12, 120, n),
            "event": np.random.binomial(1, 0.2, n),
            "albumin": np.random.normal(4.0, 0.5, n),
            "creatinine": np.random.normal(0.9, 0.2, n),
            "glucose": np.random.normal(95, 15, n),
        })
        return df

    def test_fit_cox_model(self, synthetic_survival_data):
        """Test that Cox model fits without error."""
        cox_model = fit_cox_model(
            synthetic_survival_data,
            duration_col="duration_months",
            event_col="event",
            feature_cols=["albumin", "creatinine", "glucose"],
        )
        assert cox_model is not None
        assert hasattr(cox_model, "predict_survival_function")

    def test_predict_risk(self, synthetic_survival_data):
        """Test that risk prediction returns valid scores."""
        cox_model = fit_cox_model(
            synthetic_survival_data,
            duration_col="duration_months",
            event_col="event",
            feature_cols=["albumin", "creatinine", "glucose"],
        )
        risk = predict_risk(cox_model, synthetic_survival_data[["albumin", "creatinine", "glucose"]])
        assert risk.shape[0] == synthetic_survival_data.shape[0]
        assert np.all(risk >= 0.0)
        assert np.all(risk <= 1.0)


class TestPhenotypicAgeModule:
    """Tests for phenotypic_age.py functions."""

    @pytest.fixture
    def synthetic_stage1_data(self):
        """Create a tiny synthetic stage 1 dataset."""
        np.random.seed(config.RANDOM_STATE)
        n = 50
        df = pd.DataFrame({
            "duration_months": np.random.uniform(12, 120, n),
            "event": np.random.binomial(1, 0.2, n),
            "albumin": np.random.normal(4.0, 0.5, n),
            "creatinine": np.random.normal(0.9, 0.2, n),
            "glucose": np.random.normal(95, 15, n),
        })
        return df

    def test_compute_linear_predictor(self, synthetic_stage1_data):
        """Test linear predictor computation."""
        cox_model = fit_cox_model(
            synthetic_stage1_data,
            duration_col="duration_months",
            event_col="event",
            feature_cols=["albumin", "creatinine", "glucose"],
        )
        lp = compute_linear_predictor(cox_model, synthetic_stage1_data[["albumin", "creatinine", "glucose"]])
        assert lp.shape[0] == synthetic_stage1_data.shape[0]
        assert np.all(np.isfinite(lp))

    def test_mortality_risk_to_age(self):
        """Test risk-to-age mapping."""
        risk = np.array([0.1, 0.5, 0.9])
        age = mortality_risk_to_age(risk)
        assert age.shape == risk.shape
        assert np.all(np.isfinite(age))
        assert np.all(age >= 20)
        assert np.all(age <= 100)

    def test_mortality_risk_to_age_monotonic(self):
        """Test that higher risk maps to older age."""
        low_risk = mortality_risk_to_age(np.array([0.1]))
        high_risk = mortality_risk_to_age(np.array([0.9]))
        assert high_risk[0] > low_risk[0]

    def test_build_phenotypic_age_target(self, synthetic_stage1_data):
        """Test phenotypic age target builder."""
        target = build_phenotypic_age_target(
            synthetic_stage1_data,
            feature_cols=["albumin", "creatinine", "glucose"],
        )
        assert isinstance(target, pd.Series)
        assert len(target) == len(synthetic_stage1_data)
        assert np.all(~target.isna())
        assert np.all(target >= 20)
        assert np.all(target <= 100)


class TestLifestyleRegressor:
    """Tests for lifestyle_regressor.py."""

    @pytest.fixture
    def synthetic_lifestyle_data(self):
        """Create a tiny synthetic lifestyle dataset."""
        np.random.seed(config.RANDOM_STATE)
        n = 100
        X = pd.DataFrame({
            "chronological_age": np.random.uniform(20, 80, n),
            "bmi": np.random.normal(27, 5, n),
            "sleep_hours": np.random.normal(7, 1, n),
            "sleep_quality": np.random.randint(1, 6, n),
            "weekly_exercise_sessions": np.random.randint(0, 8, n),
            "diet_quality_score": np.random.randint(1, 11, n),
            "stress_level": np.random.randint(1, 11, n),
            "sex": np.random.choice(["male", "female"], n),
            "physical_activity_level": np.random.choice(["low", "moderate", "high"], n),
            "smoking_status": np.random.choice(["never", "former", "current"], n),
            "alcohol_intake_frequency": np.random.choice(["never", "monthly", "weekly", "daily"], n),
            "has_hypertension": np.random.binomial(1, 0.25, n).astype(bool),
            "has_diabetes": np.random.binomial(1, 0.10, n).astype(bool),
        })
        y = np.random.normal(50, 10, n)
        return X, y

    def test_lifestyle_regressor_fit(self, synthetic_lifestyle_data):
        """Test that regressor fits without error."""
        X, y = synthetic_lifestyle_data
        model = LifestyleRegressor(n_estimators=10, random_state=config.RANDOM_STATE)
        model.fit(X, y)
        assert model.booster_ is not None
        assert model.preprocessor_ is not None

    def test_lifestyle_regressor_predict(self, synthetic_lifestyle_data):
        """Test that regressor predictions have correct shape."""
        X, y = synthetic_lifestyle_data
        model = LifestyleRegressor(n_estimators=10, random_state=config.RANDOM_STATE)
        model.fit(X, y)
        y_pred = model.predict(X)
        assert y_pred.shape[0] == X.shape[0]
        assert np.all(np.isfinite(y_pred))

    def test_lifestyle_regressor_with_validation(self, synthetic_lifestyle_data):
        """Test regressor training with validation set."""
        X, y = synthetic_lifestyle_data
        X_train, X_val = X.iloc[:70], X.iloc[70:]
        y_train, y_val = y[:70], y[70:]

        model = LifestyleRegressor(n_estimators=10, random_state=config.RANDOM_STATE)
        model.fit(X_train, y_train, X_val, y_val)
        y_pred = model.predict(X_val)
        assert y_pred.shape[0] == X_val.shape[0]

    def test_lifestyle_regressor_save_load(self, synthetic_lifestyle_data, tmp_path):
        """Test saving and loading the regressor."""
        X, y = synthetic_lifestyle_data
        model = LifestyleRegressor(n_estimators=10, random_state=config.RANDOM_STATE)
        model.fit(X, y)

        model_path = tmp_path / "test_model.joblib"
        model.save(model_path)

        loaded_model = LifestyleRegressor.load(model_path)
        y_pred_original = model.predict(X)
        y_pred_loaded = loaded_model.predict(X)

        np.testing.assert_array_almost_equal(y_pred_original, y_pred_loaded)
