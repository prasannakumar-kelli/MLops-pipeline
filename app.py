"""
Heart Disease Prediction API
FastAPI application serving the trained ML model.
Task 6: Model Containerization & Task 8: Monitoring/Logging
"""

import pickle
import json
import logging
import time
from datetime import datetime

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response

# Configure logging (Task 8)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Prometheus metrics (Task 8)
REQUEST_COUNT = Counter('prediction_requests_total', 'Total prediction requests', ['status'])
PREDICTION_LATENCY = Histogram('prediction_latency_seconds', 'Prediction latency')
PREDICTION_RESULT = Counter('prediction_results', 'Prediction outcomes', ['result'])

# Load model and metadata
try:
    with open('model_pipeline.pkl', 'rb') as f:
        pipeline = pickle.load(f)
    with open('model_metadata.json', 'r') as f:
        metadata = json.load(f)
    logger.info("Model and metadata loaded successfully.")
except FileNotFoundError as e:
    logger.error(f"Model files not found: {e}")
    raise

app = FastAPI(
    title="Heart Disease Prediction API",
    description="ML model API for predicting heart disease risk based on patient health data.",
    version="1.0.0"
)


class PatientData(BaseModel):
    """Input schema for patient health data."""
    age: float = Field(..., description="Age in years")
    sex: float = Field(..., description="Sex (1=male, 0=female)")
    cp: float = Field(..., description="Chest pain type (1-4)")
    trestbps: float = Field(..., description="Resting blood pressure (mm Hg)")
    chol: float = Field(..., description="Serum cholesterol (mg/dl)")
    fbs: float = Field(..., description="Fasting blood sugar > 120mg/dl (1=true, 0=false)")
    restecg: float = Field(..., description="Resting ECG results (0-2)")
    thalach: float = Field(..., description="Max heart rate achieved")
    exang: float = Field(..., description="Exercise induced angina (1=yes, 0=no)")
    oldpeak: float = Field(..., description="ST depression induced by exercise")
    slope: float = Field(..., description="Slope of peak exercise ST segment")
    ca: float = Field(..., description="Number of major vessels colored by fluoroscopy (0-3)")
    thal: float = Field(..., description="Thalassemia (3=normal, 6=fixed defect, 7=reversible defect)")

    class Config:
        json_schema_extra = {
            "example": {
                "age": 63, "sex": 1, "cp": 1, "trestbps": 145, "chol": 233,
                "fbs": 1, "restecg": 2, "thalach": 150, "exang": 0,
                "oldpeak": 2.3, "slope": 3, "ca": 0, "thal": 6
            }
        }


class PredictionResponse(BaseModel):
    prediction: int
    prediction_label: str
    confidence: float
    timestamp: str


@app.get("/")
def root():
    return {"message": "Heart Disease Prediction API", "status": "healthy"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "model": metadata.get("model_type", "unknown")}


@app.post("/predict", response_model=PredictionResponse)
def predict(patient: PatientData):
    """Predict heart disease risk for a patient."""
    start_time = time.time()
    try:
        # Convert input to DataFrame with correct feature order
        input_dict = patient.model_dump()
        feature_names = metadata['feature_names']
        input_data = pd.DataFrame([{f: input_dict.get(f, 0) for f in feature_names}])

        # Make prediction
        prediction = int(pipeline.predict(input_data)[0])
        probability = float(pipeline.predict_proba(input_data)[0][1])

        result = PredictionResponse(
            prediction=prediction,
            prediction_label="Disease" if prediction == 1 else "No Disease",
            confidence=round(probability, 4),
            timestamp=datetime.now().isoformat()
        )

        # Log & metrics
        latency = time.time() - start_time
        REQUEST_COUNT.labels(status='success').inc()
        PREDICTION_LATENCY.observe(latency)
        PREDICTION_RESULT.labels(result=result.prediction_label).inc()
        logger.info(f"Prediction: {result.prediction_label} (conf={probability:.3f}), latency={latency:.4f}s")

        return result

    except Exception as e:
        REQUEST_COUNT.labels(status='error').inc()
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type="text/plain")


@app.get("/model-info")
def model_info():
    """Return model metadata."""
    return metadata


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
