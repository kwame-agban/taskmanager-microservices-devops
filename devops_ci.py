from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

files = {
    ".github/workflows/ci.yml": """name: CI - Build and Tests

on:
  push:
    branches: [ "dev", "main" ]
  pull_request:
    branches: [ "dev", "main" ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Java 21
        uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: 21
          cache: maven

      - name: Build backend
        run: mvn -B clean install -DskipTests

  validate-k8s:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Install kubectl
        run: |
          curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
          chmod +x kubectl
          sudo mv kubectl /usr/local/bin/

      - name: Validate Kubernetes manifests
        run: |
          kubectl apply --dry-run=client -f k8s/
""",

    ".env.example": """POSTGRES_USER=postgres
POSTGRES_PASSWORD=change_me
SPRING_DATASOURCE_USERNAME=postgres
SPRING_DATASOURCE_PASSWORD=change_me
""",
}

for file_path, content in files.items():
    path = ROOT / file_path
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        print(f"SKIP: {file_path} already exists")
    else:
        path.write_text(content, encoding="utf-8")
        print(f"CREATED: {file_path}")

