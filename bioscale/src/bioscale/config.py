from pathlib import Path

# Root directory (…/bioscale)
ROOT_DIR = Path(__file__).resolve().parents[2]

# Data paths
DATA_RAW_DIR       = ROOT_DIR / "data" / "raw"
DATA_INTERIM_DIR   = ROOT_DIR / "data" / "interim"
DATA_PROCESSED_DIR = ROOT_DIR / "data" / "processed"

LABS_DIR           = DATA_RAW_DIR / "labs"
QUESTIONNAIRE_DIR  = DATA_RAW_DIR / "questionnaire"
MORTALITY_DIR      = DATA_RAW_DIR / "mortality"
METADATA_DIR       = DATA_RAW_DIR / "metadata"

# Models
MODELS_DIR = ROOT_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Reproducibility
RANDOM_STATE  = 42
MODEL_VERSION = "v1.1.0-calibrated"

# Split ratios
TEST_SIZE = 0.15
VAL_SIZE  = 0.15

# Survival config
SURVIVAL_DURATION_COL  = "duration_months"
SURVIVAL_EVENT_COL     = "event"
SURVIVAL_HORIZON_YEARS = 10.0

# Stage 2 feature lists (must match training/inference)
NUMERIC_FEATURES = [
    "chronological_age",
    "bmi",
    "sleep_hours",
    "sleep_quality",
    "weekly_exercise_sessions",
    "diet_quality_score",
    "stress_level",
]

CATEGORICAL_FEATURES = [
    "sex",
    "physical_activity_level",
    "smoking_status",
    "alcohol_intake_frequency",
]

BOOL_FEATURES = [
    "has_hypertension",
    "has_diabetes",
]

LIFESTYLE_FEATURE_COLS = NUMERIC_FEATURES + CATEGORICAL_FEATURES + BOOL_FEATURES
TARGET_COL             = "phenotypic_age"