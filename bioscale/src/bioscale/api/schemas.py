"""
Pydantic models for API request/response validation.

Defines the JSON schemas for the lifestyle prediction API.
"""

from typing import Literal
from pydantic import BaseModel, Field


class LifestyleRequest(BaseModel):
    """
    Request schema for biological age prediction.

    All fields must be provided and must satisfy the field constraints.
    """

    chronological_age: float = Field(..., gt=0, description="Age in years (must be > 0)")
    sex: Literal["male", "female", "other", "unknown"] = Field(
        ..., description="Biological sex"
    )
    bmi: float = Field(..., gt=0, description="Body Mass Index (must be > 0)")
    sleep_hours: float = Field(
        ..., ge=0, le=24, description="Sleep duration per night in hours"
    )
    sleep_quality: int = Field(..., ge=1, le=5, description="Sleep quality (1-5 Likert)")
    physical_activity_level: Literal["low", "moderate", "high"] = Field(
        ..., description="Physical activity level"
    )
    weekly_exercise_sessions: int = Field(
        ..., ge=0, le=7, description="Number of exercise sessions per week"
    )
    smoking_status: Literal["never", "former", "current"] = Field(
        ..., description="Smoking status"
    )
    alcohol_intake_frequency: Literal["never", "monthly", "weekly", "daily"] = Field(
        ..., description="Frequency of alcohol consumption"
    )
    diet_quality_score: int = Field(
        ..., ge=1, le=10, description="Diet quality score (1-10)"
    )
    stress_level: int = Field(..., ge=1, le=10, description="Stress level (1-10)")
    has_hypertension: bool = Field(..., description="Hypertension diagnosis status")
    has_diabetes: bool = Field(..., description="Diabetes diagnosis status")

    model_config = {
        "json_schema_extra": {
            "example": {
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
        }
    }


class ShapContribution(BaseModel):
    """
    Represents a single SHAP feature contribution to age prediction.

    Attributes:
        feature: Internal feature name
        display_name: Human-readable feature name
        contribution_years: SHAP value translated to years
    """

    feature: str = Field(..., description="Internal feature identifier")
    display_name: str = Field(..., description="Human-readable feature name")
    contribution_years: float = Field(
        ..., description="Contribution to biological age in years"
    )


class ShapSummary(BaseModel):
    """
    Summary of top SHAP contributions for interpretability.

    Attributes:
        top_positive: Features contributing to older biological age
        top_negative: Features contributing to younger biological age
    """

    top_positive: list[ShapContribution] = Field(
        ..., description="Top aging contributors (positive SHAP values)"
    )
    top_negative: list[ShapContribution] = Field(
        ..., description="Top protective contributors (negative SHAP values)"
    )


class LifestyleResponse(BaseModel):
    """
    Response schema for biological age prediction.

    Includes predicted age, age acceleration, and feature importance explanations.
    """

    chronological_age: float = Field(
        ..., description="Input chronological age in years"
    )
    predicted_biological_age: float = Field(
        ..., description="Predicted biological age in years"
    )
    age_acceleration: float = Field(
        ..., description="Difference between predicted and chronological age (in years)"
    )
    model_version: str = Field(..., description="Version of the prediction model")
    shap_contributions: ShapSummary = Field(
        ..., description="Feature contribution summary for explainability"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "chronological_age": 45.0,
                "predicted_biological_age": 48.5,
                "age_acceleration": 3.5,
                "model_version": "v1.0.0",
                "shap_contributions": {
                    "top_positive": [
                        {
                            "feature": "bmi",
                            "display_name": "Body Mass Index",
                            "contribution_years": 2.1,
                        }
                    ],
                    "top_negative": [
                        {
                            "feature": "sleep_hours",
                            "display_name": "Sleep Duration",
                            "contribution_years": -1.8,
                        }
                    ],
                },
            }
        }
    }
