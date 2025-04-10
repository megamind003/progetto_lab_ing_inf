#!/bin/bash

# Nome del file di output
output_file="output.txt"

# Pulisci il file di output se esiste già
> "$output_file"

# Funzione per aggiungere il contenuto di un file al file di output
append_file_content() {
    local file_path="$1"
    echo ""
    echo "File: $file_path" >> "$output_file"
    echo "----------------------------------------" >> "$output_file"
    cat "$file_path" >> "$output_file"
    echo "" >> "$output_file"
    echo "" >> "$output_file"
}

# Esporta il contenuto di tutti i file nella struttura di directory
append_file_content "dockerfiles/web-server/Dockerfile"
append_file_content "dockerfiles/web-server/app.py"
append_file_content "dockerfiles/web-server/requirements.txt"
append_file_content "dockerfiles/redis-cache/Dockerfile"
append_file_content "dockerfiles/redis-cache/redis.conf"
append_file_content "dockerfiles/postgres-db/Dockerfile"
append_file_content "dockerfiles/client/Dockerfile"
append_file_content "dockerfiles/client/client_simulator.py"
append_file_content "chaos-tester/docker-compose.yml"
append_file_content "chaos-tester/discovery.py"
append_file_content "chaos-tester/shutdown_script.sh"
append_file_content "/home/boss/Documents/progetto_lab_ing_inf/chaos-tester/project/run_test.sh"


echo "Contenuto dei file è stato scritto in $output_file"
