TaskManager Microservices
=========================

Ce projet repose sur une architecture microservices composée de plusieurs modules backend (Spring Boot) et d’un frontend Angular.

Lancement de l'application :
1. Démarrer le frontend Angular

	Se placer dans le répertoire du frontend :

	cd frontend-angular

	Lancer le serveur de développement :

	ng serve

	Une fois démarré, ouvrir le navigateur à l’adresse suivante :

    http://localhost:4200

2. Démarrer le microservice API Gateway

	Méthode 1 : Depuis IntelliJ
	Ouvrir la classe ApiGatewayApplication
	Cliquer sur "Run" ou faire un clic droit → Run

	Méthode 2 : En ligne de commande (Maven)
	cd api-gateway
	mvn spring-boot:run

	Méthode 3 : Via le jar
	Après compilation :

	mvn clean install

	Puis :
	cd api-gateway/target
	java -jar api-gateway-0.0.1-SNAPSHOT.jar

3. Démarrer le microservice Auth Service

	Méthode 1 : Depuis IntelliJ
	Ouvrir la classe AuthServiceApplication
	Cliquer sur "Run" ou clic droit → Run

	Méthode 2 : En ligne de commande (Maven)
	cd auth-service
	mvn spring-boot:run

	Méthode 3 : Via le jar

	Après compilation :
	mvn clean install

	Puis :

	cd auth-service/target
	java -jar auth-service-0.0.1-SNAPSHOT.jar
	
Build du projet
Depuis la racine :
mvn clean install

Prérequis
Java 21 ou supérieur
Maven
Node.js et Angular CLI
IntelliJ IDEA recommandé