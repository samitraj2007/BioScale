"""
Translation of SHAP values to interpretable "+years"/"-years" contributions.

This module provides utilities to transform raw SHAP values into human-readable
biological age contributions and feature display names.
"""

from bioscale import config


# Mapping of feature names to human-readable display names
FEATURE_DISPLAY_NAMES = {
    # Numeric features
    "chronological_age": "Chronological Age",
    "bmi": "Body Mass Index",
    "sleep_hours": "Sleep Duration",
    "sleep_quality": "Sleep Quality",
    "weekly_exercise_sessions": "Weekly Exercise Sessions",
    "diet_quality_score": "Diet Quality Score",
    "stress_level": "Stress Level",
    # Categorical features
    "sex": "Sex",
    "physical_activity_level": "Physical Activity Level",
    "smoking_status": "Smoking Status",
    "alcohol_intake_frequency": "Alcohol Intake Frequency",
    # Boolean features
    "has_hypertension": "Hypertension Status",
    "has_diabetes": "Diabetes Status",
}


def map_feature_names_for_display(feature_key: str) -> str:
    """
    Map internal feature keys to human-readable display names.

    Parameters
    ----------
    feature_key : str
        Internal feature name (e.g., "bmi").

    Returns
    -------
    str
        Human-readable display name (e.g., "Body Mass Index").
        If the key is not found in the mapping, returns the original key.
    """
    return FEATURE_DISPLAY_NAMES.get(feature_key, feature_key)


def translate_shap_to_years(
    baseline: float,
    shap_values: dict[str, float],
    chronological_age: float,
    top_k: int = 3,
) -> dict:
    """
    Translate SHAP values to biological age contributions in years.

    This function computes the predicted biological age as the sum of the
    baseline and all SHAP contributions, then identifies the top positive
    (aging) and negative (protective) contributors.

    Parameters
    ----------
    baseline : float
        Model baseline (expected value), typically the mean prediction.
    shap_values : dict[str, float]
        Dictionary mapping feature names to their SHAP contributions (in years).
    chronological_age : float
        The individual's chronological age in years.
    top_k : int, default=3
        Number of top positive and negative contributors to return.

    Returns
    -------
    dict
        Dictionary with keys:
        - "predicted_age": float, predicted biological age in years
        - "age_acceleration": float, predicted_age - chronological_age
        - "top_positive": list of dicts with keys:
            - "feature": original feature name
            - "display_name": human-readable feature name
            - "contribution_years": SHAP value in years
          (sorted descending by contribution_years)
        - "top_negative": list of dicts with keys:
            - "feature": original feature name
            - "display_name": human-readable feature name
            - "contribution_years": SHAP value in years
          (sorted ascending by contribution_years, i.e., most negative first)

    Notes
    -----
    - Only features with positive SHAP values are included in "top_positive".
    - Only features with negative SHAP values are included in "top_negative".
    - Each list is limited to at most `top_k` items.
    """
    # Compute predicted age
    predicted_age = baseline + sum(shap_values.values())
    age_acceleration = predicted_age - chronological_age

    # Separate positive and negative contributions
    positive_contributions = [
        (feature, shap_val)
        for feature, shap_val in shap_values.items()
        if shap_val > 0
    ]
    negative_contributions = [
        (feature, shap_val)
        for feature, shap_val in shap_values.items()
        if shap_val < 0
    ]

    # Sort and limit
    positive_contributions.sort(key=lambda x: x[1], reverse=True)
    negative_contributions.sort(key=lambda x: x[1])  # Most negative first

    top_positive = [
        {
            "feature": feature,
            "display_name": map_feature_names_for_display(feature),
            "contribution_years": float(shap_val),
        }
        for feature, shap_val in positive_contributions[:top_k]
    ]

    top_negative = [
        {
            "feature": feature,
            "display_name": map_feature_names_for_display(feature),
            "contribution_years": float(shap_val),
        }
        for feature, shap_val in negative_contributions[:top_k]
    ]

    return {
        "predicted_age": float(predicted_age),
        "age_acceleration": float(age_acceleration),
        "top_positive": top_positive,
        "top_negative": top_negative,
    }
