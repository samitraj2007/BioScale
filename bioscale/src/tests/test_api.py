"""
API endpoint tests for the BioScale FastAPI application.

Tests the health endpoint, prediction endpoint, and response schemas
using mocked model and explainer.
"""

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from bioscale import config
from bioscale.api.main import app
from bioscale.explainability.shap_engine import ShapExplainer
from bioscale.models.lifestyle_regressor import LifestyleRegressor


@pytest.fixture
def toy_model():
    """Create a tiny trained model for testing."""
    np.random.seed(config.RANDOM_STATE)

    # Create small synthetic training data
    n = 30
    X_train = pd.DataFrame({
        "chronological_age": np.random.uniform(20, 80, n),
        "bmi": np.random.normal(27, 5, n),
        "sleep_hours": np.random.uniform(4, 12, n),
        "sleep_quality": np.random.randint(1, 6, n),
        "weekly_exercise_sessions": np.random.randint(0, 8, n),
        "diet_quality_score": np.random.randint(1, 11, n),
        "stress_level": np.random.randint(1, 11, n),
        "sex": np.random.choice(["male", "female"], n),
        "physical_activity_level": np.random.choice(
            ["low", "moderate", "high"], n
        ),
        "smoking_status": np.random.choice(
            ["never", "former", "current"], n
        ),
        "alcohol_intake_frequency": np.random.choice(
            ["never", "monthly", "weekly", "daily"], n
        ),
        "has_hypertension": np.random.binomial(1, 0.25, n).astype(bool),
        "has_diabetes": np.random.binomial(1, 0.10, n).astype(bool),
    })
    y_train = np.random.normal(50, 10, n)

    # Train model
    model = LifestyleRegressor(
        n_estimators=10,
        max_depth=3,
        random_state=config.RANDOM_STATE,
    )
    model.fit(X_train, y_train)

    return model


@pytest.fixture
def toy_explainer(toy_model):
    """Create a SHAP explainer for the toy model."""
    return ShapExplainer(toy_model)


@pytest.fixture
def client(toy_model, toy_explainer, monkeypatch):
    """Create a FastAPI test client with mocked dependencies."""
    # Monkeypatch the dependency injection functions
    from bioscale.api import dependencies

    monkeypatch.setattr(dependencies, "get_lifestyle_model", lambda: toy_model)
    monkeypatch.setattr(dependencies, "get_shap_explainer", lambda: toy_explainer)

    return TestClient(app)


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_endpoint_status(self, client):
        """Test that /health returns 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_endpoint_response(self, client):
        """Test that /health returns correct JSON structure."""
        response = client.get("/health")
        data = response.json()

        assert "status" in data
        assert "model_version" in data
        assert data["status"] == "ok"
        assert isinstance(data["model_version"], str)


class TestPredictEndpoint:
    """Tests for the /predict endpoint."""

    @pytest.fixture
    def valid_request_data(self):
        """Valid request payload."""
        return {
            "chronological_age": 45.0,
            "sex": "male",
            "bmi": 26.5,
            "sleep_hours": 7.0,
            "sleep_quality": 4,
            "physical_activity_level": "moderate",
            "weekly_exercise_sessions": 3,
            "smoking_status": "never",
            "alcohol_intake_frequency": "weekly",
            "diet_quality_score": 7,
            "stress_level": 5,
            "has_hypertension": False,
            "has_diabetes": False,
        }

    def test_predict_endpoint_status(self, client, valid_request_data):
        """Test that /predict returns 200 for valid input."""
        response = client.post("/predict", json=valid_request_data)
        assert response.status_code == 200

    def test_predict_response_schema(self, client, valid_request_data):
        """Test that /predict response has correct schema."""
        response = client.post("/predict", json=valid_request_data)
        data = response.json()

        # Check required top-level keys
        assert "chronological_age" in data
        assert "predicted_biological_age" in data
        assert "age_acceleration" in data
        assert "model_version" in data
        assert "shap_contributions" in data

        # Check types
        assert isinstance(data["chronological_age"], float)
        assert isinstance(data["predicted_biological_age"], float)
        assert isinstance(data["age_acceleration"], float)
        assert isinstance(data["model_version"], str)

        # Check shap_contributions structure
        shap_contrib = data["shap_contributions"]
        assert "top_positive" in shap_contrib
        assert "top_negative" in shap_contrib
        assert isinstance(shap_contrib["top_positive"], list)
        assert isinstance(shap_contrib["top_negative"], list)

    def test_predict_response_values(self, client, valid_request_data):
        """Test that /predict response values are sensible."""
        response = client.post("/predict", json=valid_request_data)
        data = response.json()

        # Check that predicted age is > 0
        assert data["predicted_biological_age"] > 0

        # Check that chronological_age matches input
        assert data["chronological_age"] == valid_request_data["chronological_age"]

        # Check that age_acceleration is a finite number
        # (It's computed from SHAP baseline, which may differ slightly from model prediction)
        assert isinstance(data["age_acceleration"], float)
        assert -200 < data["age_acceleration"] < 200  # Reasonable bounds

    def test_predict_shap_contributions_structure(self, client, valid_request_data):
        """Test that SHAP contributions have correct structure."""
        response = client.post("/predict", json=valid_request_data)
        data = response.json()

        for contribution in (
            data["shap_contributions"]["top_positive"]
            + data["shap_contributions"]["top_negative"]
        ):
            assert "feature" in contribution
            assert "display_name" in contribution
            assert "contribution_years" in contribution
            assert isinstance(contribution["feature"], str)
            assert isinstance(contribution["display_name"], str)
            assert isinstance(contribution["contribution_years"], float)

    def test_predict_invalid_missing_field(self, client):
        """Test that /predict returns 422 for missing required field."""
        invalid_data = {
            "chronological_age": 45.0,
            # Missing other required fields
        }
        response = client.post("/predict", json=invalid_data)
        assert response.status_code == 422

    def test_predict_invalid_out_of_range(self, client, valid_request_data):
        """Test that /predict returns 422 for out-of-range values."""
        # Invalid: chronological_age <= 0
        invalid_data = valid_request_data.copy()
        invalid_data["chronological_age"] = -5.0
        response = client.post("/predict", json=invalid_data)
        assert response.status_code == 422

    def test_predict_invalid_bad_enum(self, client, valid_request_data):
        """Test that /predict returns 422 for invalid enum values."""
        # Invalid sex value
        invalid_data = valid_request_data.copy()
        invalid_data["sex"] = "invalid_sex"
        response = client.post("/predict", json=invalid_data)
        assert response.status_code == 422

    def test_predict_invalid_bmi_negative(self, client, valid_request_data):
        """Test that /predict returns 422 for negative BMI."""
        invalid_data = valid_request_data.copy()
        invalid_data["bmi"] = -10.0
        response = client.post("/predict", json=invalid_data)
        assert response.status_code == 422

    def test_predict_invalid_sleep_hours_out_of_range(self, client, valid_request_data):
        """Test that /predict returns 422 for sleep_hours out of range."""
        invalid_data = valid_request_data.copy()
        invalid_data["sleep_hours"] = 25.0
        response = client.post("/predict", json=invalid_data)
        assert response.status_code == 422

    def test_predict_model_version_in_response(self, client, valid_request_data):
        """Test that response includes correct model version."""
        response = client.post("/predict", json=valid_request_data)
        data = response.json()
        assert data["model_version"] == config.MODEL_VERSION


class TestAPIIntegration:
    """Integration tests for the API."""

    @pytest.fixture
    def valid_request_data(self):
        """Valid request payload."""
        return {
            "chronological_age": 50.0,
            "sex": "female",
            "bmi": 25.0,
            "sleep_hours": 8.0,
            "sleep_quality": 5,
            "physical_activity_level": "high",
            "weekly_exercise_sessions": 5,
            "smoking_status": "never",
            "alcohol_intake_frequency": "never",
            "diet_quality_score": 9,
            "stress_level": 3,
            "has_hypertension": False,
            "has_diabetes": False,
        }

    def test_health_then_predict(self, client, valid_request_data):
        """Test calling health check followed by prediction."""
        # Health check
        health_response = client.get("/health")
        assert health_response.status_code == 200

        # Prediction
        predict_response = client.post("/predict", json=valid_request_data)
        assert predict_response.status_code == 200

        # Verify model version matches
        assert (
            health_response.json()["model_version"]
            == predict_response.json()["model_version"]
        )

    def test_multiple_predictions_consistent(self, client, valid_request_data):
        """Test that same input produces consistent predictions."""
        response1 = client.post("/predict", json=valid_request_data)
        response2 = client.post("/predict", json=valid_request_data)

        data1 = response1.json()
        data2 = response2.json()

        # Same input should produce same output
        assert (
            data1["predicted_biological_age"] == data2["predicted_biological_age"]
        )
        assert data1["age_acceleration"] == data2["age_acceleration"]
