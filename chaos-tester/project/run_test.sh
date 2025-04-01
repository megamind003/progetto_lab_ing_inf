#!/bin/bash
set -e

# Configurazioni
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORT_DIR="${PROJECT_DIR}/traffic_logs"
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)

# Funzione per pulire l'ambiente
cleanup() {
    echo "Pulizia dell'ambiente..."
    docker-compose down -v --remove-orphans >/dev/null 2>&1 || true
    rm -rf "${REPORT_DIR}" >/dev/null 2>&1
    mkdir -p "${REPORT_DIR}"
}

# Funzione per controllare lo stato dei servizi
check_service_health() {
    local service=$1
    local max_retries=30
    local retry_interval=5

    echo -n "Attendo che ${service} diventi healthy..."
    for ((i=1; i<=max_retries; i++)); do
        container_id=$(docker-compose ps -q ${service})
        status=$(docker inspect --format '{{.State.Health.Status}}' ${container_id} 2>/dev/null || echo "starting")
        
        if [[ "${status}" == "healthy" ]]; then
            echo -e "\r${service} healthy dopo ${i} tentativi"
            return 0
        fi
        
        sleep ${retry_interval}
        echo -ne "\rAttendo ${service} (${i}/${max_retries}) - Stato: ${status}"
    done

    echo -e "\nERRORE: ${service} non healthy dopo ${max_retries} tentativi"
    exit 1
}

# Main process
cd "${PROJECT_DIR}"
cleanup

echo "Costruzione delle immagini Docker..."
docker-compose build --quiet

echo "Avvio dei servizi..."
docker-compose up -d

# Lista servizi con healthcheck
services_with_hc=("web" "redis" "postgres")
for service in "${services_with_hc[@]}"; do
    check_service_health "${service}"
done

echo "Esecuzione del discovery..."
python discovery.py
mv "${PROJECT_DIR}/traffic_logs/container_report.json" "${REPORT_DIR}/"

echo "Simulazione traffico per 30 secondi..."
sleep 30

echo "Raccolta logs e generazione report..."
REPORT_FILE="${REPORT_DIR}/final_report_${TIMESTAMP}.md"
echo -e "# Chaos Testing Report\n" > "${REPORT_FILE}"

# Aggiungi analisi container
echo -e "## Analisi Container\n\`\`\`json" >> "${REPORT_FILE}"
cat "${REPORT_DIR}/container_report.json" >> "${REPORT_FILE}"
echo -e "\n\`\`\`" >> "${REPORT_FILE}"

# Aggiungi logs
echo -e "\n## Logs dei Servizi" >> "${REPORT_FILE}"
services=("web" "redis" "postgres" "client")
for service in "${services[@]}"; do
    echo -e "\n### Logs ${service}" >> "${REPORT_FILE}"
    echo -e "\`\`\`" >> "${REPORT_FILE}"
    docker-compose logs --no-color --tail=15 "${service}" >> "${REPORT_FILE}" 2>&1
    echo -e "\n\`\`\`" >> "${REPORT_FILE}"
done

echo -e "\nReport generato il: ${TIMESTAMP}" >> "${REPORT_FILE}"

# Cleanup finale
cleanup

echo -e "\nTest completato con successo!"
echo "Report disponibile: ${REPORT_FILE}"