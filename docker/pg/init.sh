#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  CREATE ROLE catherine WITH LOGIN PASSWORD "$CATHERINE_PASSWORD";
  CREATE DATABASE catherine OWNER catherine;
EOSQL

psql -v ON_ERROR_STOP=1 --username "catherine" --dbname "catherine" <<-EOSQL
  CREATE EXTENSION IF NOT EXISTS pg_trgm;
EOSQL

