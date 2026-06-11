"""
SHAP explainability engine for the lifestyle regressor model.

This module provides SHAP-based local explanations for individual predictions,
allowing us to understand which features drive predicted biological age.
"""

import numpy as np
import pandas as pd
import shap

from bioscale.models.lifestyle_regressor import LifestyleRegressor


class ShapExplainer:
    """
    SHAP explainer wrapper for LifestyleRegressor predictions.

    This class wraps a fitted LifestyleRegressor and uses SHAP's TreeExplainer
    to provide local feature contributions for each prediction.

    Attributes
    ----------
    model : LifestyleRegressor
        Fitted lifestyle regressor.
    preprocessed_feature_names : list[str]
        Names of features in the preprocessed space (after ColumnTransformer).
    explainer : shap.TreeExplainer
        SHAP explainer initialized on the model's booster.
    """

    def __init__(self, model: LifestyleRegressor, feature_names: list[str] = None):
        """
        Initialize the SHAP explainer.

        Parameters
        ----------
        model : LifestyleRegressor
            Fitted lifestyle regressor with accessible booster_ and preprocessor_.
        feature_names : list[str], optional
            Names of features in the preprocessed space. If not provided, will be
            generated automatically from the preprocessor.
        """
        self.model = model

        # Generate preprocessed feature names if not provided
        if feature_names is None:
            feature_names = self._get_preprocessed_feature_names()

        self.preprocessed_feature_names = feature_names
        self.explainer = shap.TreeExplainer(model.booster_)

    def _get_preprocessed_feature_names(self) -> list[str]:
        """
        Generate feature names in the preprocessed feature space.

        Returns
        -------
        list[str]
            Names of all features after preprocessing (including one-hot encoded).
        """
        preprocessor = self.model.preprocessor_
        feature_names_out = []

        for name, transformer, columns in preprocessor.transformers_:
            if name == "drop":
                continue
            elif name == "num":
                # Numeric features are kept as-is
                feature_names_out.extend(columns)
            elif name == "cat":
                # Categorical features are one-hot encoded
                # Get the categories from the encoder
                encoder = transformer
                for i, category_list in enumerate(encoder.categories_):
                    for category in category_list:
                        col_name = columns[i]
                        feature_names_out.append(f"{col_name}_{category}")

        return feature_names_out

    def explain_instance(
        self, X_row: np.ndarray | pd.DataFrame
    ) -> dict:
        """
        Compute SHAP values and baseline for a single instance.

        Parameters
        ----------
        X_row : np.ndarray or pd.DataFrame
            Single-row input in the model's **preprocessed feature space**
            (i.e., after ColumnTransformer has been applied).
            Shape must be (1, n_preprocessed_features).

        Returns
        -------
        dict
            Dictionary with keys:
            - "baseline": expected_value (float)
            - "shap_values": dict mapping feature_name -> shap_value (float)

        Notes
        -----
        - Input MUST be preprocessed (categorical encoded, numeric scaled).
        - This method does NOT retrain the model or explainer.
        - Inference is deterministic and stateless.

        Examples
        --------
        >>> model_pred = model.predict(X_test)
        >>> X_test_preprocessed = model.preprocessor_.transform(X_test)
        >>> result = explainer.explain_instance(X_test_preprocessed)
        """
        # Ensure input is properly shaped
        if isinstance(X_row, pd.DataFrame):
            X_row = X_row.values

        if X_row.ndim == 1:
            X_row = X_row.reshape(1, -1)

        assert X_row.shape[0] == 1, f"Expected 1 row, got {X_row.shape[0]}"
        assert (
            X_row.shape[1] == len(self.preprocessed_feature_names)
        ), f"Expected {len(self.preprocessed_feature_names)} features, got {X_row.shape[1]}"

        # Compute SHAP values
        shap_values = self.explainer.shap_values(X_row)

        # Handle both single and multi-output cases
        if isinstance(shap_values, list):
            # For multi-output models, take the first output
            shap_values = shap_values[0]

        if shap_values.ndim > 1:
            # Remove batch dimension if present
            shap_values = shap_values[0]

        # Get baseline (expected value)
        expected_value = self.explainer.expected_value
        if isinstance(expected_value, (list, np.ndarray)):
            expected_value = expected_value[0]

        # Create output dict
        shap_dict = {
            self.preprocessed_feature_names[i]: float(shap_values[i])
            for i in range(len(self.preprocessed_feature_names))
        }

        return {
            "baseline": float(expected_value),
            "shap_values": shap_dict,
        }

