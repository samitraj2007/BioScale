"""
FastAPI application for biological age prediction.

Provides REST endpoints for lifestyle-based biological age prediction
with SHAP-based feature importance explanations.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .. import config
from .schemas import LifestyleRequest, LifestyleResponse, ShapSummary, ShapContribution
from ..models.calibration import calibrate_phenotypic_age, top_drivers

# Initialize FastAPI app
app = FastAPI(
    title="BioScale API",
    description="Biological Age Estimation with SHAP Explainability",
    version=config.MODEL_VERSION,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict:
    """
    Health check endpoint.

    Returns the API status and model version.

    Returns
    -------
    dict
        Status and version information.
    """
    return {
        "status": "ok",
        "model_version": config.MODEL_VERSION,
    }


@app.post("/predict")
def predict_biological_age(request: LifestyleRequest) -> LifestyleResponse:
    """
    Predict biological (phenotypic) age based on lifestyle and clinical factors.

    Uses a calibrated, bounded phenotypic-age mapping (see
    `bioscale.models.calibration`). The phenotypic age is anchored to
    chronological age and adjusted by an interpretable health-risk score, with
    realistic clamps so extreme inputs cannot produce absurd values. The same
    per-feature contributions drive the "top drivers" returned to the client.

    Parameters
    ----------
    request : LifestyleRequest
        Lifestyle and health information.

    Returns
    -------
    LifestyleResponse
        Predicted biological age, age acceleration, and feature contributions.
    """
    features = request.model_dump()

    result = calibrate_phenotypic_age(request.chronological_age, features)
    pos, neg = top_drivers(result.contributions, top_k=3)

    shap_summary = ShapSummary(
        top_positive=[ShapContribution(**item) for item in pos],
        top_negative=[ShapContribution(**item) for item in neg],
    )

    return LifestyleResponse(
        chronological_age=result.chronological_age,
        predicted_biological_age=result.phenotypic_age,
        age_acceleration=result.age_acceleration,
        model_version=config.MODEL_VERSION,
        shap_contributions=shap_summary,
    )
