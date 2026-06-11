"""
NHANES data access layer for Phase 1 ETL outputs.

Provides simple functions to load processed NHANES datasets for modeling.
"""

from pathlib import Path
import pandas as pd


def load_nhanes_model_input() -> pd.DataFrame:
    """
    Load Phase 1 NHANES model-input dataset (no mortality).
    
    This dataset contains all NHANES participants with complete phenotypic age
    markers (albumin, creatinine, glucose, WBC, RDW, CRP).
    
    Returns
    -------
    pd.DataFrame
        NHANES model-ready data:
        - Shape: (4386, 23) rows × columns
        - Rows: Participants with complete key lab markers
        - Columns: Demographics, anthropometry, lifestyle, lab values
        - No mortality information
    
    Raises
    ------
    FileNotFoundError
        If the parquet file is not found at the expected location.
    
    Example
    -------
    >>> from bioscale.data.load_nhanes_real import load_nhanes_model_input
    >>> df = load_nhanes_model_input()
    >>> print(df.shape)  # (4386, 23)
    >>> print(df.columns.tolist())
    """
    # Try multiple possible paths to handle different execution contexts
    candidates = [
        Path("data/processed/nhanes_1999_2002_model_input.parquet"),
        Path("bioscale/data/processed/nhanes_1999_2002_model_input.parquet"),
    ]
    
    for path in candidates:
        if path.exists():
            return pd.read_parquet(path)
    
    raise FileNotFoundError(
        f"NHANES model input file not found. "
        f"Tried: {[str(p.resolve()) for p in candidates]}. "
        "Please run Phase 1 ETL: python backend/etl/nhanes_etl.py"
    )


def load_nhanes_with_mortality() -> pd.DataFrame:
    """
    Load Phase 1 NHANES dataset with attached mortality information.
    
    This dataset contains all merged NHANES participants with linked mortality
    data from the 1999-2019 public-use linked mortality file (LMF).
    
    Returns
    -------
    pd.DataFrame
        NHANES survival-ready data:
        - Shape: (6787, 27) rows × columns
        - Rows: All NHANES participants (left-join with mortality, some duplicates)
        - Columns: All original NHANES variables + mortality data
        - Mortality columns:
            - duration_months: Follow-up time from MEC exam (in months)
            - event: Vital status (1=dead, 0=alive, NULL=unknown)
            - MORTSTAT: Raw vital status from LMF
            - PERMTH_EXM: Raw follow-up months from LMF
    
    Notes
    -----
    - Follow-up months available for ~26% of records (1776/6787)
    - Vital status (event) may be NULL if not clearly identified in source file
    - Some SEQN values have multiple rows due to survey component structure
    
    Raises
    ------
    FileNotFoundError
        If the parquet file is not found at the expected location.
    
    Example
    -------
    >>> from bioscale.data.load_nhanes_real import load_nhanes_with_mortality
    >>> df = load_nhanes_with_mortality()
    >>> print(df.shape)  # (6787, 27)
    >>> print(df['duration_months'].describe())
    """
    # Try multiple possible paths to handle different execution contexts
    candidates = [
        Path("data/processed/nhanes_1999_2002_with_mortality.parquet"),
        Path("bioscale/data/processed/nhanes_1999_2002_with_mortality.parquet"),
    ]
    
    for path in candidates:
        if path.exists():
            return pd.read_parquet(path)
    
    raise FileNotFoundError(
        f"NHANES mortality file not found. "
        f"Tried: {[str(p.resolve()) for p in candidates]}. "
        "Please run Phase 1 ETL: python backend/etl/nhanes_etl.py"
    )
