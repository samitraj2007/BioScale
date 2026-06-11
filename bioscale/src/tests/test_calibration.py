"""
Sanity tests for the phenotypic age calibration.

These guard against the previously-observed absurd behaviour (e.g. a sick
99-year-old returning a phenotypic age in the 30s with a -64 year acceleration).

They check that:
  * phenotypic age stays within [18, 110],
  * age acceleration stays within [-30, 30],
  * at the same chronological age, an unhealthy profile is older than a healthy
    one (unhealthy > neutral > healthy),
  * extreme / out-of-range inputs are clamped, not exploded.
"""

import pytest

from bioscale.models.calibration import (
    ACCEL_MAX,
    ACCEL_MIN,
    AGE_CEIL,
    AGE_FLOOR,
    calibrate_phenotypic_age,
)


def _profile(kind: str) -> dict:
    """Return a healthy / neutral / unhealthy feature profile."""
    if kind == "healthy":
        return {
            "sex": "female",
            "bmi": 22.0,
            "sleep_hours": 7.5,
            "sleep_quality": 5,
            "weekly_exercise_sessions": 6,
            "diet_quality_score": 9,
            "stress_level": 2,
            "physical_activity_level": "high",
            "smoking_status": "never",
            "alcohol_intake_frequency": "never",
            "has_hypertension": False,
            "has_diabetes": False,
        }
    if kind == "neutral":
        return {
            "sex": "male",
            "bmi": 23.0,
            "sleep_hours": 7.5,
            "sleep_quality": 3,
            "weekly_exercise_sessions": 3,
            "diet_quality_score": 6,
            "stress_level": 4,
            "physical_activity_level": "moderate",
            "smoking_status": "never",
            "alcohol_intake_frequency": "monthly",
            "has_hypertension": False,
            "has_diabetes": False,
        }
    # unhealthy
    return {
        "sex": "male",
        "bmi": 38.0,
        "sleep_hours": 4.5,
        "sleep_quality": 1,
        "weekly_exercise_sessions": 0,
        "diet_quality_score": 1,
        "stress_level": 10,
        "physical_activity_level": "low",
        "smoking_status": "current",
        "alcohol_intake_frequency": "daily",
        "has_hypertension": True,
        "has_diabetes": True,
    }


AGES = [30, 50, 70, 90]
KINDS = ["healthy", "neutral", "unhealthy"]


@pytest.mark.parametrize("age", AGES)
@pytest.mark.parametrize("kind", KINDS)
def test_outputs_within_bounds(age, kind):
    result = calibrate_phenotypic_age(age, _profile(kind))
    assert AGE_FLOOR <= result.phenotypic_age <= AGE_CEIL
    assert ACCEL_MIN - 1e-6 <= result.age_acceleration <= ACCEL_MAX + 1e-6


@pytest.mark.parametrize("age", AGES)
def test_unhealthy_older_than_healthy(age):
    healthy = calibrate_phenotypic_age(age, _profile("healthy"))
    neutral = calibrate_phenotypic_age(age, _profile("neutral"))
    unhealthy = calibrate_phenotypic_age(age, _profile("unhealthy"))
    assert unhealthy.phenotypic_age > neutral.phenotypic_age > healthy.phenotypic_age


def test_neutral_profile_close_to_chronological():
    for age in AGES:
        result = calibrate_phenotypic_age(age, _profile("neutral"))
        assert abs(result.age_acceleration) <= 2.0


def test_extreme_age_is_clamped():
    # A typed 150 should be treated as ~100, not extrapolated.
    result = calibrate_phenotypic_age(150, _profile("neutral"))
    assert result.chronological_age <= 100.0
    assert result.phenotypic_age <= AGE_CEIL


def test_sick_99_year_old_is_not_absurd():
    """The original bug: sick 99yo -> ~35 with -64 acceleration."""
    result = calibrate_phenotypic_age(99, _profile("unhealthy"))
    assert result.age_acceleration >= 0  # should read older, not -60
    assert result.phenotypic_age >= 90
    assert ACCEL_MIN <= result.age_acceleration <= ACCEL_MAX


def test_acceleration_consistent_with_ages():
    result = calibrate_phenotypic_age(55, _profile("unhealthy"))
    assert (
        abs(result.age_acceleration - (result.phenotypic_age - result.chronological_age))
        < 1e-6
    )
