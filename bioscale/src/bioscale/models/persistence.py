"""
Model persistence utilities for saving and loading trained models.

This module provides simple wrappers around joblib for serializing
and deserializing model artifacts.
"""

from pathlib import Path
from typing import Any

import joblib


def save_model(obj: Any, path: Path) -> None:
    """
    Save an object to disk using joblib.

    Parameters
    ----------
    obj : Any
        Object to save (model, preprocessor, etc.).
    path : Path
        Path to save the object to.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(obj, path)


def load_model(path: Path) -> Any:
    """
    Load an object from disk using joblib.

    Parameters
    ----------
    path : Path
        Path to load from.

    Returns
    -------
    Any
        Loaded object.
    """
    return joblib.load(path)
