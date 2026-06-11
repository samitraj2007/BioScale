"""
Schema mapper for converting Phase 1 NHANES ETL output to Stage 1/Stage 2 format.

This module provides a thin adapter that maps NHANES column names from Phase 1
ETL output into the Stage 1 (biomarkers + survival) and Stage 2 (lifestyle +
anthropometry) schemas used by Phase 2 modeling code.

Stage 1: Biomarkers + survival information for phenotypic age and survival models.
Stage 2: Lifestyle and anthropometric features for lifestyle/behavioral modeling.
"""

from typing import Tuple
import pandas as pd


def split_nhanes_to_stage1_stage2(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Map Phase 1 NHANES ETL output into Stage 1 and Stage 2 schemas for Phase 2.
    
    This is a thin adapter that:
    1. Extracts biomarker columns for survival/phenotypic age modeling (Stage 1)
    2. Extracts lifestyle/anthropometric features (Stage 2)
    3. Renames columns to standardized names
    
    Parameters
    ----------
    df : pd.DataFrame
        NHANES dataset from Phase 1 ETL (either model_input or with_mortality).
        Expected to have columns like: SEQN, RIDAGEYR, BMXBMI, LBXALB, LBXCR,
        LBXGLU, LBXWBCSI, LBXCRP, ALQ110, SMQ020, etc.
    
    Returns
    -------
    stage1 : pd.DataFrame
        Biomarkers + survival (if available):
        Columns: seqn, chronological_age, albumin, creatinine, glucose,
                 wbc, rdw, crp, duration_months, event
    
    stage2 : pd.DataFrame
        Lifestyle + anthropometry:
        Columns: seqn, chronological_age, bmi, waist_circumference,
                 height, weight, alcohol_days_per_week, smoking_status,
                 physical_activity
    
    Notes
    -----
    - Uses NHANES column names from Phase 1 ETL output
    - Renames columns to simplified names for Phase 2 compatibility
    - Both datasets include SEQN and chronological age
    - Survivalcolumns (duration_months, event) only included if present in input
    - Missing columns are handled gracefully (skipped if not present)
    
    Examples
    --------
    >>> from bioscale.data.load_nhanes_real import load_nhanes_with_mortality
    >>> from bioscale.data.nhanes_mapping import split_nhanes_to_stage1_stage2
    >>> df = load_nhanes_with_mortality()
    >>> stage1, stage2 = split_nhanes_to_stage1_stage2(df)
    >>> print(stage1.shape)  # (rows, 10) - 6 biomarkers + survival + id + age
    >>> print(stage2.shape)  # (rows, 9) - lifestyle/anthropometry features
    
    >>> # Check what columns are available
    >>> print(stage1.columns.tolist())
    >>> print(stage2.columns.tolist())
    """
    
    # Base identifiers
    id_col = "SEQN"
    age_col = "RIDAGEYR"
    
    # ========== STAGE 1: Biomarkers + Survival ==========
    
    # Always include
    stage1_base = [id_col, age_col]
    
    # Phenotypic age biomarkers (key markers from Phase 1)
    # Note: Not all biomarkers may be present in the input dataset
    # LBXALB (albumin) and LBXCR (creatinine) are in Phase 1 docs but may not be
    # extracted; only include if actually present
    biomarker_mapping = {
        "LBXWBCSI": "wbc",            # White blood cell count (10³/µL)
        "LBXCRP": "crp",              # C-Reactive Protein (mg/L)
        "LBXGLU": "glucose",          # Fasting glucose (mg/dL)
        "LBXIN": "insulin",           # Fasting insulin (µIU/mL)
        # These may not be present in extracted data:
        # "LBXALB": "albumin",        # Albumin (g/dL)
        # "LBXCR": "creatinine",      # Creatinine (mg/dL)
        # "LBXRDW": "rdw",            # Red cell distribution width (%)
    }
    
    # Extract available biomarkers
    stage1_biomarkers = {}
    for nhanes_col, standard_col in biomarker_mapping.items():
        if nhanes_col in df.columns:
            stage1_biomarkers[nhanes_col] = standard_col
    
    stage1_cols = stage1_base + list(stage1_biomarkers.keys())
    
    # Add survival columns if available
    survival_cols = {}
    for col in ["duration_months", "event"]:
        if col in df.columns:
            survival_cols[col] = col  # No renaming needed, already standardized from Phase 1
            stage1_cols.append(col)
    
    # Build Stage 1 dataframe
    stage1 = df[stage1_cols].copy()
    
    # Rename columns: NHANES names -> standardized names
    rename_dict = {
        id_col: "seqn",
        age_col: "chronological_age",
    }
    rename_dict.update(stage1_biomarkers)
    stage1.rename(columns=rename_dict, inplace=True)
    
    # ========== STAGE 2: Lifestyle + Anthropometry ==========
    
    # Always include
    stage2_base = [id_col, age_col]
    
    # Lifestyle and anthropometric features
    lifestyle_mapping = {
        "BMXBMI": "bmi",                              # BMI (kg/m²)
        "BMXWAIST": "waist_circumference",            # Waist (cm)
        "BMXHT": "height",                            # Height (cm)
        "BMXWT": "weight",                            # Weight (kg)
        "ALQ110": "alcohol_ever",                     # Ever had a drink
        "ALQ120Q": "alcohol_days_per_week",           # Days per week drank
        "ALQ130": "alcohol_drinks_per_day",           # Drinks per occasion
        "SMQ020": "smoking_ever_100_cigs",            # Ever smoked 100+ cigs
        "SMQ040": "smoking_current_status",           # Current smoking status
        # PAQ variables not extracted in Phase 1, but kept in mapping if added
        # ALQ120U not included (unit indicator)
    }
    
    # Extract available lifestyle columns
    stage2_lifestyle = {}
    for nhanes_col, standard_col in lifestyle_mapping.items():
        if nhanes_col in df.columns:
            stage2_lifestyle[nhanes_col] = standard_col
    
    stage2_cols = stage2_base + list(stage2_lifestyle.keys())
    
    # Build Stage 2 dataframe
    stage2 = df[stage2_cols].copy()
    
    # Rename columns: NHANES names -> standardized names
    rename_dict_stage2 = {
        id_col: "seqn",
        age_col: "chronological_age",
    }
    rename_dict_stage2.update(stage2_lifestyle)
    stage2.rename(columns=rename_dict_stage2, inplace=True)
    
    return stage1, stage2


def get_stage1_schema() -> dict:
    """
    Get the Stage 1 schema description.
    
    Returns
    -------
    dict
        Schema with column names, descriptions, and data types.
    """
    return {
        "seqn": {"description": "NHANES participant ID", "dtype": "int64"},
        "chronological_age": {"description": "Age at screening (years)", "dtype": "float64"},
        "albumin": {"description": "Serum albumin (g/dL)", "dtype": "float64"},
        "creatinine": {"description": "Serum creatinine (mg/dL)", "dtype": "float64"},
        "glucose": {"description": "Fasting glucose (mg/dL)", "dtype": "float64"},
        "wbc": {"description": "White blood cell count (10³/µL)", "dtype": "float64"},
        "rdw": {"description": "Red cell distribution width (%)", "dtype": "float64"},
        "crp": {"description": "C-Reactive Protein (mg/L)", "dtype": "float64"},
        "duration_months": {"description": "Follow-up time from MEC exam (months)", "dtype": "float64", "optional": True},
        "event": {"description": "Vital status (1=dead, 0=alive)", "dtype": "float64", "optional": True},
    }


def get_stage2_schema() -> dict:
    """
    Get the Stage 2 schema description.
    
    Returns
    -------
    dict
        Schema with column names, descriptions, and data types.
    """
    return {
        "seqn": {"description": "NHANES participant ID", "dtype": "int64"},
        "chronological_age": {"description": "Age at screening (years)", "dtype": "float64"},
        "bmi": {"description": "Body Mass Index (kg/m²)", "dtype": "float64"},
        "waist_circumference": {"description": "Waist circumference (cm)", "dtype": "float64"},
        "height": {"description": "Height (cm)", "dtype": "float64"},
        "weight": {"description": "Weight (kg)", "dtype": "float64"},
        "alcohol_ever": {"description": "Ever had a drink (binary)", "dtype": "float64"},
        "alcohol_days_per_week": {"description": "Days per week drank (last 12 months)", "dtype": "float64"},
        "alcohol_drinks_per_day": {"description": "Number of drinks on drinking day", "dtype": "float64"},
        "smoking_ever_100_cigs": {"description": "Ever smoked 100+ cigarettes (binary)", "dtype": "float64"},
        "smoking_current_status": {"description": "Current smoking status", "dtype": "float64"},
    }
