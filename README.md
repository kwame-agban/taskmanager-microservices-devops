# Démarrage de l'application

## Prérequis

- Java 21
- Maven 3.9+
- Node.js 20+
- Docker Desktop
- Docker Compose

---

# Architecture

L'application est composée de :

- frontend-angular : Frontend Angular
- api-gateway : API Gateway Spring Cloud Gateway
- auth-service : Service d'authentification JWT
- task-service : Service de gestion des tâches
- auth-db : Base PostgreSQL auth-service
- task-db : Base PostgreSQL task-service

---

# Démarrage avec Docker Compose

## 1. Compiler les microservices localement

### auth-service

cd auth-service
mvn clean package -DskipTests
task-service
cd ../task-service
mvn clean package -DskipTests
api-gateway
cd ../api-gateway
mvn clean package -DskipTests

2. Revenir à la racine du projet
cd ..

3. Construire les images Docker
docker compose build --no-cache

4. Démarrer les services backend
docker compose up -d
Vérification des conteneurs
docker ps

Ports utilisés :
Service	                  Port
frontend-angular	        4200
api-gateway	              8080
auth-service	            8081
task-service	            8082

auth-db	                  5433
task-db	                  5434

# Vérification des APIs
API Gateway
curl http://localhost:8080/actuator/health

Auth Service
curl http://localhost:8081/actuator/health

Task Service
curl http://localhost:8082/actuator/health

# Démarrage du Frontend Angular
cd frontend-angular
npm install
npm start

# Frontend disponible sur :
http://localhost:4200

# Authentification
# Login
curl -X POST "http://localhost:8080/api/auth/login" \
-H "Content-Type: application/json" \
-d "{\"username\":\"user.nom\",\"password\":\"password\"}"

Réponse :
{
  "token": "...",
  "tokenType": "Bearer"
}

# Arrêt des services
docker compose down

# Rebuild après modification du code
# Après une modification Java :
mvn clean package -DskipTests
docker compose build
docker compose up -d

# Logs Docker
# Task Service
docker logs -f task-service

# API Gateway
docker logs -f api-gateway

# Auth Service
docker logs -f auth-service
