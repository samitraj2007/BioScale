"""
Tests for the SHAP explainability engine and translation utilities.

This module contains unit tests for the explainability module, using small
synthetic datasets to verify SHAP value computation and interpretation.
"""

import numpy as np
import pandas as pd
import pytest

from bioscale import config
from bioscale.explainability.shap_engine import ShapExplainer
from bioscale.explainability.translation import (
    map_feature_names_for_display,
    translate_shap_to_years,
)
from bioscale.models.lifestyle_regressor import LifestyleRegressor


class TestShapExplainer:
    """Tests for the ShapExplainer class."""

    @pytest.fixture
    def simple_model_and_explainer(self):
        """Create a simple trained model and ShapExplainer for testing."""
        np.random.seed(config.RANDOM_STATE)

        # Create tiny synthetic training data
        n_train = 30
        X_train = pd.DataFrame({
            "chronological_age": np.random.uniform(20, 80, n_train),
            "bmi": np.random.normal(27, 5, n_train),
            "sleep_hours": np.random.uniform(4, 12, n_train),
            "sleep_quality": np.random.randint(1, 6, n_train),
            "weekly_exercise_sessions": np.random.randint(0, 8, n_train),
            "diet_quality_score": np.random.randint(1, 11, n_train),
            "stress_level": np.random.randint(1, 11, n_train),
            "sex": np.random.choice(["male", "female"], n_train),
            "physical_activity_level": np.random.choice(
                ["low", "moderate", "high"], n_train
            ),
            "smoking_status": np.random.choice(
                ["never", "former", "current"], n_train
            ),
            "alcohol_intake_frequency": np.random.choice(
                ["never", "monthly", "weekly", "daily"], n_train
            ),
            "has_hypertension": np.random.binomial(1, 0.25, n_train).astype(bool),
            "has_diabetes": np.random.binomial(1, 0.10, n_train).astype(bool),
        })

        y_train = np.random.normal(50, 10, n_train)

        # Train model
        model = LifestyleRegressor(
            n_estimators=10,
            max_depth=3,
            random_state=config.RANDOM_STATE,
        )
        model.fit(X_train, y_train)

        # Create explainer (automatically generates preprocessed feature names)
        explainer = ShapExplainer(model)

        return model, explainer, X_train

    def test_shap_explainer_initialization(self, simple_model_and_explainer):
        """Test that ShapExplainer initializes without error."""
        model, explainer, _ = simple_model_and_explainer
        assert explainer.model is model
        assert len(explainer.preprocessed_feature_names) > 0
        assert explainer.explainer is not None

    def test_explain_instance_returns_dict(self, simple_model_and_explainer):
        """Test that explain_instance returns proper dict structure."""
        model, explainer, X_train = simple_model_and_explainer

        # Test on first row (must be preprocessed through the model's preprocessor)
        X_test = X_train.iloc[:1]
        X_test_preprocessed = model.preprocessor_.transform(X_test)
        result = explainer.explain_instance(X_test_preprocessed)

        assert isinstance(result, dict)
        assert "baseline" in result
        assert "shap_values" in result
        assert isinstance(result["baseline"], float)
        assert isinstance(result["shap_values"], dict)

    def test_explain_instance_shap_values_shape(self, simple_model_and_explainer):
        """Test that SHAP values have correct shape."""
        model, explainer, X_train = simple_model_and_explainer

        X_test = X_train.iloc[:1]
        X_test_preprocessed = model.preprocessor_.transform(X_test)
        result = explainer.explain_instance(X_test_preprocessed)

        assert len(result["shap_values"]) == len(explainer.preprocessed_feature_names)

        # All SHAP values should be floats
        for feature_name, shap_val in result["shap_values"].items():
            assert isinstance(feature_name, str)
            assert isinstance(shap_val, (float, np.floating))

    def test_explain_instance_deterministic(self, simple_model_and_explainer):
        """Test that explain_instance is deterministic."""
        model, explainer, X_train = simple_model_and_explainer

        X_test = X_train.iloc[:1]
        X_test_preprocessed = model.preprocessor_.transform(X_test)

        result1 = explainer.explain_instance(X_test_preprocessed)
        result2 = explainer.explain_instance(X_test_preprocessed)

        # Results should be identical
        assert result1["baseline"] == result2["baseline"]
        for feature in result1["shap_values"]:
            assert result1["shap_values"][feature] == result2["shap_values"][feature]

    def test_explain_instance_with_dataframe(self, simple_model_and_explainer):
        """Test that explain_instance works with DataFrame input."""
        model, explainer, X_train = simple_model_and_explainer

        X_test = X_train.iloc[:1]
        X_test_preprocessed = model.preprocessor_.transform(X_test)
        result = explainer.explain_instance(X_test_preprocessed)

        assert isinstance(result, dict)
        assert "baseline" in result
        assert "shap_values" in result

    def test_explain_instance_single_value_vs_array(self, simple_model_and_explainer):
        """Test that 1D and 2D inputs produce same results."""
        model, explainer, X_train = simple_model_and_explainer

        X_test = X_train.iloc[:1]
        X_test_preprocessed = model.preprocessor_.transform(X_test)
        result_2d = explainer.explain_instance(X_test_preprocessed)

        X_test_1d = X_test_preprocessed[0]
        result_1d = explainer.explain_instance(X_test_1d)

        # Should produce identical results
        assert result_2d["baseline"] == result_1d["baseline"]
        for feature in result_2d["shap_values"]:
            assert (
                result_2d["shap_values"][feature]
                == result_1d["shap_values"][feature]
            )


class TestTranslation:
    """Tests for translation utilities."""

    def test_map_feature_names_for_display_known(self):
        """Test mapping for known features."""
        assert map_feature_names_for_display("bmi") == "Body Mass Index"
        assert map_feature_names_for_display("sleep_hours") == "Sleep Duration"
        assert map_feature_names_for_display("has_diabetes") == "Diabetes Status"

    def test_map_feature_names_for_display_unknown(self):
        """Test mapping for unknown features returns original."""
        unknown_feature = "unknown_feature_xyz"
        assert map_feature_names_for_display(unknown_feature) == unknown_feature

    def test_translate_shap_to_years_structure(self):
        """Test that translate_shap_to_years returns correct structure."""
        baseline = 50.0
        shap_values = {
            "bmi": 3.5,
            "sleep_hours": -2.1,
            "stress_level": 1.5,
            "diet_quality_score": -0.5,
        }
        chronological_age = 40.0

        result = translate_shap_to_years(baseline, shap_values, chronological_age)

        assert isinstance(result, dict)
        assert "predicted_age" in result
        assert "age_acceleration" in result
        assert "top_positive" in result
        assert "top_negative" in result

    def test_translate_shap_to_years_predicted_age(self):
        """Test that predicted_age is computed correctly."""
        baseline = 50.0
        shap_values = {
            "bmi": 3.0,
            "sleep_hours": -1.0,
            "stress_level": 2.0,
        }
        chronological_age = 40.0

        result = translate_shap_to_years(baseline, shap_values, chronological_age)

        expected_predicted_age = baseline + sum(shap_values.values())
        assert result["predicted_age"] == expected_predicted_age

    def test_translate_shap_to_years_age_acceleration(self):
        """Test that age_acceleration is computed correctly."""
        baseline = 50.0
        shap_values = {
            "bmi": 3.0,
            "sleep_hours": -1.0,
        }
        chronological_age = 40.0

        result = translate_shap_to_years(baseline, shap_values, chronological_age)

        expected_acceleration = result["predicted_age"] - chronological_age
        assert result["age_acceleration"] == expected_acceleration

    def test_translate_shap_to_years_positive_only(self):
        """Test separation of positive contributions."""
        baseline = 50.0
        shap_values = {
            "bmi": 5.0,
            "stress_level": 3.0,
            "diet_quality_score": 1.5,
        }
        chronological_age = 40.0

        result = translate_shap_to_years(baseline, shap_values, chronological_age)

        assert len(result["top_positive"]) == 3
        assert len(result["top_negative"]) == 0

        # Check that positive contributions are sorted descending
        contributions = [item["contribution_years"] for item in result["top_positive"]]
        assert contributions == sorted(contributions, reverse=True)

    def test_translate_shap_to_years_negative_only(self):
        """Test separation of negative contributions."""
        baseline = 50.0
        shap_values = {
            "sleep_hours": -5.0,
            "weekly_exercise_sessions": -2.0,
            "alcohol_intake_frequency": -1.5,
        }
        chronological_age = 40.0

        result = translate_shap_to_years(baseline, shap_values, chronological_age)

        assert len(result["top_positive"]) == 0
        assert len(result["top_negative"]) == 3

        # Check that negative contributions are sorted ascending (most negative first)
        contributions = [item["contribution_years"] for item in result["top_negative"]]
        assert contributions == sorted(contributions)

    def test_translate_shap_to_years_mixed(self):
        """Test with both positive and negative contributions."""
        baseline = 50.0
        shap_values = {
            "bmi": 5.0,
            "sleep_hours": -3.0,
            "stress_level": 2.0,
            "diet_quality_score": -1.0,
        }
        chronological_age = 40.0

        result = translate_shap_to_years(baseline, shap_values, chronological_age)

        assert len(result["top_positive"]) == 2
        assert len(result["top_negative"]) == 2

    def test_translate_shap_to_years_top_k(self):
        """Test that top_k parameter limits results."""
        baseline = 50.0
        shap_values = {
            "bmi": 5.0,
            "stress_level": 3.0,
            "diet_quality_score": 2.0,
            "sleep_hours": -4.0,
            "weekly_exercise_sessions": -2.0,
            "alcohol_intake_frequency": -1.0,
        }
        chronological_age = 40.0

        result = translate_shap_to_years(baseline, shap_values, chronological_age, top_k=2)

        assert len(result["top_positive"]) == 2
        assert len(result["top_negative"]) == 2

    def test_translate_shap_to_years_top_positive_sorted(self):
        """Test that top_positive is sorted descending."""
        baseline = 50.0
        shap_values = {
            "bmi": 2.0,
            "stress_level": 5.0,
            "diet_quality_score": 3.0,
        }
        chronological_age = 40.0

        result = translate_shap_to_years(baseline, shap_values, chronological_age)

        contributions = [item["contribution_years"] for item in result["top_positive"]]
        assert contributions == sorted(contributions, reverse=True)
        assert contributions[0] == 5.0

    def test_translate_shap_to_years_top_negative_sorted(self):
        """Test that top_negative is sorted ascending (most negative first)."""
        baseline = 50.0
        shap_values = {
            "sleep_hours": -1.0,
            "weekly_exercise_sessions": -5.0,
            "alcohol_intake_frequency": -3.0,
        }
        chronological_age = 40.0

        result = translate_shap_to_years(baseline, shap_values, chronological_age)

        contributions = [item["contribution_years"] for item in result["top_negative"]]
        assert contributions == sorted(contributions)
        assert contributions[0] == -5.0

    def test_translate_shap_to_years_display_names(self):
        """Test that display names are properly mapped."""
        baseline = 50.0
        shap_values = {
            "bmi": 3.0,
            "sleep_hours": -2.0,
        }
        chronological_age = 40.0

        result = translate_shap_to_years(baseline, shap_values, chronological_age)

        # Check positive
        for item in result["top_positive"]:
            assert "feature" in item
            assert "display_name" in item
            assert "contribution_years" in item
            assert isinstance(item["display_name"], str)
            assert len(item["display_name"]) > 0

        # Check negative
        for item in result["top_negative"]:
            assert "feature" in item
            assert "display_name" in item
            assert "contribution_years" in item
            assert isinstance(item["display_name"], str)
            assert len(item["display_name"]) > 0


class TestExplainerIntegration:
    """Integration tests between ShapExplainer and translation."""

    @pytest.fixture
    def model_explainer_and_data(self):
        """Create model, explainer, and test data."""
        np.random.seed(config.RANDOM_STATE)

        # Create small training data
        n_train = 30
        X_train = pd.DataFrame({
            "chronological_age": np.random.uniform(20, 80, n_train),
            "bmi": np.random.normal(27, 5, n_train),
            "sleep_hours": np.random.uniform(4, 12, n_train),
            "sleep_quality": np.random.randint(1, 6, n_train),
            "weekly_exercise_sessions": np.random.randint(0, 8, n_train),
            "diet_quality_score": np.random.randint(1, 11, n_train),
            "stress_level": np.random.randint(1, 11, n_train),
            "sex": np.random.choice(["male", "female"], n_train),
            "physical_activity_level": np.random.choice(
                ["low", "moderate", "high"], n_train
            ),
            "smoking_status": np.random.choice(
                ["never", "former", "current"], n_train
            ),
            "alcohol_intake_frequency": np.random.choice(
                ["never", "monthly", "weekly", "daily"], n_train
            ),
            "has_hypertension": np.random.binomial(1, 0.25, n_train).astype(bool),
            "has_diabetes": np.random.binomial(1, 0.10, n_train).astype(bool),
        })

        y_train = np.random.normal(50, 10, n_train)

        model = LifestyleRegressor(
            n_estimators=10,
            max_depth=3,
            random_state=config.RANDOM_STATE,
        )
        model.fit(X_train, y_train)

        explainer = ShapExplainer(model)

        return model, explainer, X_train

    def test_end_to_end_explanation(self, model_explainer_and_data):
        """Test full explanation pipeline from model to translated results."""
        model, explainer, X_train = model_explainer_and_data
        chronological_age = 45.0

        # Get SHAP explanation (use preprocessed data)
        X_test = X_train.iloc[:1]
        X_test_preprocessed = model.preprocessor_.transform(X_test)
        shap_result = explainer.explain_instance(X_test_preprocessed)

        # Translate to years
        translated = translate_shap_to_years(
            baseline=shap_result["baseline"],
            shap_values=shap_result["shap_values"],
            chronological_age=chronological_age,
        )

        # Verify structure
        assert translated["predicted_age"] > 0
        assert isinstance(translated["age_acceleration"], float)
        assert isinstance(translated["top_positive"], list)
        assert isinstance(translated["top_negative"], list)

    def test_baseline_plus_shap_equals_prediction(self, model_explainer_and_data):
        """Test that baseline + SHAP sum equals the predicted age."""
        model, explainer, X_train = model_explainer_and_data

        X_test = X_train.iloc[:1]
        model_pred = model.predict(X_test)[0]

        X_test_preprocessed = model.preprocessor_.transform(X_test)
        shap_result = explainer.explain_instance(X_test_preprocessed)
        baseline = shap_result["baseline"]
        shap_sum = sum(shap_result["shap_values"].values())

        # They should be approximately equal (within floating point tolerance)
        np.testing.assert_allclose(baseline + shap_sum, model_pred, rtol=1e-5)
