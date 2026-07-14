#!/usr/bin/env python3
"""
devops_files.py
Prépare et contrôle les fichiers nécessaires au déploiement DevOps
du projet TaskManager Microservices.

Fonctions principales :
- détecte les microservices du projet ;
- vérifie les Dockerfile, pom.xml, package.json, docker-compose.yml et .env ;
- vérifie les ressources Kubernetes et les workflows GitHub Actions ;
- crée les dossiers DevOps manquants ;
- crée des fichiers .dockerignore standards lorsqu'ils sont absents ;
- génère un rapport de préparation ;
- peut constituer un dossier "devops_bundle" sans modifier les fichiers sources.

Le script n'est pas exécuté automatiquement par Docker Compose.
Il doit être lancé explicitement :
    python devops_files.py check
    python devops_files.py prepare
    python devops_files.py bundle
"""

from __future__ import annotations

import argparse
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parent

BACKEND_SERVICES = (
    "api-gateway",
    "auth-service",
    "task-service",
    "ai-review-service",
    "ai-assistant-service",
    "ai-planner-service",
    "ai-ops-service",
)

FRONTEND_SERVICE = "frontend-angular"

REQUIRED_ROOT_FILES = (
    "docker-compose.yml",
    ".env",
)

OPTIONAL_ROOT_FILES = (
    "pom.xml",
    "README.md",
    "devops_ci.py",
)

K8S_EXPECTED_FILES = (
    "namespace.yml",
    "configmap.yml",
    "secret.yml",
    "api-gateway.yml",
    "auth-service.yml",
    "task-service.yml",
    "ingress.yml",
)

WORKFLOW_EXPECTED_FILES = (
    "ci.yml",
    "cd.yml",
    "ai-review.yml",
)

BACKEND_DOCKERIGNORE = """\
target/
.git/
.idea/
*.iml
*.log
.env
"""

FRONTEND_DOCKERIGNORE = """\
node_modules/
dist/
.git/
.idea/
*.log
.env
"""


@dataclass(frozen=True)
class CheckResult:
    path: Path
    required: bool
    exists: bool
    message: str


def relative(path: Path) -> str:
    """Retourne un chemin lisible par rapport à la racine du projet."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def check_file(path: Path, *, required: bool, description: str) -> CheckResult:
    exists = path.is_file()
    return CheckResult(
        path=path,
        required=required,
        exists=exists,
        message=description,
    )


def check_directory(path: Path, *, required: bool, description: str) -> CheckResult:
    exists = path.is_dir()
    return CheckResult(
        path=path,
        required=required,
        exists=exists,
        message=description,
    )


def discover_services() -> tuple[list[str], list[str]]:
    """
    Retourne :
    - les services connus présents ;
    - les dossiers inconnus ressemblant à des microservices.
    """
    known = [
        service
        for service in (*BACKEND_SERVICES, FRONTEND_SERVICE)
        if (PROJECT_ROOT / service).is_dir()
    ]

    ignored = {
        ".git",
        ".github",
        ".idea",
        ".mvn",
        "k8s",
        "public",
        "target",
        "devops_bundle",
        "__pycache__",
    }

    unknown: list[str] = []
    for item in PROJECT_ROOT.iterdir():
        if not item.is_dir() or item.name in ignored or item.name in known:
            continue

        looks_like_service = (
            (item / "pom.xml").is_file()
            or (item / "package.json").is_file()
            or (item / "Dockerfile").is_file()
        )
        if looks_like_service:
            unknown.append(item.name)

    return sorted(known), sorted(unknown)


def collect_checks() -> list[CheckResult]:
    """Construit la liste complète des contrôles DevOps."""
    results: list[CheckResult] = []

    for filename in REQUIRED_ROOT_FILES:
        results.append(
            check_file(
                PROJECT_ROOT / filename,
                required=True,
                description="Fichier indispensable à l'exécution locale",
            )
        )

    for filename in OPTIONAL_ROOT_FILES:
        results.append(
            check_file(
                PROJECT_ROOT / filename,
                required=False,
                description="Fichier utile au projet ou à l'automatisation",
            )
        )

    for service in BACKEND_SERVICES:
        service_dir = PROJECT_ROOT / service
        service_exists = service_dir.is_dir()

        results.append(
            check_directory(
                service_dir,
                required=service in {"api-gateway", "auth-service", "task-service"},
                description="Répertoire du microservice Spring Boot",
            )
        )

        if service_exists:
            results.extend(
                [
                    check_file(
                        service_dir / "Dockerfile",
                        required=True,
                        description=f"Dockerfile de {service}",
                    ),
                    check_file(
                        service_dir / "pom.xml",
                        required=True,
                        description=f"Configuration Maven de {service}",
                    ),
                    check_directory(
                        service_dir / "src",
                        required=True,
                        description=f"Code source de {service}",
                    ),
                    check_file(
                        service_dir / ".dockerignore",
                        required=False,
                        description=f"Exclusions du contexte Docker de {service}",
                    ),
                ]
            )

    frontend_dir = PROJECT_ROOT / FRONTEND_SERVICE
    results.append(
        check_directory(
            frontend_dir,
            required=True,
            description="Répertoire du frontend Angular",
        )
    )

    if frontend_dir.is_dir():
        results.extend(
            [
                check_file(
                    frontend_dir / "Dockerfile",
                    required=True,
                    description="Dockerfile du frontend Angular",
                ),
                check_file(
                    frontend_dir / "package.json",
                    required=True,
                    description="Configuration npm du frontend Angular",
                ),
                check_directory(
                    frontend_dir / "src",
                    required=True,
                    description="Code source Angular",
                ),
                check_file(
                    frontend_dir / ".dockerignore",
                    required=False,
                    description="Exclusions du contexte Docker Angular",
                ),
            ]
        )

    k8s_dir = PROJECT_ROOT / "k8s"
    results.append(
        check_directory(
            k8s_dir,
            required=False,
            description="Répertoire des manifestes Kubernetes",
        )
    )

    if k8s_dir.is_dir():
        for filename in K8S_EXPECTED_FILES:
            results.append(
                check_file(
                    k8s_dir / filename,
                    required=False,
                    description="Manifeste Kubernetes attendu",
                )
            )

    workflows_dir = PROJECT_ROOT / ".github" / "workflows"
    results.append(
        check_directory(
            workflows_dir,
            required=False,
            description="Répertoire des workflows GitHub Actions",
        )
    )

    if workflows_dir.is_dir():
        for filename in WORKFLOW_EXPECTED_FILES:
            results.append(
                check_file(
                    workflows_dir / filename,
                    required=False,
                    description="Workflow GitHub Actions attendu",
                )
            )

    return results


def print_results(results: Iterable[CheckResult]) -> tuple[int, int]:
    """Affiche les contrôles et retourne le nombre d'erreurs et d'avertissements."""
    errors = 0
    warnings = 0

    print("\n=== Contrôle des fichiers DevOps ===\n")

    for result in results:
        if result.exists:
            status = "OK"
        elif result.required:
            status = "ERREUR"
            errors += 1
        else:
            status = "AVERTISSEMENT"
            warnings += 1

        print(f"[{status:13}] {relative(result.path)}")
        if not result.exists:
            print(f"                {result.message}")

    print("\n=== Résumé ===")
    print(f"Erreurs bloquantes : {errors}")
    print(f"Avertissements     : {warnings}")

    return errors, warnings


def create_file_if_missing(path: Path, content: str) -> bool:
    """Crée un fichier uniquement s'il n'existe pas déjà."""
    if path.exists():
        return False

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"[CRÉÉ] {relative(path)}")
    return True


def prepare_project() -> None:
    """
    Prépare les ressources non destructives :
    - création de k8s et .github/workflows ;
    - création des .dockerignore manquants ;
    - création d'un dossier de rapports.
    """
    print("\n=== Préparation non destructive ===\n")

    directories = (
        PROJECT_ROOT / "k8s",
        PROJECT_ROOT / ".github" / "workflows",
        PROJECT_ROOT / "devops-reports",
    )

    for directory in directories:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            print(f"[CRÉÉ] {relative(directory)}/")
        else:
            print(f"[EXISTE] {relative(directory)}/")

    for service in BACKEND_SERVICES:
        service_dir = PROJECT_ROOT / service
        if service_dir.is_dir():
            create_file_if_missing(
                service_dir / ".dockerignore",
                BACKEND_DOCKERIGNORE,
            )

    frontend_dir = PROJECT_ROOT / FRONTEND_SERVICE
    if frontend_dir.is_dir():
        create_file_if_missing(
            frontend_dir / ".dockerignore",
            FRONTEND_DOCKERIGNORE,
        )

    report_path = write_report(collect_checks())
    print(f"\nRapport généré : {relative(report_path)}")
    print("Aucun Dockerfile, docker-compose.yml ou manifeste existant n'a été écrasé.")


def write_report(results: Iterable[CheckResult]) -> Path:
    """Génère un rapport texte daté."""
    report_dir = PROJECT_ROOT / "devops-reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    report_path = report_dir / f"devops-files-report-{timestamp}.txt"

    lines = [
        "RAPPORT DE PRÉPARATION DEVOPS",
        f"Projet : {PROJECT_ROOT.name}",
        f"Date   : {datetime.now().isoformat(timespec='seconds')}",
        "",
    ]

    for result in results:
        if result.exists:
            status = "OK"
        elif result.required:
            status = "ERREUR"
        else:
            status = "AVERTISSEMENT"

        lines.append(f"[{status}] {relative(result.path)} - {result.message}")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def safe_copy(source: Path, destination: Path) -> None:
    """Copie un fichier ou un dossier sans modifier la source."""
    if source.is_dir():
        shutil.copytree(source, destination, dirs_exist_ok=True)
    elif source.is_file():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def build_bundle() -> Path:
    """
    Constitue un paquet contenant les ressources DevOps déjà présentes.
    Ce paquet peut être archivé ou transmis à un pipeline.
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    bundle_dir = PROJECT_ROOT / "devops_bundle" / timestamp
    bundle_dir.mkdir(parents=True, exist_ok=False)

    root_files = (
        "docker-compose.yml",
        ".env",
        "pom.xml",
        "devops_ci.py",
        "devops_files.py",
    )

    for filename in root_files:
        safe_copy(PROJECT_ROOT / filename, bundle_dir / filename)

    safe_copy(PROJECT_ROOT / "k8s", bundle_dir / "k8s")
    safe_copy(
        PROJECT_ROOT / ".github" / "workflows",
        bundle_dir / ".github" / "workflows",
    )

    services, unknown_services = discover_services()
    for service in services + unknown_services:
        service_dir = PROJECT_ROOT / service
        destination = bundle_dir / service

        for filename in ("Dockerfile", ".dockerignore", "pom.xml", "package.json"):
            safe_copy(service_dir / filename, destination / filename)

    report_path = write_report(collect_checks())
    safe_copy(report_path, bundle_dir / "reports" / report_path.name)

    archive_path = shutil.make_archive(str(bundle_dir), "zip", root_dir=bundle_dir)
    print(f"\nBundle créé : {relative(bundle_dir)}")
    print(f"Archive ZIP : {relative(Path(archive_path))}")
    return Path(archive_path)


def show_services() -> None:
    known, unknown = discover_services()

    print("\n=== Services détectés ===")
    for service in known:
        print(f"[CONNU]   {service}")

    for service in unknown:
        print(f"[AUTRE]   {service}")

    if not known and not unknown:
        print("Aucun microservice détecté.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prépare et contrôle les fichiers DevOps du projet TaskManager."
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="check",
        choices=("check", "prepare", "bundle", "services"),
        help=(
            "check : contrôle les fichiers ; "
            "prepare : crée les ressources non destructives ; "
            "bundle : crée une archive DevOps ; "
            "services : affiche les services détectés"
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    print(f"Racine du projet : {PROJECT_ROOT}")

    if args.command == "services":
        show_services()
        return 0

    if args.command == "prepare":
        prepare_project()
        results = collect_checks()
        errors, _ = print_results(results)
        return 1 if errors else 0

    if args.command == "bundle":
        results = collect_checks()
        errors, _ = print_results(results)
        if errors:
            print(
                "\nLe bundle n'a pas été créé, car des fichiers obligatoires manquent.",
                file=sys.stderr,
            )
            return 1

        build_bundle()
        return 0

    results = collect_checks()
    errors, _ = print_results(results)

    if errors:
        print(
            "\nPréparation incomplète. Corrigez les erreurs avant le déploiement.",
            file=sys.stderr,
        )
        return 1

    print("\nLes fichiers indispensables au déploiement local sont présents.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
