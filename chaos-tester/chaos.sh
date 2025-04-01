#!/bin/bash

COMPOSE_FILE="docker-compose.yml"
REPORT_DIR="report"
SLEEP_AFTER_FAILURE=10
PROJECT_NAME="chaos-tester"

mkdir -p $REPORT_DIR
REPORT="$REPORT_DIR/report_$(date +%Y%m%d_%H%M%S).md"
echo "# Chaos Testing Report" > $REPORT

SERVICES=$(docker-compose -p $PROJECT_NAME -f $COMPOSE_FILE config --services)

check_services_health() {
    for service in $SERVICES; do
        container_id=$(docker-compose -p $PROJECT_NAME -f $COMPOSE_FILE ps -q $service)
        if [ -z "$container_id" ]; then
            echo " - $service: not found"
        else
            status=$(docker inspect -f '{{.State.Status}}' $container_id)
            health=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}no healthcheck{{end}}' $container_id)
            echo " - $service: $status (health: $health)"
        fi
    done
}

for service_to_stop in $SERVICES; do
    echo "## Testing failure of: $service_to_stop" >> $REPORT
    echo "Stopping $service_to_stop..."
    docker-compose -p $PROJECT_NAME -f $COMPOSE_FILE stop $service_to_stop

    echo "Waiting for system reaction..."
    sleep $SLEEP_AFTER_FAILURE

    echo "Current status:" >> $REPORT
    check_services_health >> $REPORT

    echo "Restarting $service_to_stop..."
    docker-compose -p $PROJECT_NAME -f $COMPOSE_FILE up -d --no-deps $service_to_stop

    echo "---" >> $REPORT
done

echo "Report generato: $REPORT"
# script per test container

