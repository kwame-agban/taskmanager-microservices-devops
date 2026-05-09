# Task Manager Microservices -- Kubernetes Deployment

## Description

Microservices app with: - auth-service (JWT) - task-service -
api-gateway - PostgreSQL - Angular frontend

## Run with Kubernetes

### Build images

mvn clean package -DskipTests
docker build -t api-gateway . // ou bien, docker build -t api-gateway ./api-gateway
docker build -t auth-service . // ou bien, docker build -t auth-service ./auth-service
docker build -t task-service . // ou bien, docker build -t task-service ./task-service

### Deploy

kubectl apply -f k8s/ -n taskmanager

### Check

kubectl get pods -n taskmanager
kubectl get svc -n taskmanager

### Port forward

kubectl port-forward svc/api-gateway 8080:8080 -n taskmanager

### Test

curl http://localhost:8080/actuator/health

### Login

curl -X POST "http://localhost:8080/api/auth/login" \
-H "Content-Type: application/json" \
-d "{\"username\":\"user.nom\",\"password\":\"password\"}"

