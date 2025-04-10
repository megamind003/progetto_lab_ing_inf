#!/bin/bash

# Parameters: database name (required), username (optional), password (optional), --sudo (optional)
DB_NAME=$1
DB_USER=""
DB_PASS=""
USE_SUDO="no"

# Parse arguments
for arg in "$@"; do
    case $arg in
        --sudo)
            USE_SUDO="yes"
            shift
            ;;
        *)
            if [ -z "$DB_NAME" ]; then
                DB_NAME=$arg
            elif [ -z "$DB_USER" ]; then
                DB_USER=$arg
            elif [ -z "$DB_PASS" ]; then
                DB_PASS=$arg
            fi
            shift
            ;;
    esac
done

# Check if database name is provided
if [ -z "$DB_NAME" ]; then
    echo "Usage: $0 database_name [username] [password] [--sudo]"
    echo "Username and password are optional"
    echo "Use --sudo to run with root privileges (will prompt for sudo password)"
    exit 1
fi

# Function to build MariaDB command base
mariadb_cmd_base() {
    local cmd="mariadb -D $DB_NAME"
    if [ "$USE_SUDO" = "yes" ]; then
        cmd="sudo $cmd"
    elif [ -n "$DB_USER" ]; then
        cmd="$cmd -u $DB_USER"
        if [ -n "$DB_PASS" ]; then
            cmd="$cmd -p$DB_PASS"
        fi
    fi
    echo "$cmd"
}

# Function to get list of tables
get_tables() {
    local cmd=$(mariadb_cmd_base)
    $cmd -e "SHOW TABLES" 2>/dev/null | tail -n +2
}

# Function to show table content with better formatting
show_table() {
    local table=$1
    local cmd=$(mariadb_cmd_base)
    
    # Get column names
    local columns=$($cmd -e "SHOW COLUMNS FROM $table" 2>/dev/null | tail -n +2 | awk '{print $1}' | tr '\n' '\t' | sed 's/\t$//')
    
    # Get column list for IFNULL
    local column_list=$($cmd -e "SHOW COLUMNS FROM $table" 2>/dev/null | tail -n +2 | awk '{print "IFNULL(" $1 ", \"\")"}' | paste -sd ",")
    
    # Get data with NULLs replaced by empty string
    local data=$($cmd -e "SELECT $column_list FROM $table" 2>/dev/null | tail -n +2)
    
    # Calculate width for borders (based on longest line)
    local formatted=$(echo -e "$columns\n$data" | column -t -s $'\t')
    local width=$(echo "$formatted" | awk '{print length($0)}' | sort -nr | head -n 1)
    width=$((width + 4)) # Add padding for borders
    
    # Print top border
    printf '┌'; printf '─' $((width-2)); printf '┐\n'
    
    # Print table content (left-aligned)
    echo -e "$columns\n$data" | column -t -s $'\t' | sed 's/^/│ /;s/$/ │/'
    
    # Print bottom border
    printf '└'; printf '─' $((width-2)); printf '┘\n'
}

# Test connection first
CONN_TEST=$(mariadb_cmd_base)
if ! $CONN_TEST -e "SELECT 1" >/dev/null 2>&1; then
    echo "Error: Cannot connect to database '$DB_NAME'"
    if [ "$USE_SUDO" = "yes" ]; then
        echo "Sudo failed - check sudo privileges"
    elif [ -n "$DB_USER" ]; then
        echo "Check username '$DB_USER' and password"
    else
        echo "Try providing a username and password, or use --sudo option"
    fi
    exit 1
fi

# Get all tables
TABLES=$(get_tables)
if [ -z "$TABLES" ]; then
    echo "No tables found in database '$DB_NAME' or access denied"
    exit 1
fi

# Process each table
for table in $TABLES
do
    echo "=== TABELLA: $table ==="
    show_table "$table"
    echo ""
done