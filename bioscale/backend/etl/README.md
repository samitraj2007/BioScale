# NHANES ETL Pipeline Documentation

## Overview

The NHANES ETL pipeline (`backend/etl/nhanes_etl.py`) loads and harmonizes NHANES data from survey cycles 1999-2002, preparing it for phenotypic age modeling.

## Data Sources

### Input Directory Structure

```
data/raw/
├── questionnaire/
│   ├── DEMO.xpt, DEMO_B.xpt           # Demographics
│   ├── BMX.xpt, BMX_B.xpt             # Body measurements
│   ├── ALQ.xpt, ALQ_B.xpt             # Alcohol use
│   ├── PAQ.xpt, PAQ_B.xpt             # Physical activity
│   └── SMQ.xpt, SMQ_B.xpt             # Smoking status
├── labs/
│   ├── LAB25.xpt, L25_B.xpt           # CBC (Complete Blood Count)
│   ├── LAB18.xpt, L40_B.xpt           # Biochemistry
│   ├── LAB11.xpt, L11_B.xpt           # CRP
│   └── LAB10AM.xpt, L10AM_B.xpt       # Fasting glucose/insulin
└── mortality/ (TODO)
    └── nhanes_1999_2019_mortality.csv # Vital status and follow-up
```

### Survey Cycles

- **1999-2000**: Files without suffix (e.g., `DEMO.xpt`)
- **2001-2002**: Files with `_B` suffix (e.g., `DEMO_B.xpt`)

## Data Extracted by Module

### Demographics (DEMO/DEMO_B)
- `RIDAGEYR`: Age at screening
- `RIDSEX`: Sex (1=Male, 2=Female)
- `RIDRETH1`: Race/Hispanic origin
- `WTINT2YR`: Interview weight (2-year)
- `WTMEC2YR`: MEC weight (2-year)
- `SDMVSTRA`: Strata (survey design)
- `SDMVPSU`: PSU (survey design)

### Body Measurements (BMX/BMX_B)
- `BMXBMI`: Body Mass Index (kg/m²)
- `BMXWAIST`: Waist circumference (cm)
- `BMXHT`: Height (cm)
- `BMXWT`: Weight (kg)

### Lifestyle Questionnaires

#### Alcohol (ALQ/ALQ_B)
- `ALQ101`: Ever had 12 drinks/year?
- `ALQ110`: Ever had a drink?
- `ALQ120Q`: Days per week drank (last 12 months)
- `ALQ130`: Number of drinks on drinking day

#### Physical Activity (PAQ/PAQ_B)
- `PAQ605`: Engage in moderate-intensity activity?
- `PAQ610`: Days per week moderate activity
- `PAQ625`: Engage in vigorous-intensity activity?
- `PAQ630`: Days per week vigorous activity

#### Smoking (SMQ/SMQ_B)
- `SMQ020`: Smoked at least 100 cigarettes?
- `SMQ040`: Do you now smoke cigarettes?
- `SMQ050`: How long since last smoked?

### Laboratory Values

#### CBC (LAB25/L25_B)
Key variables for phenotypic age:
- `LBXWBC`: White blood cell count
- `LBXRDW`: Red cell distribution width
- `LBXLYPCT`: Lymphocyte percentage
- `LBXMCV`: Mean corpuscular volume

#### Biochemistry (LAB18/L40_B)
Key variables for phenotypic age:
- `LBXALB`: Albumin (g/dL)
- `LBXCR`: Creatinine (mg/dL)
- `LBXAP`: Alkaline phosphatase
- `LBXBUN`: Blood urea nitrogen
- `LBXGLU`: Glucose (mg/dL)

#### CRP (LAB11/L11_B)
- `LBXCRP`: C-Reactive Protein (mg/L)

#### Fasting Glucose/Insulin (LAB10AM/L10AM_B)
- `LBXGLU`: Fasting glucose (mg/dL)
- `LBXIN`: Fasting insulin

## Output Directory Structure

```
data/
├── interim/
│   └── nhanes_1999_2002_merged.parquet
│       All selected variables from both cycles, NAs included
│
├── nhanes_1999_2002_with_mortality.parquet
│   All merged NHANES variables + mortality follow-up data
│
└── nhanes_1999_2002_model_input.parquet
    Rows with complete key phenotypic age markers
    (does not include mortality - use with_mortality version for survival analysis)
```

## Mortality Integration

### Input File

The NHANES 1999–2019 public-use linked mortality file (LMF) is located at:
```
data/raw/mortality/NHIS_1999_MORT_2019_PUBLIC.dat
```

**Expected columns** (per CDC 2019 public-use LMF data dictionary):
- `SEQN`: NHANES participant identifier (join key)
- `MORTSTAT`: Vital status (1 = assumed dead, 0 = assumed alive)
- `PERMTH_EXM`: Months of follow-up from MEC exam

### Output File

The mortality-augmented dataset is saved as:
```
data/processed/nhanes_1999_2002_with_mortality.parquet
```

**Contains all NHANES variables plus:**
- `duration_months`: Follow-up time in months from MEC exam (`PERMTH_EXM`)
- `event`: Vital status indicator (MORTSTAT; 1 = dead, 0 = alive)

**Note**: This file uses **left-join**, so:
- Includes all 4,696 NHANES participants (both cycles)
- Some participants have multiple records in the mortality file (by survey component)
- Final shape: 6,787 rows × 27 columns
- `duration_months` and `event` may be NULL for participants not in mortality file

### Data Definitions

- **MORTSTAT / event**: Vital status as of data release (2019)
  - 1 = Assumed dead
  - 0 = Assumed alive
  - NULL = Not available in mortality file

- **PERMTH_EXM / duration_months**: Months of follow-up from MEC exam to either:
  - Date of death (if event = 1), or
  - Data release (Dec 31, 2019, if event = 0)
  - Range: 10–9,975 months (~0.8–831 years)

### Using for Survival Analysis

For survival/phenotypic age modeling that incorporates mortality:

```python
import pandas as pd

# Load survival-ready data
df = pd.read_parquet("data/processed/nhanes_1999_2002_with_mortality.parquet")

# Perform survival analysis using:
# - Dependent variable: 'event' (vital status)
# - Time variable: 'duration_months' (follow-up duration)
# - Covariates: All other NHANES variables (age, labs, BMI, etc.)
```

## Key Harmonization Steps

1. **Cycle Detection**: Automatically determine cycle from filename suffix (`_B` = 2001-2002)
2. **Variable Selection**: Extract only phenotypic age-relevant variables
3. **Inner Joins**: Join questionnaire + demographic + lab data within each cycle
4. **Row Binding**: Concatenate both cycles vertically
5. **Survey Weights**: Add `survey_weight` column (defaults to `WTMEC2YR`)
6. **Row Filtering**: Drop incomplete records (missing key lab markers)

## Running the Pipeline

### From Python

```python
from backend.etl import run_nhanes_etl

run_nhanes_etl()
```

### From Command Line

```bash
cd bioscale
python backend/etl/nhanes_etl.py
```

## Output Schema

### Merged Data (`nhanes_1999_2002_merged.parquet`)

Columns include:
- `SEQN`: Unique person ID
- All demographic, anthropometric, lifestyle, and lab variables
- `cycle`: Survey cycle ("1999_2000" or "2001_2002")
- `survey_weight`: Survey weight for analysis

### Model Input Data (`nhanes_1999_2002_model_input.parquet`)

Same schema as merged data, but:
- Rows with missing key lab markers removed
- Ready for phenotypic age model training

## TODOs

### 1. Mortality Data Integration ✅ COMPLETE
**Status**: Implemented  
**File**: `data/raw/mortality/NHIS_1999_MORT_2019_PUBLIC.dat`

**Completed steps**:
- ✅ Load fixed-width format mortality file
- ✅ Extract SEQN, MORTSTAT (vital status), PERMTH_EXM (follow-up months)
- ✅ Left-join to merged NHANES data by SEQN
- ✅ Output to `data/processed/nhanes_1999_2002_with_mortality.parquet`

**Current implementation**:
- Handled both CSV and fixed-width (.dat) formats
- Gracefully degrades if mortality file is unavailable
- Sets MORTSTAT=None with warning if vital status field cannot be clearly identified
- Follow-up months fully extracted and validated

**Future enhancements**:
- Verify exact CDC data dictionary positions for MORTSTAT field
- If available, add ICD-10 cause-of-death codes
- Consider aggregating multiple records per SEQN to single row

### 2. Metadata Schema
**File**: `backend/etl/nhanes_metadata.yaml` (or `.json`)

Content:
- Variable labels and descriptions
- Units of measurement
- Value mappings for categorical variables
- Data quality thresholds
- Derived variable formulas (if any)

Load in `nhanes_metadata.py` on module import.

### 3. Extended Variable Selection
For future phases, may want to add:
- Blood pressure variables (BPX)
- Dietary variables (DR1T, DR1TOT)
- Mental health variables (DPQ, GADQ)
- Kidney function variables (LBXUAID)

## Technical Notes

### XPT File Reading

The module attempts to use `pyreadstat` for robust SAS file reading, with fallback to `pandas.read_sas`:

```python
if HAS_PYREADSTAT:
    df, meta = pyreadstat.read_sas7bdat(str(filepath))
else:
    df = pd.read_sas(str(filepath), format="xpt")
```

### Merging Strategy

All joins are **inner** within cycles (intersection of available participants), then **row-bind** across cycles. This ensures:
- No duplicate SEQNs
- Only participants with complete questionnaire + lab data
- Clear separation of cycle information

### Logging

The pipeline provides detailed logging at each merge step:

```
=== Loading 1999_2000 data ===
DEMO rows: 9965
After BMX merge: 9965 rows
After ALQ merge: 9965 rows
...
Final 1999_2000 data: 8234 rows, 47 columns

Merged both cycles: 15899 rows, 47 columns
Dropped 1234 rows with missing key markers
Model-ready data: 14665 rows
```

## Example Usage

```python
import pandas as pd
from backend.etl import run_nhanes_etl

# Run ETL pipeline
run_nhanes_etl()

# Load model-ready data
df = pd.read_parquet("data/processed/nhanes_1999_2002_model_input.parquet")

# Inspect
print(f"Shape: {df.shape}")
print(f"Cycles: {df['cycle'].unique()}")
print(f"Missing markers: {df[['LBXALB', 'LBXCR']].isna().sum()}")
```

## Determinism and Extensibility

- **Deterministic**: Same input files produce identical output (no random sampling or shuffling)
- **Extensible**: New variables can be added by modifying variable selection functions
- **Robustness**: Handles missing files gracefully; logs warnings for skipped data sources
- **Traceable**: Cycle information preserved for stratified analysis

## Dependencies

- `pandas`: Data manipulation
- `pyreadstat` or `pandas.read_sas`: XPT file reading
- `numpy`: Numerical operations
- `logging`: Pipeline logging
