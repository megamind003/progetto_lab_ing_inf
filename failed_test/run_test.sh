#!/bin/bash
set -e

# Path corretto alla directory del compose
COMPOSE_DIR="$HOME/Documents/progetto_lab_ing_inf/chaos-tester/project/chaos-tester"

# Pulizia ambiente
echo "Pulizia ambiente..."
cd "$COMPOSE_DIR"
docker-compose down -v --remove-orphans

# Build immagini
echo "Building immagini..."
docker-compose build

# Avvio servizi
echo "Avvio servizi..."
docker-compose up -d

# Attesa healthcheck
echo "Attesa avvio servizi..."
services=("redis" "postgres" "web")
for service in "${services[@]}"; do
    until [ "$(docker inspect -f '{{.State.Health.Status}}' chaos-tester_${service}_1)" == "healthy" ]; do
        sleep 5
        echo "Attendo ${service}..."
    done
done

# Avvio client manualmente se necessario
echo "Avvio client..."
docker-compose up -d client

echo "Esecuzione test per 30 secondi..."
sleep 30

# Shutdown e report
echo "Generazione report..."
./shutdown_script.sh

echo "Test completato!"