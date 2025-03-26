#!/bin/bash

set -e
set -u

function create_user_and_database() {
    local database=$1
    local password=$2
    echo "  Creating user and database '$database' with password"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
        CREATE USER $database WITH ENCRYPTED PASSWORD '$password';
        CREATE DATABASE $database;
        GRANT ALL PRIVILEGES ON DATABASE $database TO $database;
        ALTER DATABASE $database OWNER TO $database;
EOSQL
}

if [ -n "$POSTGRES_MULTIPLE_DATABASES" ] && [ -n "$POSTGRES_PASSWORDS" ]; then
    echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"
    IFS=',' read -r -a databases <<< "$POSTGRES_MULTIPLE_DATABASES"
    IFS=',' read -r -a passwords <<< "$POSTGRES_PASSWORDS"

    if [ "${#databases[@]}" -ne "${#passwords[@]}" ]; then
        echo "Error: Number of databases and passwords must match"
        exit 1
    fi

    for i in "${!databases[@]}"; do
        create_user_and_database "${databases[$i]}" "${passwords[$i]}"
    done
    echo "Multiple databases created"
fi
