source .env
mssql -s $DB_HOST -o $DB_PORT -d $DB_NAME -u $DB_USER -p $DB_PASSWORD
