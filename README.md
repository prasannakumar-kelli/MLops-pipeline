# MLOps Assignment 1: Heart Disease Prediction

## Overview

End-to-end ML pipeline for predicting heart disease risk using the UCI Heart Disease dataset. The project covers EDA, model development, experiment tracking (MLflow), CI/CD (GitHub Actions), containerization (Docker), Kubernetes deployment, and monitoring (Prometheus + Grafana).

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌────────────┐
│  UCI Dataset │────▶│ EDA/Training │────▶│  MLflow    │
│  (fetch)     │     │  (Notebook)  │     │  Tracking  │
└─────────────┘     └──────┬───────┘     └────────────┘
                           │
                    ┌──────▼───────┐
                    │  Model PKL   │
                    │  + Pipeline  │
                    └──────┬───────┘
                           │
              ┌────────────▼────────────┐
              │  FastAPI App (app.py)   │
              │  /predict /health       │
              │  /metrics /model-info   │
              └────────────┬────────────┘
                           │
              ┌────────────▼────────────┐
              │   Docker Container      │
              └────────────┬────────────┘
                           │
         ┌─────────────────▼──────────────────┐
         │  Kubernetes (Minikube/Cloud)        │
         │  2 replicas + LoadBalancer          │
         └─────────────────┬──────────────────┘
                           │
              ┌────────────▼────────────┐
              │  Prometheus + Grafana   │
              │  (Monitoring)           │
              └─────────────────────────┘
```

## Project Structure

```
MLops/
├── MLops_Heart_Disease.ipynb   # EDA, model training, experiment tracking (Tasks 1-4)
├── app.py                      # FastAPI prediction API (Task 6)
├── Dockerfile                  # Container build (Task 6)
├── docker-compose.yml          # Local stack with monitoring (Task 8)
├── requirements.txt            # Python dependencies (Task 4)
├── model_pipeline.pkl          # Trained model pipeline (generated)
├── model_metadata.json         # Model metadata (generated)
├── heart_disease_cleaned.csv   # Cleaned dataset (generated)
├── test/
│   └── test_model.py           # Unit tests (Task 5)
├── .github/workflows/
│   └── ci-cd.yml               # GitHub Actions CI/CD (Task 5)
├── deployment/
│   ├── k8s-deployment.yaml     # Kubernetes manifests (Task 7)
│   ├── monitoring.yaml         # ServiceMonitor for Prometheus
│   └── prometheus.yml          # Prometheus config
├── screenshots/                # EDA and deployment screenshots (Task 9)
└── Mlops_Assignment1.pdf       # Assignment specification
```

## Setup Instructions

### 1. Clone and Install

```bash
cd MLops/
python -m venv venv
source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

### 2. Run Notebook (Tasks 1-4)

Open `MLops_Heart_Disease.ipynb` in VS Code/Jupyter and run all cells. This will:
- Fetch and clean the Heart Disease dataset from UCI
- Perform EDA with visualizations
- Train 3 models (Logistic Regression, Random Forest, Gradient Boosting)
- Log all experiments to MLflow
- Save the best model pipeline as `model_pipeline.pkl`

### 3. View MLflow Dashboard (Task 3)

```bash
mlflow ui --backend-store-uri file:./mlruns
# Open http://localhost:5000
```

### 4. Run Unit Tests (Task 5)

```bash
pytest test/ -v
```

### 5. Run API Locally (Task 6)

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
# API docs: http://localhost:8000/docs
```

### 6. Docker Build & Run (Task 6)

```bash
docker build -t heart-disease-api:latest .
docker run -p 8000:8000 heart-disease-api:latest

# Test the API
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"age":63,"sex":1,"cp":1,"trestbps":145,"chol":233,"fbs":1,"restecg":2,"thalach":150,"exang":0,"oldpeak":2.3,"slope":3,"ca":0,"thal":6}'
```

### 7. Kubernetes Deployment (Task 7)

```bash
# Using Minikube
minikube start
eval $(minikube docker-env)
docker build -t heart-disease-api:latest .
kubectl apply -f deployment/k8s-deployment.yaml
kubectl get pods
kubectl get svc

# Access via LoadBalancer
minikube service heart-disease-api-service
```

### 8. Monitoring Stack (Task 8)

```bash
docker compose up -d
# API:        http://localhost:8000
# Prometheus: http://localhost:9090
# Grafana:    http://localhost:3000 (admin/admin)
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root/welcome |
| `/health` | GET | Health check |
| `/predict` | POST | Make prediction (JSON input) |
| `/metrics` | GET | Prometheus metrics |
| `/model-info` | GET | Model metadata |
| `/docs` | GET | Swagger API documentation |

## Sample API Request

```json
POST /predict
{
  "age": 63, "sex": 1, "cp": 1, "trestbps": 145,
  "chol": 233, "fbs": 1, "restecg": 2, "thalach": 150,
  "exang": 0, "oldpeak": 2.3, "slope": 3, "ca": 0, "thal": 6
}
```

Response:
```json
{
  "prediction": 1,
  "prediction_label": "Disease",
  "confidence": 0.8523,
  "timestamp": "2026-05-04T15:30:00"
}
```
