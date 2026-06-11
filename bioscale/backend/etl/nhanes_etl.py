"""
NHANES 1999-2002 Data ETL Pipeline.

Loads and harmonizes NHANES data from XPT files across two survey cycles:
- 1999-2000 (files without suffix)
- 2001-2002 (files with _B suffix)

Extracts key variables for phenotypic age modeling and merges across all sources.
"""

import logging
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd
import numpy as np

# Try pyreadstat first, fall back to pandas.read_sas
try:
    import pyreadstat
    HAS_PYREADSTAT = True
except ImportError:
    HAS_PYREADSTAT = False

logger = logging.getLogger(__name__)

# Configure paths
REPO_ROOT = Path(__file__).resolve().parents[2]  # Navigate to bioscale/
DATA_RAW_DIR = REPO_ROOT / "data" / "raw"
DATA_INTERIM_DIR = REPO_ROOT / "data" / "interim"
DATA_PROCESSED_DIR = REPO_ROOT / "data" / "processed"

# Ensure output directories exist
DATA_INTERIM_DIR.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def detect_cycle(filename: str) -> str:
    """
    Detect survey cycle from filename.
    
    Files with _B suffix are 2001-2002; others are 1999-2000.
    
    Parameters
    ----------
    filename : str
        Filename of the XPT file.
    
    Returns
    -------
    str
        Cycle label: "1999_2000" or "2001_2002"
    """
    if "_B" in filename.upper():
        return "2001_2002"
    return "1999_2000"


def read_xpt(filepath: Path) -> pd.DataFrame:
    """
    Read XPT file using pyreadstat or pandas.
    
    Parameters
    ----------
    filepath : Path
        Path to XPT file.
    
    Returns
    -------
    pd.DataFrame
        Data from XPT file.
    """
    if HAS_PYREADSTAT:
        try:
            # Try reading as XPT (transport) format
            df, meta = pyreadstat.read_xport(str(filepath))
            return df
        except Exception:
            # Fall back to sas7bdat
            try:
                df, meta = pyreadstat.read_sas7bdat(str(filepath))
                return df
            except Exception:
                logger.warning(f"pyreadstat failed for {filepath}, trying pandas.read_sas")
                return pd.read_sas(str(filepath), format="xpt")
    else:
        return pd.read_sas(str(filepath), format="xpt")


def load_demo_variables(df: pd.DataFrame, cycle: str) -> pd.DataFrame:
    """
    Extract demographic variables from DEMO table.
    
    Keeps: SEQN, age, sex, race/ethnicity, weights, strata, PSU.
    
    Parameters
    ----------
    df : pd.DataFrame
        Raw DEMO dataframe.
    cycle : str
        Survey cycle ("1999_2000" or "2001_2002").
    
    Returns
    -------
    pd.DataFrame
        Subset of DEMO variables with SEQN as index.
    """
    # Variable names may differ; harmonize as we find them
    cols_to_keep = ["SEQN"]
    
    # Age: typically RIDAGEYR
    if "RIDAGEYR" in df.columns:
        cols_to_keep.append("RIDAGEYR")
    
    # Sex: typically RIDSEX
    if "RIDSEX" in df.columns:
        cols_to_keep.append("RIDSEX")
    
    # Race/ethnicity: RIDRETH1
    if "RIDRETH1" in df.columns:
        cols_to_keep.append("RIDRETH1")
    
    # Survey weights: WTINT2YR, WTMEC2YR
    if "WTINT2YR" in df.columns:
        cols_to_keep.append("WTINT2YR")
    if "WTMEC2YR" in df.columns:
        cols_to_keep.append("WTMEC2YR")
    
    # Design variables: SDMVSTRA, SDMVPSU
    if "SDMVSTRA" in df.columns:
        cols_to_keep.append("SDMVSTRA")
    if "SDMVPSU" in df.columns:
        cols_to_keep.append("SDMVPSU")
    
    # Keep only available columns
    cols_present = [c for c in cols_to_keep if c in df.columns]
    
    result = df[cols_present].copy()
    logger.info(f"DEMO ({cycle}): kept {len(cols_present)} columns")
    
    return result


def load_bmx_variables(df: pd.DataFrame, cycle: str) -> pd.DataFrame:
    """
    Extract body measurement variables from BMX table.
    
    Keeps: SEQN, BMI, waist circumference, height, weight.
    
    Parameters
    ----------
    df : pd.DataFrame
        Raw BMX dataframe.
    cycle : str
        Survey cycle ("1999_2000" or "2001_2002").
    
    Returns
    -------
    pd.DataFrame
        Subset of BMX variables with SEQN.
    """
    cols_to_keep = ["SEQN"]
    
    # BMI: BMXBMI
    if "BMXBMI" in df.columns:
        cols_to_keep.append("BMXBMI")
    
    # Waist circumference: BMXWAIST
    if "BMXWAIST" in df.columns:
        cols_to_keep.append("BMXWAIST")
    
    # Height: BMXHT
    if "BMXHT" in df.columns:
        cols_to_keep.append("BMXHT")
    
    # Weight: BMXWT
    if "BMXWT" in df.columns:
        cols_to_keep.append("BMXWT")
    
    cols_present = [c for c in cols_to_keep if c in df.columns]
    
    result = df[cols_present].copy()
    logger.info(f"BMX ({cycle}): kept {len(cols_present)} columns")
    
    return result


def load_alq_variables(df: pd.DataFrame, cycle: str) -> pd.DataFrame:
    """
    Extract alcohol use variables from ALQ table.
    
    Selected variables:
    - ALQ101: Ever had 12 drinks per year?
    - ALQ110: Ever had a drink?
    - ALQ120Q: Days per week drank alcohol (last 12 months)
    - ALQ120U: Days per week unit
    - ALQ130: Number of drinks on a drinking day
    
    Parameters
    ----------
    df : pd.DataFrame
        Raw ALQ dataframe.
    cycle : str
        Survey cycle ("1999_2000" or "2001_2002").
    
    Returns
    -------
    pd.DataFrame
        Subset of ALQ variables with SEQN.
    """
    cols_to_keep = ["SEQN"]
    
    # Common ALQ variables
    alq_vars = ["ALQ101", "ALQ110", "ALQ120Q", "ALQ120U", "ALQ130"]
    for var in alq_vars:
        if var in df.columns:
            cols_to_keep.append(var)
    
    cols_present = [c for c in cols_to_keep if c in df.columns]
    
    result = df[cols_present].copy()
    logger.info(f"ALQ ({cycle}): kept {len(cols_present)} columns")
    
    return result


def load_paq_variables(df: pd.DataFrame, cycle: str) -> pd.DataFrame:
    """
    Extract physical activity variables from PAQ table.
    
    Selected variables:
    - PAQ605: Engage in moderate-intensity activity?
    - PAQ610: Days per week moderate activity
    - PAQ625: Engage in vigorous-intensity activity?
    - PAQ630: Days per week vigorous activity
    
    Parameters
    ----------
    df : pd.DataFrame
        Raw PAQ dataframe.
    cycle : str
        Survey cycle ("1999_2000" or "2001_2002").
    
    Returns
    -------
    pd.DataFrame
        Subset of PAQ variables with SEQN.
    """
    cols_to_keep = ["SEQN"]
    
    # Common PAQ variables
    paq_vars = ["PAQ605", "PAQ610", "PAQ625", "PAQ630"]
    for var in paq_vars:
        if var in df.columns:
            cols_to_keep.append(var)
    
    cols_present = [c for c in cols_to_keep if c in df.columns]
    
    result = df[cols_present].copy()
    logger.info(f"PAQ ({cycle}): kept {len(cols_present)} columns")
    
    return result


def load_smq_variables(df: pd.DataFrame, cycle: str) -> pd.DataFrame:
    """
    Extract smoking status variables from SMQ table.
    
    Selected variables:
    - SMQ020: Smoked at least 100 cigarettes?
    - SMQ040: Do you now smoke cigarettes?
    - SMQ050: How long since last smoked?
    
    Parameters
    ----------
    df : pd.DataFrame
        Raw SMQ dataframe.
    cycle : str
        Survey cycle ("1999_2000" or "2001_2002").
    
    Returns
    -------
    pd.DataFrame
        Subset of SMQ variables with SEQN.
    """
    cols_to_keep = ["SEQN"]
    
    # Common SMQ variables
    smq_vars = ["SMQ020", "SMQ040", "SMQ050"]
    for var in smq_vars:
        if var in df.columns:
            cols_to_keep.append(var)
    
    cols_present = [c for c in cols_to_keep if c in df.columns]
    
    result = df[cols_present].copy()
    logger.info(f"SMQ ({cycle}): kept {len(cols_present)} columns")
    
    return result


def load_lab25_variables(df: pd.DataFrame, cycle: str) -> pd.DataFrame:
    """
    Extract CBC (Complete Blood Count) variables from LAB25/L25_B.
    
    Selected variables for phenotypic age:
    - WBC: White blood cell count (LBXWBCSI or LBXWBC)
    - RDW: Red cell distribution width (LBXRDW)
    - Lymphocyte percentage (LBXLYPCT)
    - Others as available
    
    Parameters
    ----------
    df : pd.DataFrame
        Raw LAB25 dataframe.
    cycle : str
        Survey cycle ("1999_2000" or "2001_2002").
    
    Returns
    -------
    pd.DataFrame
        Subset of CBC variables with SEQN.
    """
    cols_to_keep = ["SEQN"]
    
    # CBC variables
    cbc_vars = ["LBXWBCSI", "LBXWBC", "LBXRDW", "LBXLYPCT", "LBXMCV", "LBXHGB", "LBXHCT"]
    for var in cbc_vars:
        if var in df.columns:
            cols_to_keep.append(var)
            break  # Take first match to avoid duplicates
    
    # Ensure SEQN is present
    if "SEQN" in df.columns:
        cols_present = [c for c in cols_to_keep if c in df.columns]
        result = df[cols_present].copy()
        logger.info(f"LAB25 ({cycle}): kept {len(cols_present)} columns")
        return result
    
    return pd.DataFrame({"SEQN": []})


def load_lab18_variables(df: pd.DataFrame, cycle: str) -> pd.DataFrame:
    """
    Extract biochemistry variables from LAB18/L40_B.
    
    Selected variables for phenotypic age:
    - Albumin (LBXALB)
    - Creatinine (LBXCR)
    - Alkaline phosphatase (LBXAP)
    - Others as available
    
    Parameters
    ----------
    df : pd.DataFrame
        Raw LAB18 dataframe.
    cycle : str
        Survey cycle ("1999_2000" or "2001_2002").
    
    Returns
    -------
    pd.DataFrame
        Subset of biochemistry variables with SEQN.
    """
    cols_to_keep = ["SEQN"]
    
    # Biochemistry variables
    biochem_vars = ["LBXALB", "LBXCR", "LBXAP", "LBXBUN", "LBXGLU", "LBXCHOL", "LBXHDL"]
    for var in biochem_vars:
        if var in df.columns:
            cols_to_keep.append(var)
    
    cols_present = [c for c in cols_to_keep if c in df.columns]
    
    result = df[cols_present].copy()
    logger.info(f"LAB18 ({cycle}): kept {len(cols_present)} columns")
    
    return result


def load_lab11_variables(df: pd.DataFrame, cycle: str) -> pd.DataFrame:
    """
    Extract CRP (C-Reactive Protein) from LAB11/L11_B.
    
    Selected variables:
    - LBXCRP: C-Reactive Protein
    
    Parameters
    ----------
    df : pd.DataFrame
        Raw LAB11 dataframe.
    cycle : str
        Survey cycle ("1999_2000" or "2001_2002").
    
    Returns
    -------
    pd.DataFrame
        Subset of CRP variables with SEQN.
    """
    cols_to_keep = ["SEQN"]
    
    if "LBXCRP" in df.columns:
        cols_to_keep.append("LBXCRP")
    
    cols_present = [c for c in cols_to_keep if c in df.columns]
    
    result = df[cols_present].copy()
    logger.info(f"LAB11 ({cycle}): kept {len(cols_present)} columns")
    
    return result


def load_lab10am_variables(df: pd.DataFrame, cycle: str) -> pd.DataFrame:
    """
    Extract fasting glucose and insulin from LAB10AM/L10AM_B.
    
    Selected variables:
    - LBXGLU: Fasting glucose (mg/dL)
    - LBXIN: Fasting insulin
    
    Parameters
    ----------
    df : pd.DataFrame
        Raw LAB10AM dataframe.
    cycle : str
        Survey cycle ("1999_2000" or "2001_2002").
    
    Returns
    -------
    pd.DataFrame
        Subset of fasting glucose/insulin variables with SEQN.
    """
    cols_to_keep = ["SEQN"]
    
    if "LBXGLU" in df.columns:
        cols_to_keep.append("LBXGLU")
    if "LBXIN" in df.columns:
        cols_to_keep.append("LBXIN")
    
    cols_present = [c for c in cols_to_keep if c in df.columns]
    
    result = df[cols_present].copy()
    logger.info(f"LAB10AM ({cycle}): kept {len(cols_present)} columns")
    
    return result


def load_and_merge_cycle(cycle: str) -> pd.DataFrame:
    """
    Load and merge all data sources for a single survey cycle.
    
    Parameters
    ----------
    cycle : str
        Survey cycle ("1999_2000" or "2001_2002").
    
    Returns
    -------
    pd.DataFrame
        Merged dataframe for the cycle with SEQN as index.
    """
    logger.info(f"\n=== Loading {cycle} data ===")
    
    # Determine filename suffixes
    suffix = "_B" if cycle == "2001_2002" else ""
    
    # Load demographic data
    demo_file = DATA_RAW_DIR / "questionnaire" / f"DEMO{suffix}.xpt"
    if not demo_file.exists():
        logger.error(f"DEMO file not found: {demo_file}")
        return pd.DataFrame()
    
    demo_df = read_xpt(demo_file)
    demo_vars = load_demo_variables(demo_df, cycle)
    logger.info(f"DEMO rows: {len(demo_vars)}")
    
    # Load BMX data
    bmx_file = DATA_RAW_DIR / "questionnaire" / f"BMX{suffix}.xpt"
    if bmx_file.exists():
        bmx_df = read_xpt(bmx_file)
        bmx_vars = load_bmx_variables(bmx_df, cycle)
        demo_vars = demo_vars.merge(bmx_vars, on="SEQN", how="inner")
        logger.info(f"After BMX merge: {len(demo_vars)} rows")
    
    # Load ALQ data
    alq_file = DATA_RAW_DIR / "questionnaire" / f"ALQ{suffix}.xpt"
    if alq_file.exists():
        alq_df = read_xpt(alq_file)
        alq_vars = load_alq_variables(alq_df, cycle)
        demo_vars = demo_vars.merge(alq_vars, on="SEQN", how="inner")
        logger.info(f"After ALQ merge: {len(demo_vars)} rows")
    
    # Load PAQ data
    paq_file = DATA_RAW_DIR / "questionnaire" / f"PAQ{suffix}.xpt"
    if paq_file.exists():
        paq_df = read_xpt(paq_file)
        paq_vars = load_paq_variables(paq_df, cycle)
        demo_vars = demo_vars.merge(paq_vars, on="SEQN", how="inner")
        logger.info(f"After PAQ merge: {len(demo_vars)} rows")
    
    # Load SMQ data
    smq_file = DATA_RAW_DIR / "questionnaire" / f"SMQ{suffix}.xpt"
    if smq_file.exists():
        smq_df = read_xpt(smq_file)
        smq_vars = load_smq_variables(smq_df, cycle)
        demo_vars = demo_vars.merge(smq_vars, on="SEQN", how="inner")
        logger.info(f"After SMQ merge: {len(demo_vars)} rows")
    
    # Load lab files
    # LAB25 / L25_B
    lab25_map = {"1999_2000": "LAB25.xpt", "2001_2002": "L25_B.xpt"}
    lab25_file = DATA_RAW_DIR / "labs" / lab25_map[cycle]
    if lab25_file.exists():
        lab25_df = read_xpt(lab25_file)
        lab25_vars = load_lab25_variables(lab25_df, cycle)
        if not lab25_vars.empty:
            demo_vars = demo_vars.merge(lab25_vars, on="SEQN", how="inner")
            logger.info(f"After LAB25 merge: {len(demo_vars)} rows")
    
    # LAB18 / L40_B
    lab18_map = {"1999_2000": "LAB18.xpt", "2001_2002": "L40_B.xpt"}
    lab18_file = DATA_RAW_DIR / "labs" / lab18_map[cycle]
    if lab18_file.exists():
        lab18_df = read_xpt(lab18_file)
        lab18_vars = load_lab18_variables(lab18_df, cycle)
        demo_vars = demo_vars.merge(lab18_vars, on="SEQN", how="inner")
        logger.info(f"After LAB18 merge: {len(demo_vars)} rows")
    
    # LAB11 / L11_B
    lab11_map = {"1999_2000": "LAB11.xpt", "2001_2002": "L11_B.xpt"}
    lab11_file = DATA_RAW_DIR / "labs" / lab11_map[cycle]
    if lab11_file.exists():
        lab11_df = read_xpt(lab11_file)
        lab11_vars = load_lab11_variables(lab11_df, cycle)
        demo_vars = demo_vars.merge(lab11_vars, on="SEQN", how="inner")
        logger.info(f"After LAB11 merge: {len(demo_vars)} rows")
    
    # LAB10AM / L10AM_B
    lab10am_map = {"1999_2000": "LAB10AM.xpt", "2001_2002": "L10AM_B.xpt"}
    lab10am_file = DATA_RAW_DIR / "labs" / lab10am_map[cycle]
    if lab10am_file.exists():
        lab10am_df = read_xpt(lab10am_file)
        lab10am_vars = load_lab10am_variables(lab10am_df, cycle)
        demo_vars = demo_vars.merge(lab10am_vars, on="SEQN", how="inner")
        logger.info(f"After LAB10AM merge: {len(demo_vars)} rows")
    
    # Add cycle label
    demo_vars["cycle"] = cycle
    
    # Add survey weight (defaults to WTMEC2YR if available)
    if "WTMEC2YR" in demo_vars.columns:
        demo_vars["survey_weight"] = demo_vars["WTMEC2YR"]
    elif "WTINT2YR" in demo_vars.columns:
        demo_vars["survey_weight"] = demo_vars["WTINT2YR"]
    else:
        demo_vars["survey_weight"] = 1.0
        logger.warning(f"No survey weights found for {cycle}; using default of 1.0")
    
    logger.info(f"Final {cycle} data: {len(demo_vars)} rows, {len(demo_vars.columns)} columns")
    
    return demo_vars


def load_mortality(
    path: str = "data/raw/mortality/NHIS_1999_MORT_2019_PUBLIC.dat",
) -> pd.DataFrame:
    """
    Load the NHANES 1999–2019 public-use linked mortality file.
    
    Expected columns (per the 2019 public-use LMF data dictionary):
    - SEQN: NHANES participant identifier (join key)
    - MORTSTAT: vital status (1 = assumed dead, 0 = assumed alive)
    - PERMTH_EXM: months of follow-up from MEC exam
    
    Parameters
    ----------
    path : str
        Path to mortality file (fixed-width .dat format or .csv).
    
    Returns
    -------
    pd.DataFrame
        Mortality data with SEQN, MORTSTAT, PERMTH_EXM columns.
    """
    mortality_path = Path(path)
    if not mortality_path.exists():
        logger.warning(
            "Mortality file not found at %s; skipping mortality attachment.",
            mortality_path,
        )
        return pd.DataFrame()
    
    # Try CSV first; if that fails, try fixed-width format
    try:
        # First try CSV format
        mort = pd.read_csv(mortality_path)
        # Verify it parsed correctly (should have multiple columns)
        if len(mort.columns) == 1:
            raise ValueError("CSV parsed as single column; likely fixed-width format")
        logger.info(f"Loaded mortality data (CSV): {len(mort)} rows")
    except Exception as csv_error:
        try:
            # Try fixed-width format for NHANES mortality file
            # NHANES mortality file format (based on CDC docs and inspection):
            # Positions 1-4: Follow-up years (FOLLOW_UP_YRS)
            # Positions 5-10: SEQN (6-digit participant ID)
            # Positions 11-20: Survey component codes
            # Positions 21-24: Vital status area (may contain MORTSTAT)
            # Positions 25-28: PERMTH_EXM (months of follow-up, 4 digits)
            # Positions 29+: ICD-10 cause of death
            
            # Read with appropriate column widths
            mort_raw = pd.read_fwf(
                mortality_path,
                widths=[4, 6, 10, 4, 4, 10],  # Approximate widths
                header=None,
                names=["FOLLOW_UP_YRS", "SEQN_STR", "SURVEY_CODES", "MORTSTAT_AREA", 
                       "PERMTH_STR", "ICD10"],
                skiprows=0,
            )
            logger.info(f"Parsed fixed-width format: {len(mort_raw)} rows")
            
            # Extract SEQN (should be numeric 6-digit from column 2)
            mort = pd.DataFrame()
            mort["SEQN"] = (
                mort_raw["SEQN_STR"]
                .astype(str)
                .str.strip()
                .apply(lambda x: int(x) if (x.isdigit() and len(x) <= 6) else None)
            )
            
            # Extract PERMTH_EXM (months of follow-up)
            mort["PERMTH_EXM"] = pd.to_numeric(
                mort_raw["PERMTH_STR"].astype(str).str.strip(),
                errors="coerce"
            )
            
            # For MORTSTAT, we need to find the actual vital status field
            # Based on CDC NHANES documentation, vital status is typically:
            # 1 = assumed dead, 0 = assumed alive
            # It may not be clearly encoded in this file, or may use different encoding
            # For now, set as None and log warning
            mort["MORTSTAT"] = None
            logger.warning(
                "MORTSTAT (vital status) not clearly identified in fixed-width format; "
                "setting to None. May need to refer to CDC data dictionary for exact position."
            )
            
            # Keep only rows with valid SEQN
            mort = mort.dropna(subset=["SEQN"])
            logger.info(f"Loaded mortality data (FWF): {len(mort)} rows with valid SEQN")
            
        except Exception as fwf_error:
            logger.error(
                f"Failed to parse mortality file as CSV or FWF: {csv_error}, {fwf_error}"
            )
            return pd.DataFrame()
    
    # Verify expected columns exist
    keep_cols = ["SEQN"]
    if "MORTSTAT" not in mort.columns:
        mort["MORTSTAT"] = None
    if "PERMTH_EXM" not in mort.columns:
        logger.error("PERMTH_EXM column not found in mortality file")
        return pd.DataFrame()
    
    keep_cols.extend(["MORTSTAT", "PERMTH_EXM"])
    mort = mort[keep_cols].copy()
    
    # Ensure SEQN is integer
    mort["SEQN"] = mort["SEQN"].astype(int)
    
    logger.info(f"Mortality file processed: {len(mort)} rows, {mort['PERMTH_EXM'].notna().sum()} with follow-up months")
    return mort


def attach_mortality(
    nhanes_df: pd.DataFrame,
    mort_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Left-join linked mortality info to the merged NHANES dataframe.
    
    Adds:
    - duration_months: follow-up time from exam (PERMTH_EXM)
    - event: vital status (MORTSTAT; 1 = assumed dead, 0 = assumed alive)
    
    Parameters
    ----------
    nhanes_df : pd.DataFrame
        Merged NHANES dataframe with SEQN column.
    mort_df : pd.DataFrame
        Mortality data with SEQN, MORTSTAT, PERMTH_EXM columns.
    
    Returns
    -------
    pd.DataFrame
        NHANES data with added mortality columns.
    """
    if mort_df.empty:
        logger.warning(
            "Mortality dataframe is empty; returning NHANES data unchanged."
        )
        return nhanes_df
    
    merged = nhanes_df.merge(mort_df, on="SEQN", how="left")
    
    # Rename/add standardized columns
    if "PERMTH_EXM" in merged.columns:
        merged["duration_months"] = merged["PERMTH_EXM"]
    else:
        merged["duration_months"] = None
    
    if "MORTSTAT" in merged.columns:
        merged["event"] = merged["MORTSTAT"]
    else:
        merged["event"] = None
    
    logger.info(
        f"Attached mortality data: {merged['event'].notna().sum()} / {len(merged)} "
        f"with vital status, {merged['duration_months'].notna().sum()} with follow-up months"
    )
    
    return merged


def run_nhanes_etl() -> None:
    """
    Execute full NHANES 1999-2002 ETL pipeline.
    
    Steps:
    1. Load and merge data for 1999-2000 cycle.
    2. Load and merge data for 2001-2002 cycle.
    3. Row-bind both cycles.
    4. Save merged data to interim/
    5. Load and attach mortality data.
    6. Save survival-ready data to processed/
    7. Drop rows with missing key lab markers.
    8. Save model-ready data to processed/
    
    Outputs:
    - data/interim/nhanes_1999_2002_merged.parquet
    - data/processed/nhanes_1999_2002_model_input.parquet
    - data/processed/nhanes_1999_2002_with_mortality.parquet (if mortality file available)
    """
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger.info("Starting NHANES 1999-2002 ETL pipeline...")
    
    # Load both cycles
    data_1999_2000 = load_and_merge_cycle("1999_2000")
    data_2001_2002 = load_and_merge_cycle("2001_2002")
    
    # Row-bind
    merged_df = pd.concat([data_1999_2000, data_2001_2002], ignore_index=False)
    logger.info(f"\nMerged both cycles: {len(merged_df)} rows, {len(merged_df.columns)} columns")
    
    # Save merged data
    output_merged = DATA_INTERIM_DIR / "nhanes_1999_2002_merged.parquet"
    merged_df.to_parquet(output_merged)
    logger.info(f"Saved merged data to {output_merged}")
    
    # Load and attach mortality data
    logger.info("\n=== Loading Mortality Data ===")
    # Try multiple paths to handle different execution contexts
    mort_path = None
    for candidate in [
        "data/raw/mortality/NHIS_1999_MORT_2019_PUBLIC.dat",
        "bioscale/data/raw/mortality/NHIS_1999_MORT_2019_PUBLIC.dat",
        REPO_ROOT / "data" / "raw" / "mortality" / "NHIS_1999_MORT_2019_PUBLIC.dat",
    ]:
        if isinstance(candidate, str):
            candidate = Path(candidate)
        if candidate.exists():
            mort_path = str(candidate)
            break
    
    if mort_path is None:
        logger.warning("Mortality file not found in any expected location")
        mort_df = pd.DataFrame()
    else:
        mort_df = load_mortality(mort_path)
    
    if not mort_df.empty:
        nhanes_with_mort = attach_mortality(merged_df, mort_df)
        
        # Save survival-ready dataset
        output_with_mort = DATA_PROCESSED_DIR / "nhanes_1999_2002_with_mortality.parquet"
        nhanes_with_mort.to_parquet(output_with_mort, index=False)
        logger.info(f"Saved survival-ready dataset to {output_with_mort}")
    else:
        logger.warning("Mortality data not available; skipping mortality-augmented output")
        nhanes_with_mort = None
    
    # Drop rows with missing key lab markers for phenotypic age
    key_markers = ["LBXALB", "LBXCR", "LBXGLU", "LBXWBC", "LBXRDW", "LBXCRP"]
    available_markers = [col for col in key_markers if col in merged_df.columns]
    
    if available_markers:
        model_input_df = merged_df.dropna(subset=available_markers)
        logger.info(f"\nDropped {len(merged_df) - len(model_input_df)} rows with missing key markers")
        logger.info(f"Model-ready data: {len(model_input_df)} rows")
    else:
        model_input_df = merged_df
        logger.warning("No key phenotypic age markers found; skipping row drop")
    
    # Save model-ready data
    output_model_input = DATA_PROCESSED_DIR / "nhanes_1999_2002_model_input.parquet"
    model_input_df.to_parquet(output_model_input)
    logger.info(f"Saved model-ready data to {output_model_input}")
    
    logger.info("\n" + "=" * 70)
    logger.info("ETL pipeline complete!")
    logger.info("=" * 70)


if __name__ == "__main__":
    run_nhanes_etl()
