"""
Survival analysis module using Cox Proportional Hazards model.

This module provides functions to fit Cox PH models and predict 10-year
mortality risk, which serves as the basis for the Phenotypic Age target.
"""

import numpy as np
import pandas as pd
from lifelines import CoxPHFitter


def fit_cox_model(
    df: pd.DataFrame,
    duration_col: str,
    event_col: str,
    feature_cols: list[str],
    penalizer: float = 0.1,
) -> CoxPHFitter:
    """
    Fit a Cox Proportional Hazards model.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing duration, event, and feature columns.
    duration_col : str
        Name of the duration column (typically duration_months).
    event_col : str
        Name of the event (mortality) indicator column (0/1).
    feature_cols : list[str]
        List of feature column names to use in the model.
    penalizer : float, default=0.1
        L2 penalization parameter for regularization.

    Returns
    -------
    CoxPHFitter
        Fitted Cox model.
    """
    cox_model = CoxPHFitter(penalizer=penalizer)
    cox_model.fit(
        df[[duration_col, event_col] + feature_cols],
        duration_col=duration_col,
        event_col=event_col,
    )
    return cox_model


def predict_risk(
    cox_model: CoxPHFitter,
    df_features: pd.DataFrame,
    horizon_years: float = 10.0,
) -> np.ndarray:
    """
    Predict cumulative mortality risk at a given time horizon.

    Parameters
    ----------
    cox_model : CoxPHFitter
        Fitted Cox model.
    df_features : pd.DataFrame
        Feature DataFrame (must contain the same columns used in training).
    horizon_years : float, default=10.0
        Time horizon in years for risk prediction.

    Returns
    -------
    np.ndarray
        Array of predicted 10-year risk scores (0-1 scale, typically).
    """
    horizon_months = horizon_years * 12
    risk_scores = cox_model.predict_survival_function(
        df_features, times=[horizon_months]
    ).values.flatten()
    cumulative_hazard = 1.0 - risk_scores
    return np.clip(cumulative_hazard, 0.0, 1.0)
