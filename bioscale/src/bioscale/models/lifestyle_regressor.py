"""
Lifestyle Regressor using XGBoost with scikit-learn preprocessing.

This module provides a scikit-learn-compatible wrapper for training
and inference on lifestyle features to predict Phenotypic Age.
"""

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer


class LifestyleRegressor:
    """
    Wrapper for XGBoost regressor with preprocessing pipeline.

    Attributes
    ----------
    booster_ : xgb.XGBRegressor
        Fitted XGBoost model.
    preprocessor_ : ColumnTransformer
        Fitted preprocessing pipeline.
    feature_names_ : list[str]
        Names of features in the original input.
    """

    def __init__(
        self,
        learning_rate: float = 0.1,
        max_depth: int = 5,
        n_estimators: int = 100,
        min_child_weight: float = 1.0,
        subsample: float = 0.8,
        colsample_bytree: float = 0.8,
        random_state: int = 42,
    ):
        """
        Initialize the LifestyleRegressor.

        Parameters
        ----------
        learning_rate : float, default=0.1
            Learning rate for XGBoost.
        max_depth : int, default=5
            Max depth of trees.
        n_estimators : int, default=100
            Number of boosting rounds.
        min_child_weight : float, default=1.0
            Minimum child weight for tree splits.
        subsample : float, default=0.8
            Fraction of samples for training each tree.
        colsample_bytree : float, default=0.8
            Fraction of features for training each tree.
        random_state : int, default=42
            Random seed for reproducibility.
        """
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.n_estimators = n_estimators
        self.min_child_weight = min_child_weight
        self.subsample = subsample
        self.colsample_bytree = colsample_bytree
        self.random_state = random_state

        self.booster_ = None
        self.preprocessor_ = None
        self.feature_names_ = None

    def _build_preprocessor(self, numeric_cols: list[str], categorical_cols: list[str]):
        """Build the preprocessing pipeline."""
        transformers = []

        if numeric_cols:
            transformers.append(("num", StandardScaler(), numeric_cols))

        if categorical_cols:
            transformers.append(
                (
                    "cat",
                    OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                    categorical_cols,
                )
            )

        self.preprocessor_ = ColumnTransformer(
            transformers=transformers, remainder="drop"
        )
        return self.preprocessor_

    def fit(
        self,
        X_train: pd.DataFrame,
        y_train: np.ndarray | pd.Series,
        X_val: pd.DataFrame | None = None,
        y_val: np.ndarray | pd.Series | None = None,
    ) -> "LifestyleRegressor":
        """
        Fit the regressor on training data.

        Parameters
        ----------
        X_train : pd.DataFrame
            Training feature matrix.
        y_train : np.ndarray or pd.Series
            Training targets.
        X_val : pd.DataFrame, optional
            Validation feature matrix (for early stopping).
        y_val : np.ndarray or pd.Series, optional
            Validation targets.

        Returns
        -------
        self
        """
        if isinstance(X_train, pd.DataFrame):
            self.feature_names_ = X_train.columns.tolist()
            numeric_cols = X_train.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = X_train.select_dtypes(include=["object", "category"]).columns.tolist()
        else:
            self.feature_names_ = [f"feature_{i}" for i in range(X_train.shape[1])]
            numeric_cols = self.feature_names_
            categorical_cols = []

        self._build_preprocessor(numeric_cols, categorical_cols)

        X_train_transformed = self.preprocessor_.fit_transform(X_train)

        eval_set = None
        if X_val is not None and y_val is not None:
            X_val_transformed = self.preprocessor_.transform(X_val)
            eval_set = [(X_val_transformed, y_val)]

        self.booster_ = xgb.XGBRegressor(
            learning_rate=self.learning_rate,
            max_depth=self.max_depth,
            n_estimators=self.n_estimators,
            min_child_weight=self.min_child_weight,
            subsample=self.subsample,
            colsample_bytree=self.colsample_bytree,
            random_state=self.random_state,
            eval_metric="mae",
        )

        self.booster_.fit(
            X_train_transformed,
            y_train,
            eval_set=eval_set,
            verbose=False,
        )

        return self

    def predict(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        """
        Make predictions.

        Parameters
        ----------
        X : pd.DataFrame or np.ndarray
            Feature matrix.

        Returns
        -------
        np.ndarray
            Predicted values.
        """
        if self.booster_ is None:
            raise ValueError("Model has not been fitted yet.")

        X_transformed = self.preprocessor_.transform(X)
        return self.booster_.predict(X_transformed)

    def save(self, path: Path) -> None:
        """
        Save the fitted model and preprocessor.

        Parameters
        ----------
        path : Path
            Path to save the model.
        """
        import joblib

        joblib.dump(
            {
                "booster": self.booster_,
                "preprocessor": self.preprocessor_,
                "feature_names": self.feature_names_,
                "hyperparams": {
                    "learning_rate": self.learning_rate,
                    "max_depth": self.max_depth,
                    "n_estimators": self.n_estimators,
                    "min_child_weight": self.min_child_weight,
                    "subsample": self.subsample,
                    "colsample_bytree": self.colsample_bytree,
                    "random_state": self.random_state,
                },
            },
            path,
        )

    @classmethod
    def load(cls, path: Path) -> "LifestyleRegressor":
        """
        Load a saved model.

        Parameters
        ----------
        path : Path
            Path to the saved model.

        Returns
        -------
        LifestyleRegressor
            Loaded model.
        """
        import joblib

        data = joblib.load(path)
        model = cls(**data["hyperparams"])
        model.booster_ = data["booster"]
        model.preprocessor_ = data["preprocessor"]
        model.feature_names_ = data["feature_names"]
        return model
