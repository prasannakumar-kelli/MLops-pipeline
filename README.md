# MLOps: Heart Disease Prediction

## Quick Links & Deliverables

| Deliverable | Location |
|-------------|----------|
| GitHub Repository | [MLops-pipeline](https://github.com/prasannakumar-kelli/MLops-pipeline) |
| Final Report | `MLOps_Final_Report.docx` (in repo) |
| Assignment Spec | `Mlops_Assignment1.pdf` (in repo) |
| Runbook | `RUNBOOK.md` — step-by-step procedures |
| CI/CD Pipeline | GitHub Actions → [Actions tab](https://github.com/prasannakumar-kelli/MLops-pipeline/actions) |
| Video Demo | MLops/mlops_pipeline-demo.mp4(in repo) |

---

## Overview

End-to-end ML pipeline for predicting heart disease risk using the UCI Heart Disease dataset. The project covers EDA, model development, experiment tracking (MLflow), CI/CD (GitHub Actions), containerization (Docker/Podman), Kubernetes deployment (Minikube), and monitoring (Prometheus + Grafana).

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
MLops-pipeline/
├── .github/workflows/
│   └── ci-cd.yml                   # GitHub Actions CI/CD pipeline (Task 5)
├── deployment/
│   ├── grafana/
│   │   ├── dashboards/
│   │   │   └── heart_disease_api.json   # Auto-provisioned Grafana dashboard
│   │   └── provisioning/
│   │       ├── dashboards/dashboard.yml
│   │       └── datasources/prometheus.yml
│   ├── k8s-deployment.yaml         # Kubernetes Deployment + Service (Task 7)
│   ├── monitoring.yaml             # ServiceMonitor for Prometheus
│   └── prometheus.yml              # Prometheus scrape config
├── screenshots/                    # EDA visualizations (7 plots)
├── test/
│   ├── __init__.py
│   └── test_model.py              # Unit tests — data, model, API (Task 5)
├── MLops_Heart_Disease.ipynb       # EDA, training, MLflow tracking (Tasks 1-4)
├── app.py                          # FastAPI prediction API (Task 6)
├── Dockerfile                      # Multi-stage container build (Task 6)
├── docker-compose.yml              # Full stack: API + Prometheus + Grafana (Task 8)
├── deploy_minikube.sh              # Automated Minikube deployment script (Task 7)
├── requirements.txt                # Pinned Python dependencies (Task 4)
├── RUNBOOK.md                      # Operational runbook with procedures
├── MLOps_Final_Report.docx         # 12-page final report (Task 9)
├── Mlops_Assignment1.pdf           # Assignment specification
└── README.md                       # This file
```

**Generated at runtime (git-ignored):**
- `model_pipeline.pkl` — Trained sklearn pipeline
- `model_metadata.json` — Model metadata (accuracy, features, timestamp)
- `heart_disease_cleaned.csv` — Cleaned dataset
- `mlruns/` — MLflow experiment logs

## Setup Instructions

### Prerequisites

- Python 3.11+
- Podman 5.x (or Docker)
- Minikube 1.38+ (for Kubernetes deployment)
- kubectl (bundled with minikube)

### 1. Clone and Install

```bash
git clone git@github.com:prasannakumar-kelli/MLops-pipeline.git
cd MLops-pipeline
python3 -m venv venv
source venv/bin/activate
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

### 6. Docker/Podman Build & Run (Task 6)

```bash
podman build -t heart-disease-api:latest .
podman run -d --name heart-api -p 8004:8000 heart-disease-api:latest

# Test
curl http://localhost:8004/health
curl -X POST http://localhost:8004/predict \
  -H "Content-Type: application/json" \
  -d '{"age":63,"sex":1,"cp":1,"trestbps":145,"chol":233,"fbs":1,"restecg":2,"thalach":150,"exang":0,"oldpeak":2.3,"slope":3,"ca":0,"thal":6}'

# Cleanup
podman stop heart-api && podman rm heart-api
```

### 7. Kubernetes Deployment (Task 7)

```bash
# Automated script (starts minikube, builds image, deploys, port-forwards to 8080)
chmod +x deploy_minikube.sh
./deploy_minikube.sh

# Verify
kubectl get pods -l app=heart-disease-api    # 2/2 Running
kubectl get svc heart-disease-api-service    # LoadBalancer

# Test via port-forward
curl http://localhost:8080/health
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"age":63,"sex":1,"cp":1,"trestbps":145,"chol":233,"fbs":1,"restecg":2,"thalach":150,"exang":0,"oldpeak":2.3,"slope":3,"ca":0,"thal":6}'
```

### 8. Monitoring Stack (Task 8)

```bash
podman-compose up -d
# API:        http://localhost:8004
# Prometheus: http://localhost:9090
# Grafana:    http://localhost:3000 (admin/admin)
```

Grafana dashboard is auto-provisioned with panels for:
- Request counts (total / success / error)
- Prediction latency percentiles (p50, p90, p99)
- Request rate (req/s)
- Prediction outcomes (Disease vs No Disease)
- Prediction distribution pie chart

---

## CI/CD Pipeline (GitHub Actions)

Triggered on every push to `main`:

| Job | Steps |
|-----|-------|
| **lint-and-test** | Install deps → flake8 lint → pytest (12 tests) |
| **train-model** | Train model → upload `model_pipeline.pkl` artifact |
| **build-docker** | Download model → Build Docker image |

View runs: [Actions tab](https://github.com/prasannakumar-kelli/MLops-pipeline/actions)

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

---

## Assignment Task Coverage

| # | Task | Marks | Status | Key Files |
|---|------|-------|--------|-----------|
| 1 | Data Acquisition & EDA | 5 | Done | `MLops_Heart_Disease.ipynb`, `screenshots/` |
| 2 | Feature Engineering & Model Dev | 8 | Done | `MLops_Heart_Disease.ipynb` |
| 3 | Experiment Tracking (MLflow) | 5 | Done | `MLops_Heart_Disease.ipynb`, `mlruns/` |
| 4 | Model Packaging & Reproducibility | 7 | Done | `model_pipeline.pkl`, `requirements.txt` |
| 5 | CI/CD & Automated Testing | 8 | Done | `.github/workflows/ci-cd.yml`, `test/test_model.py` |
| 6 | Model Containerization | 5 | Done | `Dockerfile`, `app.py` |
| 7 | Production Deployment | 7 | Done | `deployment/k8s-deployment.yaml`, `deploy_minikube.sh` |
| 8 | Monitoring & Logging | 3 | Done | `docker-compose.yml`, `deployment/grafana/` |
| 9 | Documentation & Reporting | 2 | Done | `README.md`, `RUNBOOK.md`, `MLOps_Final_Report.docx` |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11 |
| ML Framework | scikit-learn 1.8 |
| API | FastAPI + Uvicorn |
| Experiment Tracking | MLflow |
| Containerization | Podman / Docker |
| Orchestration | Kubernetes (Minikube) |
| CI/CD | GitHub Actions |
| Monitoring | Prometheus + Grafana |
| Testing | pytest + flake8 |

---

## Author

**Prasanna Kumar Kelli**  
M.Tech — Machine Learning & AI
