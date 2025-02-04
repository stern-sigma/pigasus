source .env
sqlcmd -S $SERVER -d master -U $USERNAME -P $PASSWORD -i schema.sql