# BioScale Lifestyle Model HTTP API

## Overview

A minimal FastAPI backend that serves phenotypic age predictions using the trained LifestyleRegressor model. The API accepts lifestyle and health features and returns predicted biological age, chronological age, and age acceleration.

## Quick Start

### Installation

Ensure dependencies are installed:
```bash
pip install fastapi uvicorn pydantic pandas numpy xgboost shap scikit-learn
```

### Running the Server

From the project root (`bioscale` directory):

```bash
cd bioscale
python -m uvicorn backend.api.app:app --reload --host 0.0.0.0 --port 8000
```

Or directly:
```bash
cd bioscale
python backend/api/app.py
```

Output:
```
================================================================================
BioScale Lifestyle Model API
================================================================================

Starting server on http://0.0.0.0:8000
Interactive API docs: http://0.0.0.0:8000/docs
Alternative docs: http://0.0.0.0:8000/redoc

Example request:
curl -X POST "http://localhost:8000/predict" ...
```

## API Endpoints

### 1. Health Check
**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "ok",
  "model_version": "v1.0.0"
}
```

**Example**:
```bash
curl http://localhost:8000/health
```

### 2. Phenotypic Age Prediction
**Endpoint**: `POST /predict`

**Request Body** (JSON):
```json
{
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
}
```

**Response** (JSON):
```json
{
  "chronological_age": 45.0,
  "phenotypic_age": 36.22,
  "age_acceleration": -8.78,
  "model_version": "v1.0.0"
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
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
```

## Request Fields

### Required Fields

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `chronological_age` | float | 0-150 | Age in years |
| `sex` | string | male/female/other/unknown | Biological sex |
| `bmi` | float | 10-60 | Body Mass Index (kg/m²) |
| `sleep_hours` | float | 0-24 | Average sleep hours per night |
| `sleep_quality` | int | 1-5 | Sleep quality rating (1=poor, 5=excellent) |
| `weekly_exercise_sessions` | int | 0-7 | Number of exercise sessions per week |
| `diet_quality_score` | int | 1-10 | Diet quality score (1=poor, 10=excellent) |
| `stress_level` | int | 1-10 | Stress level (1=minimal, 10=extreme) |
| `physical_activity_level` | string | low/moderate/high | Physical activity level |
| `smoking_status` | string | never/former/current | Smoking status |
| `alcohol_intake_frequency` | string | never/monthly/weekly/daily | Frequency of alcohol consumption |
| `has_hypertension` | boolean | true/false | Whether person has hypertension diagnosis |
| `has_diabetes` | boolean | true/false | Whether person has diabetes diagnosis |

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `chronological_age` | float | Input chronological age (years) |
| `phenotypic_age` | float | Predicted phenotypic (biological) age (years) |
| `age_acceleration` | float | Age acceleration: phenotypic_age - chronological_age (years). Positive = accelerated aging, negative = decelerated aging |
| `model_version` | string | Version of the model used for prediction |

## Interactive Documentation

Once the server is running, access interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Error Handling

### Missing Required Field (400 / 422)
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"chronological_age": 45}'
```

Response (422 Unprocessable Entity):
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "sex"],
      "msg": "Field required"
    },
    ...
  ]
}
```

### Out of Range Value (422)
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "chronological_age": -5,
    ...
  }'
```

Response (422 Unprocessable Entity):
```json
{
  "detail": [
    {
      "type": "greater_than",
      "loc": ["body", "chronological_age"],
      "msg": "Input should be greater than 0",
      "input": -5
    }
  ]
}
```

### Model Not Available (503)
If the model file is not found or fails to load:
```json
{
  "detail": "Model not available"
}
```

## Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Health check
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# Make prediction
payload = {
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
    "has_hypertension": False,
    "has_diabetes": False,
}

response = requests.post(f"{BASE_URL}/predict", json=payload)
result = response.json()

print(f"Chronological Age: {result['chronological_age']:.1f} years")
print(f"Phenotypic Age: {result['phenotypic_age']:.1f} years")
print(f"Age Acceleration: {result['age_acceleration']:.1f} years")
```

## Docker Deployment

Build and run as a Docker container:

```bash
docker build -t bioscale-api -f backend/Dockerfile .
docker run -p 8000:8000 bioscale-api
```

## Performance Notes

- **Model Loading**: The model is loaded once on startup and cached in memory
- **Preprocessing**: Each request applies the same preprocessor used during training
- **Inference Time**: Typically <50ms per prediction on modern hardware
- **Concurrent Requests**: FastAPI handles concurrent requests efficiently

## Architecture

```
HTTP Request (JSON)
    ↓
FastAPI Route Handler
    ↓
Pydantic Validation
    ↓
DataFrame Construction
    ↓
Model Preprocessor (ColumnTransformer)
    ↓
XGBoost Model (Booster)
    ↓
Prediction (Phenotypic Age)
    ↓
Response JSON
```

## File Structure

```
bioscale/
├── backend/
│   └── api/
│       └── app.py              # FastAPI application
├── models/
│   └── lifestyle_regressor.joblib  # Trained model
├── src/
│   └── bioscale/
│       ├── config.py           # Configuration
│       ├── models/
│       │   ├── lifestyle_regressor.py
│       │   └── persistence.py
│       └── ...
└── ...
```

## Troubleshooting

### Model Not Found
```
FileNotFoundError: Model not found at ...
```
**Solution**: Train the model using `python -m bioscale.cli.train_pipeline --use-real-data`

### Import Errors
```
ModuleNotFoundError: No module named 'bioscale'
```
**Solution**: Ensure `src` is in PYTHONPATH or use relative imports as configured

### Port Already in Use
```
OSError: [Errno 48] Address already in use
```
**Solution**: Use a different port: `--port 8001`

### CORS Issues
The API allows all origins by default. For production, restrict to specific domains in `app.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourfrontend.com"],
    ...
)
```

## Dependencies

- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **pydantic**: Data validation
- **pandas**: Data manipulation
- **numpy**: Numerical operations
- **xgboost**: Model inference
- **scikit-learn**: Preprocessing

## Model Details

- **Type**: XGBoost Regressor
- **Output**: Phenotypic Age (years)
- **Features**: 13 lifestyle and health factors
- **Version**: v1.0.0
- **Training Data**: NHANES 1999-2002 (real NHANES data)

## Testing

Run the included test client:
```bash
cd bioscale
python test_api_client.py
```

Expected output:
```
[Test 1] Health Check
Status: 200
Response: {'status': 'ok', 'model_version': 'v1.0.0'}

[Test 2] Prediction - Valid Request
Status: 200
Response: {'chronological_age': 45.0, 'phenotypic_age': 36.22, ...}

[Test 3] Prediction - Female, Younger
Status: 200
Response: {'chronological_age': 35.0, 'phenotypic_age': 29.90, ...}

[Test 4] Invalid Request - Missing Field
Status: 422

[Test 5] Invalid Request - Out of Range
Status: 422
```
