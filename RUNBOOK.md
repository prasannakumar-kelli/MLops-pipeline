# MLOps Heart Disease API — User Runbook

## Status Tracker

| # | Task | Status | Files |
|---|------|--------|-------|
| 1 | Data Acquisition & EDA (5 marks) | DONE | `MLops_Heart_Disease.ipynb` (cells 1-18) |
| 2 | Feature Engineering & Model Dev (8 marks) | DONE | `MLops_Heart_Disease.ipynb` (cells 19-29) |
| 3 | Experiment Tracking - MLflow (5 marks) | DONE | `MLops_Heart_Disease.ipynb` (cells 33-34), `mlruns/` |
| 4 | Model Packaging & Reproducibility (7 marks) | DONE | `model_pipeline.pkl`, `model_metadata.json`, `requirements.txt` |
| 5 | CI/CD Pipeline & Automated Testing (8 marks) | DONE | `.github/workflows/ci-cd.yml`, `test/test_model.py` |
| 6 | Model Containerization (5 marks) | DONE | `Dockerfile`, `app.py` |
| 7 | Production Deployment (7 marks) | READY TO RUN | `deployment/k8s-deployment.yaml`, `deploy_minikube.sh` |
| 8 | Monitoring & Logging (3 marks) | DONE | `docker-compose.yml`, `deployment/grafana/`, `deployment/prometheus.yml` |
| 9 | Documentation & Reporting (2 marks) | DONE | `README.md`, `RUNBOOK.md`, `MLOps_Final_Report.docx` |

---

## Prerequisites

- **macOS** with Homebrew installed
- **Python 3.11+** with venv
- **Podman** (installed: `podman version 5.8.1`)
- **Minikube** (installed: `v1.38.1`)
- **kubectl** (bundled with minikube)

---

## Step-by-Step Procedures

### STEP 1: Environment Setup

```bash
cd MLops/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### STEP 2: Run the Notebook (Tasks 1-4)

Open `MLops_Heart_Disease.ipynb` in VS Code and **Run All Cells**. This performs:
- Data acquisition from UCI repository
- EDA with visualizations saved to `screenshots/`
- Training 3 models (Logistic Regression, Random Forest, Gradient Boosting)
- Cross-validation and test-set evaluation
- MLflow experiment logging to `mlruns/`
- Saving best model as `model_pipeline.pkl`

### STEP 3: View MLflow Dashboard (Task 3)

```bash
mlflow ui --backend-store-uri file:./mlruns
# Open browser: http://localhost:5000
```

**Screenshot checklist:**
- [ ] MLflow experiment list showing all 3 models + best model run
- [ ] Metrics comparison (accuracy, ROC-AUC)
- [ ] Artifacts tab showing logged model

### STEP 4: Run Unit Tests (Task 5)

```bash
pytest test/ -v --tb=short
```

Expected: All tests pass (data processing, model training, API input validation).

### STEP 5: Test API Locally (Task 6)

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

In another terminal:
```bash
# Health check
curl http://localhost:8000/health

# Prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"age":63,"sex":1,"cp":1,"trestbps":145,"chol":233,"fbs":1,"restecg":2,"thalach":150,"exang":0,"oldpeak":2.3,"slope":3,"ca":0,"thal":6}'

# Swagger docs
open http://localhost:8000/docs

# Prometheus metrics
curl http://localhost:8000/metrics
```

### STEP 6: Docker Build & Run (Task 6)

```bash
# Build
podman build -t heart-disease-api:latest .

# Run
podman run -d --name heart-api -p 8004:8000 heart-disease-api:latest

# Test
curl http://localhost:8004/health
curl -X POST http://localhost:8004/predict \
  -H "Content-Type: application/json" \
  -d '{"age":63,"sex":1,"cp":1,"trestbps":145,"chol":233,"fbs":1,"restecg":2,"thalach":150,"exang":0,"oldpeak":2.3,"slope":3,"ca":0,"thal":6}'

# Stop
podman stop heart-api && podman rm heart-api
```

### STEP 7: Monitoring Stack — Prometheus + Grafana (Task 8)

```bash
# Start full stack (API + Prometheus + Grafana)
docker compose up -d
# OR with podman:
podman-compose up -d

# Access:
#   API:        http://localhost:8000
#   Prometheus: http://localhost:9090
#   Grafana:    http://localhost:3000  (login: admin / admin)
```

**Grafana dashboard** is auto-provisioned with panels for:
- Total/Success/Error prediction request counts
- Prediction latency percentiles (p50, p90, p99)
- Request rate (req/s)
- Prediction outcomes over time (Disease vs No Disease)
- Prediction distribution pie chart

**Screenshot checklist:**
- [ ] Prometheus targets page showing heart-disease-api UP
- [ ] Grafana dashboard with all panels
- [ ] Make a few predictions first to populate metrics

### STEP 8: Production Deployment — Minikube + Podman (Task 7)

```bash
# Ensure podman machine is running
podman machine start   # skip if already running

# Run the deployment script
./deploy_minikube.sh
```

**What the script does:**
1. Starts minikube with podman driver
2. Builds the Docker image inside minikube
3. Applies Kubernetes deployment (2 replicas) + LoadBalancer service
4. Waits for pods to be ready
5. Shows pod/service status

**After deployment:**
```bash
# Get the service URL
minikube service heart-disease-api-service --url

# OR port-forward to localhost
kubectl port-forward svc/heart-disease-api-service 8080:80

# Test
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"age":63,"sex":1,"cp":1,"trestbps":145,"chol":233,"fbs":1,"restecg":2,"thalach":150,"exang":0,"oldpeak":2.3,"slope":3,"ca":0,"thal":6}'
```

**Verify:**
```bash
kubectl get pods -l app=heart-disease-api
kubectl get svc heart-disease-api-service
kubectl logs -l app=heart-disease-api --tail=20
```

**Screenshot checklist:**
- [ ] `kubectl get pods` showing 2/2 Running
- [ ] `kubectl get svc` showing LoadBalancer
- [ ] API response from minikube endpoint
- [ ] `minikube dashboard` (optional — web UI for k8s)

### STEP 9: Cleanup

```bash
# Stop minikube
minikube stop

# Stop monitoring stack
docker compose down   # or: podman compose down

# Deactivate venv
deactivate
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `minikube start` fails with podman | Run `podman machine start` first |
| Image not found in minikube | Use `minikube image build -t heart-disease-api:latest .` |
| Pods stuck in ImagePullBackOff | Ensure `imagePullPolicy: IfNotPresent` in k8s-deployment.yaml |
| Grafana shows "No data" | Send a few prediction requests first, then refresh |
| Port 8000 already in use | `lsof -i :8000` and kill the process, or use a different port |
