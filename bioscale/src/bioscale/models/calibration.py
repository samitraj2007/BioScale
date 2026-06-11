"""
Phenotypic age calibration.

This module turns user inputs into a stable, interpretable phenotypic age.

Why this exists
---------------
The survival model produces a relative mortality risk, and the lifestyle
regressor learns a risk-derived target. On their own those raw outputs are
poorly calibrated for direct display: the risk-to-age mapping is not anchored to
chronological age, so almost everyone collapses into a narrow (young) band, and
extreme/out-of-range inputs (e.g. age 99) extrapolate to nonsense such as a
phenotypic age of 35 with an age acceleration of -64 years.

The model used here
-------------------
We use a deliberately simple and explainable calibration, in the spirit of
phenotypic-age work (e.g. Levine PhenoAge) but not identical to it:

    phenotypic_age = clip(chronological_age + age_acceleration, AGE_FLOOR, AGE_CEIL)
    age_acceleration = clip(sum of per-feature health contributions, ACCEL_MIN, ACCEL_MAX)

Each lifestyle/clinical feature contributes a signed number of "years" relative
to a healthy reference profile (so an average-healthy person contributes ~0).
Unhealthy inputs add years (older); protective inputs subtract years (younger).
Everything is clamped to realistic bounds so extreme inputs cannot produce
absurd results.

This keeps the output:
  * anchored to chronological age (a typical person ~= their real age),
  * monotonic in health (unhealthier => older at the same age),
  * bounded (no -60 year accelerations),
  * and fully interpretable (the same contributions drive the "top drivers").
"""

from __future__ import annotations

from dataclasses import dataclass, field

from bioscale.explainability.translation import map_feature_names_for_display

# --- Realistic bounds -------------------------------------------------------
AGE_FLOOR = 18.0          # minimum phenotypic age we will report
AGE_CEIL = 110.0          # maximum phenotypic age we will report
CHRONO_MIN = 18.0         # chronological age is clamped into the modelled range
CHRONO_MAX = 100.0        # (e.g. a typed 150 becomes 100)
ACCEL_MIN = -30.0         # age acceleration is clamped to a sane interval
ACCEL_MAX = 30.0

# --- Healthy reference profile (contributes ~0 years) -----------------------
# These are the "neutral" values against which deviations are scored.
REF_BMI = 23.0
REF_SLEEP_HOURS = 7.5
REF_SLEEP_QUALITY = 3.0
REF_EXERCISE_SESSIONS = 3.0
REF_DIET_SCORE = 6.0
REF_STRESS = 4.0


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _as_float(value: object, default: float) -> float:
    try:
        if value is None:
            return default
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def _as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1", "y"}
    return False


def compute_contributions(features: dict) -> dict[str, float]:
    """
    Compute each feature's signed contribution to age acceleration, in years.

    Positive = pushes phenotypic age older; negative = younger. A healthy,
    average profile yields contributions that sum to roughly zero.

    Parameters
    ----------
    features : dict
        Raw request features (lifestyle, clinical, demographic). Missing keys
        fall back to the healthy reference values.

    Returns
    -------
    dict[str, float]
        Mapping of feature name -> contribution in years.
    """
    contrib: dict[str, float] = {}

    # BMI: U-shaped — penalise both overweight (>25) and underweight (<18.5).
    bmi = _as_float(features.get("bmi"), REF_BMI)
    contrib["bmi"] = 0.35 * max(0.0, bmi - 25.0) + 0.20 * max(0.0, 18.5 - bmi)

    # Sleep duration: penalise too little (<6.5h) or too much (>8.5h).
    sleep = _as_float(features.get("sleep_hours"), REF_SLEEP_HOURS)
    contrib["sleep_hours"] = 0.8 * max(0.0, 6.5 - sleep) + 0.6 * max(0.0, sleep - 8.5)

    # Sleep quality (1-5, higher is better): each point off the reference ~1.2y.
    sleep_q = _as_float(features.get("sleep_quality"), REF_SLEEP_QUALITY)
    contrib["sleep_quality"] = (REF_SLEEP_QUALITY - sleep_q) * 1.2

    # Weekly exercise sessions (0-7): fewer than reference adds years.
    sessions = _as_float(features.get("weekly_exercise_sessions"), REF_EXERCISE_SESSIONS)
    contrib["weekly_exercise_sessions"] = (REF_EXERCISE_SESSIONS - sessions) * 0.9

    # Diet quality (1-10, higher is better).
    diet = _as_float(features.get("diet_quality_score"), REF_DIET_SCORE)
    contrib["diet_quality_score"] = (REF_DIET_SCORE - diet) * 0.7

    # Stress (1-10, higher is worse).
    stress = _as_float(features.get("stress_level"), REF_STRESS)
    contrib["stress_level"] = (stress - REF_STRESS) * 0.8

    # Physical activity level.
    activity = str(features.get("physical_activity_level", "moderate")).lower()
    contrib["physical_activity_level"] = {
        "low": 4.0,
        "moderate": 0.0,
        "high": -3.0,
    }.get(activity, 0.0)

    # Smoking status (a strong driver).
    smoking = str(features.get("smoking_status", "never")).lower()
    contrib["smoking_status"] = {
        "never": 0.0,
        "former": 2.0,
        "current": 8.0,
    }.get(smoking, 0.0)

    # Alcohol intake frequency.
    alcohol = str(features.get("alcohol_intake_frequency", "never")).lower()
    contrib["alcohol_intake_frequency"] = {
        "never": 0.0,
        "monthly": 0.0,
        "weekly": 1.0,
        "daily": 5.0,
    }.get(alcohol, 0.0)

    # Diagnosed conditions.
    contrib["has_hypertension"] = 4.0 if _as_bool(features.get("has_hypertension")) else 0.0
    contrib["has_diabetes"] = 6.0 if _as_bool(features.get("has_diabetes")) else 0.0

    # Sex (small effect; females have a modest longevity advantage on average).
    sex = str(features.get("sex", "unknown")).lower()
    contrib["sex"] = -1.0 if sex == "female" else 0.0

    # Round to avoid noisy -0.0 / long floats in the response.
    return {k: round(v, 4) for k, v in contrib.items()}


@dataclass
class CalibrationResult:
    """Calibrated, bounded phenotypic age output."""

    chronological_age: float
    phenotypic_age: float
    age_acceleration: float
    contributions: dict[str, float] = field(default_factory=dict)


def calibrate_phenotypic_age(chronological_age: object, features: dict) -> CalibrationResult:
    """
    Compute a calibrated, bounded phenotypic age from request features.

    Parameters
    ----------
    chronological_age : float-like
        The user's chronological age (clamped into [CHRONO_MIN, CHRONO_MAX]).
    features : dict
        The full request features (used for the health contributions).

    Returns
    -------
    CalibrationResult
        chronological_age (clamped), phenotypic_age, age_acceleration, and the
        per-feature contributions used.
    """
    # Clamp the chronological age into the modelled range [18, 100] *for
    # modeling only*. This is the single source of truth for the reported
    # chronological age: it is never rounded, floored, or reconstructed from
    # phenotypic_age/acceleration (that previously caused off-by-one display,
    # e.g. input 25 -> 24). Formatting is left entirely to the frontend.
    age_for_model = _clamp(_as_float(chronological_age, 50.0), CHRONO_MIN, CHRONO_MAX)

    contributions = compute_contributions(features)
    raw_acceleration = sum(contributions.values())
    acceleration = _clamp(raw_acceleration, ACCEL_MIN, ACCEL_MAX)

    phenotypic_age = _clamp(age_for_model + acceleration, AGE_FLOOR, AGE_CEIL)
    # Recompute acceleration from the (clamped) phenotypic age and age_for_model
    # so that age_acceleration == phenotypic_age - chronological_age holds
    # exactly with the values returned below.
    acceleration = phenotypic_age - age_for_model

    return CalibrationResult(
        chronological_age=float(age_for_model),
        phenotypic_age=float(phenotypic_age),
        age_acceleration=float(acceleration),
        contributions=contributions,
    )


def top_drivers(
    contributions: dict[str, float],
    top_k: int = 3,
    threshold: float = 0.05,
) -> tuple[list[dict], list[dict]]:
    """
    Split contributions into the top positive (aging) and negative (protective)
    drivers, formatted for the API's `shap_contributions` field.

    Returns
    -------
    (top_positive, top_negative) : tuple of lists of dicts
        Each dict has feature, display_name, contribution_years.
    """

    def fmt(items: list[tuple[str, float]]) -> list[dict]:
        return [
            {
                "feature": feature,
                "display_name": map_feature_names_for_display(feature),
                "contribution_years": round(float(value), 2),
            }
            for feature, value in items
        ]

    positives = sorted(
        [(f, v) for f, v in contributions.items() if v > threshold],
        key=lambda kv: kv[1],
        reverse=True,
    )
    negatives = sorted(
        [(f, v) for f, v in contributions.items() if v < -threshold],
        key=lambda kv: kv[1],
    )
    return fmt(positives[:top_k]), fmt(negatives[:top_k])
