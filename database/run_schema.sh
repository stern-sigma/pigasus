source .env
sqlcmd -S $SERVER -d $DB_NAME -U $USERNAME -P $PASSWORD -i schema.sql