#!/bin/bash
# Runs once on first init of an empty pgdata volume.
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE ROLE "$APP_DB_USER" WITH LOGIN PASSWORD '$APP_DB_PASSWORD';
    GRANT CONNECT ON DATABASE "$POSTGRES_DB" TO "$APP_DB_USER";
    GRANT USAGE, CREATE ON SCHEMA public TO "$APP_DB_USER";
    ALTER DATABASE "$POSTGRES_DB" OWNER TO "$APP_DB_USER";
EOSQL

echo "Created application role: $APP_DB_USER"
