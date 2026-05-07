#!/bin/bash
# =============================================================
# Minikube + Podman Setup for Heart Disease API (Production Env)
# =============================================================
set -e

echo "============================================"
echo "  Heart Disease API - Minikube Deployment"
echo "============================================"

# --- Step 1: Start minikube with podman driver ---
echo ""
echo "[Step 1] Starting minikube with podman driver..."
if minikube status --format='{{.Host}}' 2>/dev/null | grep -q "Running"; then
    echo "  Minikube is already running."
else
    minikube start --driver=podman --container-runtime=containerd
    echo "  Minikube started successfully."
fi

# --- Step 2: Point shell to minikube's container runtime ---
echo ""
echo "[Step 2] Configuring environment for minikube's container runtime..."
eval $(minikube docker-env 2>/dev/null) || true

# --- Step 3: Build Docker image inside minikube ---
echo ""
echo "[Step 3] Building Docker image inside minikube..."
minikube image build -t heart-disease-api:latest .

echo "  Image built successfully."

# --- Step 4: Apply Kubernetes manifests ---
echo ""
echo "[Step 4] Deploying to Kubernetes..."
kubectl apply -f deployment/k8s-deployment.yaml
echo "  Deployment and Service applied."

# --- Step 5: Wait for pods to be ready ---
echo ""
echo "[Step 5] Waiting for pods to be ready..."
kubectl rollout status deployment/heart-disease-api --timeout=120s
echo "  All pods are ready!"

# --- Step 6: Port-forward to localhost:8080 ---
echo ""
echo "[Step 6] Setting up port-forward on localhost:8080..."
echo "  API will be available at: http://localhost:8080"
echo ""
kubectl port-forward deployment/heart-disease-api 8080:8000 &
PF_PID=$!
echo "  Port-forward started (PID: $PF_PID)"
echo ""
echo "  Test with:"
echo "    curl http://localhost:8080/health"
echo "    curl -X POST http://localhost:8080/predict -H 'Content-Type: application/json' -d '{\"age\":63,\"sex\":1,\"cp\":1,\"trestbps\":145,\"chol\":233,\"fbs\":1,\"restecg\":2,\"thalach\":150,\"exang\":0,\"oldpeak\":2.3,\"slope\":3,\"ca\":0,\"thal\":6}'"
echo ""
echo "  To stop port-forward: kill $PF_PID"
echo ""
echo "  Or use port-forward:"
echo "    kubectl port-forward svc/heart-disease-api-service 8000:80"

# --- Step 7: Show status ---
echo ""
echo "[Step 7] Deployment Status:"
echo "---"
kubectl get pods -l app=heart-disease-api
echo "---"
kubectl get svc heart-disease-api-service
echo ""
echo "============================================"
echo "  Deployment Complete!"
echo "============================================"
echo ""
echo "Quick test command:"
echo '  curl -X POST http://localhost:8000/predict \'
echo '    -H "Content-Type: application/json" \'
echo '    -d '"'"'{"age":63,"sex":1,"cp":1,"trestbps":145,"chol":233,"fbs":1,"restecg":2,"thalach":150,"exang":0,"oldpeak":2.3,"slope":3,"ca":0,"thal":6}'"'"''
