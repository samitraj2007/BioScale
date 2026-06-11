"""Test script for BioScale API."""

import sys
sys.path.insert(0, 'src')

from fastapi.testclient import TestClient
from backend.api.app import app

client = TestClient(app)

print("=" * 80)
print("Testing BioScale API")
print("=" * 80)

# Test 1: Health check
print("\n[Test 1] Health Check")
response = client.get("/health")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test 2: Prediction with valid data
print("\n[Test 2] Prediction - Valid Request")
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

response = client.post("/predict", json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test 3: Prediction with different values
print("\n[Test 3] Prediction - Female, Younger")
payload["sex"] = "female"
payload["chronological_age"] = 35
payload["bmi"] = 24.0
payload["smoking_status"] = "current"

response = client.post("/predict", json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test 4: Invalid request (missing field)
print("\n[Test 4] Invalid Request - Missing Field")
bad_payload = {"chronological_age": 45}
response = client.post("/predict", json=bad_payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test 5: Invalid request (invalid value)
print("\n[Test 5] Invalid Request - Out of Range")
bad_payload = payload.copy()
bad_payload["chronological_age"] = -5  # Invalid
response = client.post("/predict", json=bad_payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

print("\n" + "=" * 80)
print("All tests completed!")
print("=" * 80)
