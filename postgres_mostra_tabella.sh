# si connette al database messo come argomento del programma, mostra le tabelle nel terminale in modo piu leggibile
DB_NAME=$1

if [ -z "$DB_NAME" ]; then
    echo "bash [nome_prog] : $0 nome_database"
    exit 1
fi


for table in $(psql -U postgres -d "$DB_NAME" -t -c "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename")
do    
    columns=$(psql -U postgres -d "$DB_NAME" -t -c "SELECT string_agg(column_name, ', ') FROM information_schema.columns WHERE table_schema = 'public' AND table_name = '$table'")
    echo "=== TABELLA: $table ==="
    echo "$columns"
    psql --pset=border=2 --pset=linestyle=unicode --pset=format=aligned -U postgres -d "$DB_NAME" -c "SELECT * FROM $table"

    
    echo ""
done