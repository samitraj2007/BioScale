"""
Optuna-based hyperparameter optimization for the LifestyleRegressor.

This module provides functions to search for optimal hyperparameters
for the XGBoost lifestyle regressor using Optuna.
"""

from typing import Any

import numpy as np
import optuna
from sklearn.metrics import mean_absolute_error

from bioscale.models.lifestyle_regressor import LifestyleRegressor


def optimize_lifestyle_regressor(
    X_train: Any,
    y_train: np.ndarray,
    X_val: Any,
    y_val: np.ndarray,
    numeric_cols: list[str],
    categorical_cols: list[str],
    n_trials: int = 50,
    random_state: int = 42,
) -> dict[str, Any]:
    """
    Optimize hyperparameters for LifestyleRegressor using Optuna.

    Parameters
    ----------
    X_train : pd.DataFrame
        Training feature matrix.
    y_train : np.ndarray
        Training targets.
    X_val : pd.DataFrame
        Validation feature matrix.
    y_val : np.ndarray
        Validation targets.
    numeric_cols : list[str]
        List of numeric column names.
    categorical_cols : list[str]
        List of categorical column names.
    n_trials : int, default=50
        Number of trials for Optuna search.
    random_state : int, default=42
        Random seed for reproducibility.

    Returns
    -------
    dict
        Dictionary with keys:
        - "best_params": dict of best hyperparameters
        - "best_model": fitted LifestyleRegressor with best params
        - "best_mae": best validation MAE
    """
    sampler = optuna.samplers.TPESampler(seed=random_state)
    study = optuna.create_study(sampler=sampler, direction="minimize")

    def objective(trial):
        params = {
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
            "max_depth": trial.suggest_int("max_depth", 3, 12),
            "n_estimators": trial.suggest_int("n_estimators", 50, 500),
            "min_child_weight": trial.suggest_float("min_child_weight", 0.5, 5.0),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "random_state": random_state,
        }

        model = LifestyleRegressor(**params)
        model.fit(X_train, y_train, X_val, y_val)
        y_pred = model.predict(X_val)
        mae = mean_absolute_error(y_val, y_pred)
        return mae

    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)

    best_params = study.best_params
    best_params["random_state"] = random_state

    best_model = LifestyleRegressor(**best_params)
    best_model.fit(X_train, y_train, X_val, y_val)

    best_mae = study.best_value

    return {
        "best_params": best_params,
        "best_model": best_model,
        "best_mae": best_mae,
    }
