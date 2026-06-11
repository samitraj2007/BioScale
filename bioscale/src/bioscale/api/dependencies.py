"""
FastAPI dependency injection utilities.

Provides lazy-loaded singletons for the trained model and SHAP explainer.
"""

from pathlib import Path

from .. import config
from ..explainability.shap_engine import ShapExplainer
from ..models.lifestyle_regressor import LifestyleRegressor

# Module-level singletons
_model: LifestyleRegressor | None = None
_explainer: ShapExplainer | None = None


def get_lifestyle_model() -> LifestyleRegressor:
    """
    Get or load the trained lifestyle regressor model.

    This function implements lazy loading: the model is loaded on first call
    and then cached for subsequent calls.

    Returns
    -------
    LifestyleRegressor
        The fitted lifestyle regressor model.

    Raises
    ------
    FileNotFoundError
        If the model file does not exist at config.MODELS_DIR.
    """
    global _model

    if _model is None:
        model_path = config.MODELS_DIR / "lifestyle_regressor.joblib"
        _model = LifestyleRegressor.load(model_path)

    return _model


def get_shap_explainer() -> ShapExplainer:
    """
    Get or create the SHAP explainer for the lifestyle model.

    This function implements lazy loading: the explainer is created on first call
    and then cached for subsequent calls.

    Returns
    -------
    ShapExplainer
        SHAP explainer initialized with the lifestyle model.
    """
    global _explainer

    if _explainer is None:
        model = get_lifestyle_model()
        _explainer = ShapExplainer(model)

    return _explainer
