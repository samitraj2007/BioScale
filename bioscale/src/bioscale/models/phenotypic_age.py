"""
Phenotypic Age module for engineering biological age targets.

This module builds a Phenotypic Age-like target from survival models.
The implementation is calibrated on NHANES-style data using Cox PH models
and a deterministic risk-to-age mapping.

Note: This is an engineered target, not an exact replication of published
Phenotypic Age coefficients (e.g., Levine et al. 2018).
"""

import numpy as np
import pandas as pd
from lifelines import CoxPHFitter

from bioscale.models.survival import fit_cox_model, predict_risk


def compute_linear_predictor(cox_model: CoxPHFitter, df_features: pd.DataFrame) -> np.ndarray:
    """
    Compute the linear predictor (log hazard) from a Cox model.

    Parameters
    ----------
    cox_model : CoxPHFitter
        Fitted Cox model.
    df_features : pd.DataFrame
        Feature DataFrame.

    Returns
    -------
    np.ndarray
        Linear predictor values (log hazard ratio relative to baseline).
    """
    partial_hazard = cox_model.predict_partial_hazard(df_features)
    log_hazard = np.log(partial_hazard)
    return log_hazard


def mortality_risk_to_age(
    risk: np.ndarray,
    mapping_params: dict | None = None,
) -> np.ndarray:
    """
    Transform mortality risk (0-1) to a Phenotypic Age-like value in years.

    A simple monotonic mapping: if risk is near 0 (low mortality), age is young;
    if risk is near 1 (high mortality), age is old. This uses a linear transform
    scaled to a reasonable age range (typically 20-100 years).

    Note
    ----
    This is an absolute (non-age-anchored) mapping. Because most people have a
    low 10-year mortality risk, it compresses nearly everyone into a narrow
    young band, so the resulting target has little relationship to chronological
    age. Prefer :func:`risk_to_age_anchored` for a target that stays anchored to
    chronological age. Kept for backward compatibility.

    Parameters
    ----------
    risk : np.ndarray
        Array of mortality risk scores (0-1 scale).
    mapping_params : dict | None, default=None
        Optional dictionary with 'age_min', 'age_max' for scaling.
        Default: {'age_min': 20, 'age_max': 100}.

    Returns
    -------
    np.ndarray
        Phenotypic Age in years.
    """
    if mapping_params is None:
        mapping_params = {"age_min": 20, "age_max": 100}

    age_min = mapping_params["age_min"]
    age_max = mapping_params["age_max"]

    risk = np.clip(risk, 0.0, 1.0)
    phenotypic_age = age_min + risk * (age_max - age_min)

    return phenotypic_age


def risk_to_age_anchored(
    risk: np.ndarray,
    chronological_age: np.ndarray,
    accel_scale_years: float = 12.0,
    accel_cap_years: float = 30.0,
    age_floor: float = 18.0,
    age_ceil: float = 110.0,
) -> np.ndarray:
    """
    Map mortality risk to phenotypic age, anchored to chronological age.

    Instead of mapping the whole population's risk onto a fixed [20, 100] band
    (which collapses everyone into a narrow range), this expresses phenotypic
    age as::

        phenotypic_age = clip(chronological_age + age_acceleration, floor, ceil)
        age_acceleration = clip(accel_scale_years * z, -cap, +cap)

    where ``z`` is the standardized (mean 0, std 1) mortality risk across the
    cohort. A person with average risk for the cohort gets ~0 acceleration
    (phenotypic age ~= chronological age); higher risk reads as modestly older,
    lower risk as modestly younger. Bounds keep the target realistic.

    Parameters
    ----------
    risk : np.ndarray
        Mortality risk scores.
    chronological_age : np.ndarray
        Chronological ages, aligned with ``risk``.
    accel_scale_years : float, default=12.0
        Years of acceleration per 1 standard deviation of risk.
    accel_cap_years : float, default=30.0
        Maximum absolute acceleration.
    age_floor, age_ceil : float
        Bounds on the returned phenotypic age.

    Returns
    -------
    np.ndarray
        Age-anchored, bounded phenotypic age in years.
    """
    risk = np.asarray(risk, dtype=float)
    chronological_age = np.asarray(chronological_age, dtype=float)

    std = risk.std()
    z = (risk - risk.mean()) / (std + 1e-8)

    acceleration = np.clip(accel_scale_years * z, -accel_cap_years, accel_cap_years)
    phenotypic_age = np.clip(chronological_age + acceleration, age_floor, age_ceil)
    return phenotypic_age


def build_phenotypic_age_target(
    df_stage1: pd.DataFrame,
    feature_cols: list[str],
) -> pd.Series:
    """
    Build a Phenotypic Age-like target from Stage 1 survival data.

    This function:
    1. Fits a Cox PH model using duration_months and event (mortality).
    2. Computes 10-year mortality risk for each individual.
    3. Maps risk to a Phenotypic Age-like value in years.

    Parameters
    ----------
    df_stage1 : pd.DataFrame
        DataFrame with columns: duration_months, event, and feature_cols.
    feature_cols : list[str]
        Names of biomarker columns to use in the Cox model.

    Returns
    -------
    pd.Series
        Phenotypic Age in years (indexed by df_stage1.index).

    Notes
    -----
    This is an engineered Phenotypic Age-like target calibrated on NHANES-style data,
    not an exact replication of published Phenotypic Age coefficients.
    """
    cox_model = fit_cox_model(
        df_stage1,
        duration_col="duration_months",
        event_col="event",
        feature_cols=feature_cols,
    )

    risk = predict_risk(cox_model, df_stage1[feature_cols], horizon_years=10.0)
    phenotypic_age = mortality_risk_to_age(risk)

    return pd.Series(phenotypic_age, index=df_stage1.index, name="phenotypic_age")
