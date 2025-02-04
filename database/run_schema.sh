source .env
sqlcmd -S $DB_HOST,$DB_PORT -d $DB_NAME -U $DB_USER -P $DB_PASSWORD -i schema.sql