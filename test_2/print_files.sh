#!/bin/bash

# Nome del file di output
output_file="output.txt"

# Pulisci il file di output se esiste già
> "$output_file"

# Funzione per aggiungere il contenuto di un file al file di output
append_file_content() {
    local file_path="$1"
    echo "" >> "$output_file"
    echo "File: $file_path" >> "$output_file"
    echo "----------------------------------------" >> "$output_file"
    cat "$file_path" >> "$output_file"
    echo "" >> "$output_file"
    echo "" >> "$output_file"
}

# Esporta il contenuto di tutti i file nella struttura di directory
append_file_content "cont1/app/__init__.py"
append_file_content "cont1/app/main.py"
append_file_content "cont1/Dockerfile"
append_file_content "cont1/requirements.txt"
append_file_content "cont2/app/main.py"
append_file_content "cont2/Dockerfile"
append_file_content "cont2/requirements.txt"
append_file_content "cont3/init.sql"
append_file_content "docker-compose.yml"
append_file_content "docker_visualizer.py"
append_file_content "print_files.sh"

echo "Contenuto dei file è stato scritto in $output_file"
