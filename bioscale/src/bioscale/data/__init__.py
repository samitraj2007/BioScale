"""
Data access layer for BioScale.

Provides functions to load NHANES datasets and adapt them to Phase 2 schemas.
"""

from .load_nhanes_real import load_nhanes_model_input, load_nhanes_with_mortality
from .nhanes_mapping import split_nhanes_to_stage1_stage2

__all__ = [
    "load_nhanes_model_input",
    "load_nhanes_with_mortality",
    "split_nhanes_to_stage1_stage2",
]
