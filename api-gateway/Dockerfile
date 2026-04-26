FROM maven:3.9.9-eclipse-temurin-21 AS build
WORKDIR /app

COPY pom.xml .
COPY auth-service/pom.xml auth-service/pom.xml
COPY api-gateway/pom.xml api-gateway/pom.xml
COPY task-service/pom.xml task-service/pom.xml
COPY api-gateway/src api-gateway/src

RUN mvn -pl api-gateway -am clean package -DskipTests

FROM eclipse-temurin:21-jre
WORKDIR /app
COPY --from=build /app/api-gateway/target/*.jar app.jar

EXPOSE 8080
ENTRYPOINT ["java","-jar","app.jar"]
