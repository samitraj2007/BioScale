"""
BioScale Lifestyle Model FastAPI Backend.

Serves phenotypic age predictions using a trained LifestyleRegressor model.

Usage:
    uvicorn backend.api.app:app --reload

Or from the project root:
    cd bioscale
    python -m uvicorn backend.api.app:app --reload --host 0.0.0.0 --port 8000
"""

import logging
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import from bioscale package
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from bioscale import config
from bioscale.models.lifestyle_regressor import LifestyleRegressor
from bioscale.models.calibration import calibrate_phenotypic_age

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Global model cache (loaded on startup)
_model = None


def load_model() -> LifestyleRegressor:
    """Load the trained LifestyleRegressor model."""
    global _model
    
    if _model is not None:
        return _model
    
    model_path = config.MODELS_DIR / "lifestyle_regressor.joblib"
    
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found at {model_path}. "
            "Please train the model using train_pipeline.py first."
        )
    
    logger.info(f"Loading model from {model_path}...")
    _model = LifestyleRegressor.load(model_path)
    logger.info("Model loaded successfully.")
    
    return _model


# ============================================================================
# Pydantic Request/Response Models
# ============================================================================


class PredictRequest(BaseModel):
    """Request payload for phenotypic age prediction."""
    
    chronological_age: float = Field(
        ..., 
        gt=0, 
        le=150,
        description="Age in years"
    )
    sex: Literal["male", "female", "other", "unknown"] = Field(
        ..., 
        description="Biological sex"
    )
    bmi: float = Field(
        ..., 
        gt=10, 
        lt=60,
        description="Body Mass Index (kg/m²)"
    )
    sleep_hours: float = Field(
        ..., 
        ge=0, 
        le=24,
        description="Average sleep hours per night"
    )
    sleep_quality: int = Field(
        ..., 
        ge=1, 
        le=5,
        description="Sleep quality rating (1=poor, 5=excellent)"
    )
    weekly_exercise_sessions: int = Field(
        ..., 
        ge=0, 
        le=7,
        description="Number of exercise sessions per week"
    )
    diet_quality_score: int = Field(
        ..., 
        ge=1, 
        le=10,
        description="Diet quality score (1=poor, 10=excellent)"
    )
    stress_level: int = Field(
        ..., 
        ge=1, 
        le=10,
        description="Stress level (1=minimal, 10=extreme)"
    )
    physical_activity_level: Literal["low", "moderate", "high"] = Field(
        ..., 
        description="Physical activity level"
    )
    smoking_status: Literal["never", "former", "current"] = Field(
        ..., 
        description="Smoking status"
    )
    alcohol_intake_frequency: Literal["never", "monthly", "weekly", "daily"] = Field(
        ..., 
        description="Frequency of alcohol consumption"
    )
    has_hypertension: bool = Field(
        ..., 
        description="Whether person has hypertension diagnosis"
    )
    has_diabetes: bool = Field(
        ..., 
        description="Whether person has diabetes diagnosis"
    )


class PredictResponse(BaseModel):
    """Response payload with phenotypic age prediction."""
    
    chronological_age: float = Field(
        ..., 
        description="Input chronological age"
    )
    phenotypic_age: float = Field(
        ..., 
        description="Predicted phenotypic (biological) age"
    )
    age_acceleration: float = Field(
        ..., 
        description="Difference: phenotypic_age - chronological_age (positive = accelerated aging)"
    )
    model_version: str = Field(
        ..., 
        description="Version of the model used"
    )


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(..., description="Service status")
    model_version: str = Field(..., description="Deployed model version")


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="BioScale Lifestyle Model API",
    description="Phenotypic age prediction based on lifestyle and health factors.",
    version=config.MODEL_VERSION,
)

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for simplicity; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """
    Best-effort model load on startup.

    Predictions use the calibrated phenotypic-age mapping
    (`bioscale.models.calibration`), which does not require the trained joblib
    artifact, so a missing model file is logged but not fatal.
    """
    try:
        load_model()
        logger.info("Startup: Model loaded successfully.")
    except Exception as e:
        logger.warning(f"Startup: model artifact not loaded ({e}); using calibrator only.")


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        model_version=config.MODEL_VERSION,
    )


@app.post("/predict", response_model=PredictResponse)
def predict_phenotypic_age(request: PredictRequest) -> PredictResponse:
    """
    Predict phenotypic age from lifestyle and health factors.
    
    Args:
        request: User features in JSON format
        
    Returns:
        Predicted phenotypic age and age acceleration
        
    Raises:
        HTTPException: If model is not loaded or prediction fails
    """
    try:
        # Calibrated, bounded phenotypic age (anchored to chronological age and
        # adjusted by an interpretable health-risk score). See
        # bioscale.models.calibration for the formula and bounds.
        result = calibrate_phenotypic_age(request.chronological_age, request.dict())

        logger.info(
            f"Prediction: chron_age={result.chronological_age:.1f}, "
            f"pheno_age={result.phenotypic_age:.1f}, "
            f"accel={result.age_acceleration:.1f}"
        )

        return PredictResponse(
            chronological_age=result.chronological_age,
            phenotypic_age=result.phenotypic_age,
            age_acceleration=result.age_acceleration,
            model_version=config.MODEL_VERSION,
        )

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}",
        )


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 80)
    print("BioScale Lifestyle Model API")
    print("=" * 80)
    print("\nStarting server on http://0.0.0.0:8000")
    print("Interactive API docs: http://0.0.0.0:8000/docs")
    print("Alternative docs: http://0.0.0.0:8000/redoc")
    print("\nExample request:")
    print("""
curl -X POST "http://localhost:8000/predict" \\
  -H "Content-Type: application/json" \\
  -d '{
    "chronological_age": 45,
    "sex": "male",
    "bmi": 28.5,
    "sleep_hours": 7.0,
    "sleep_quality": 4,
    "weekly_exercise_sessions": 3,
    "diet_quality_score": 7,
    "stress_level": 6,
    "physical_activity_level": "moderate",
    "smoking_status": "never",
    "alcohol_intake_frequency": "weekly",
    "has_hypertension": false,
    "has_diabetes": false
  }'
    """)
    print("\n" + "=" * 80)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
