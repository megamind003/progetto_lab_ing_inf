#!/bin/bash

# Esegui l'analisi
python discovery.py

# Ferma tutti i container
docker-compose down -v

# Genera report finale
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
REPORT_FILE="traffic_logs/final_report_${TIMESTAMP}.md"

echo "# Final System Report" > $REPORT_FILE
echo "## Container Analysis" >> $REPORT_FILE
echo '```json' >> $REPORT_FILE
cat traffic_logs/container_report.json >> $REPORT_FILE
echo '```' >> $REPORT_FILE

echo "## Log Summary" >> $REPORT_FILE
# Modifica queste righe
echo "### Web Server Logs" >> $REPORT_FILE
[ -f traffic_logs/web/server.log ] && tail -n 10 traffic_logs/web/server.log >> $REPORT_FILE || echo "No web logs" >> $REPORT_FILE

echo "### Redis Logs" >> $REPORT_FILE
[ -f traffic_logs/redis/access.log ] && tail -n 10 traffic_logs/redis/access.log >> $REPORT_FILE || echo "No redis logs" >> $REPORT_FILE


echo "Report generated at ${TIMESTAMP}" >> $REPORT_FILE