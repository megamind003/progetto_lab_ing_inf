# script per test container


#!/bin/bash

# Configurazioni
COMPOSE_FILE="docker-compose.yml"
REPORT_DIR="report"
SLEEP_AFTER_FAILURE=10  # Attesa dopo il failure (in secondi)

# Inizializza il report
mkdir -p $REPORT_DIR
REPORT="$REPORT_DIR/report_$(date +%Y%m%d_%H%M%S).md"
echo "# Chaos Testing Report" > $REPORT

# Ottieni lista servizi
SERVICES=$(docker-compose -f $COMPOSE_FILE config --services)

# Funzione per verificare lo stato dei servizi
check_services_health() {
    for service in $SERVICES; do
        status=$(docker inspect --format='{{.State.Status}}' $(docker-compose -f $COMPOSE_FILE ps -q $service))
        echo " - $service: $status"
    done
}

# Test per ogni servizio
for service_to_stop in $SERVICES; do
    echo "## Testing failure of: $service_to_stop" >> $REPORT
    echo "Stopping $service_to_stop..."
    docker-compose -f $COMPOSE_FILE stop $service_to_stop

    echo "Waiting for system reaction..."
    sleep $SLEEP_AFTER_FAILURE

    echo "Current status:" >> $REPORT
    check_services_health >> $REPORT

    # Riavvia il servizio per il prossimo test
    echo "Restarting $service_to_stop..."
    docker-compose -f $COMPOSE_FILE start $service_to_stop

    echo "---" >> $REPORT
done

echo "Report generato: $REPORT"