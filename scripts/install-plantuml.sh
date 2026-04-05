#!/bin/bash
# Install PlantUML and its dependencies on Ubuntu/Debian Linux
set -euo pipefail

echo "=== Installing PlantUML dependencies ==="

# Java (required runtime for PlantUML)
sudo apt-get update -qq
sudo apt-get install -y -qq default-jre-headless

# Graphviz (required for C4 and other diagrams with layouts)
sudo apt-get install -y -qq graphviz

# PlantUML jar
PLANTUML_VERSION="1.2024.8"
PLANTUML_JAR="/usr/local/share/plantuml/plantuml.jar"
sudo mkdir -p /usr/local/share/plantuml
sudo curl -sSL -o "$PLANTUML_JAR" \
  "https://github.com/plantuml/plantuml/releases/download/v${PLANTUML_VERSION}/plantuml-${PLANTUML_VERSION}.jar"

# Create wrapper script
sudo tee /usr/local/bin/plantuml > /dev/null <<'WRAPPER'
#!/bin/bash
java -jar /usr/local/share/plantuml/plantuml.jar "$@"
WRAPPER
sudo chmod +x /usr/local/bin/plantuml

echo "=== Verifying installation ==="
java -version 2>&1 | head -1
dot -V 2>&1
plantuml -version 2>&1 | head -1

echo ""
echo "=== Done! Usage: ==="
echo "  plantuml docs/diagrams/*.puml        # Generate PNGs"
echo "  plantuml -tsvg docs/diagrams/*.puml   # Generate SVGs"
