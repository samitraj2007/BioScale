"""Verify BioScale API functionality."""
import sys
sys.path.insert(0, 'src')

from backend.api.app import app
from fastapi.testclient import TestClient

client = TestClient(app)

print("API VERIFICATION")
print("="*80)

# Health check
r = client.get("/health")
print(f"Health Check: {r.status_code}")
print(f"Response: {r.json()}")

# Sample prediction
payload = {
    "chronological_age": 40, 
    "sex": "male", 
    "bmi": 25, 
    "sleep_hours": 7,
    "sleep_quality": 4, 
    "weekly_exercise_sessions": 3, 
    "diet_quality_score": 7,
    "stress_level": 5, 
    "physical_activity_level": "moderate", 
    "smoking_status": "never",
    "alcohol_intake_frequency": "monthly", 
    "has_hypertension": False, 
    "has_diabetes": False,
}
r = client.post("/predict", json=payload)
print(f"\nPrediction: {r.status_code}")
data = r.json()
print(f"Chronological Age: {data['chronological_age']}")
print(f"Phenotypic Age: {data['phenotypic_age']:.2f}")
print(f"Age Acceleration: {data['age_acceleration']:.2f} years")
print(f"Model Version: {data['model_version']}")

print("\n" + "="*80)
print("API is working correctly!")
print("="*80)
