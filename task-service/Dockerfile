FROM maven:3.9.9-eclipse-temurin-21 AS build
WORKDIR /app

COPY pom.xml .
COPY auth-service/pom.xml auth-service/pom.xml
COPY api-gateway/pom.xml api-gateway/pom.xml
COPY task-service/pom.xml task-service/pom.xml
COPY task-service/src task-service/src

RUN mvn -pl task-service -am clean package -DskipTests

FROM eclipse-temurin:21-jre
WORKDIR /app
COPY --from=build /app/task-service/target/*.jar app.jar

EXPOSE 8082
ENTRYPOINT ["java","-jar","app.jar"]

