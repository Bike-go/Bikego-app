import os
import sys
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
db_port = os.getenv("DB_PORT")
db_schema_name = os.getenv("DB_SCHEMA_NAME")

encoded_password = quote(db_password) if db_password else ""

connection_string = f"postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"

def read_schema_file(schema_file_path):
    with open(schema_file_path, 'r') as file:
        schema_sql = file.read()
    return schema_sql

def get_existing_tables(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = %s;", (db_schema_name,))
    tables = cursor.fetchall()
    cursor.close()
    return [table[0] for table in tables]

def drop_existing_schema(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = %s;", (db_schema_name,))
    tables = cursor.fetchall()
    
    for table in tables:
        cursor.execute(sql.SQL("DROP TABLE IF EXISTS {} CASCADE;").format(sql.Identifier(table[0])))
    connection.commit()
    cursor.close()
    print("Existing schema dropped.")

def upload_schema(rebuild):
    schema_file_path = "schema.sql"
    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(connection_string)
        
        existing_tables = get_existing_tables(connection)

        if existing_tables:
            if rebuild:
                drop_existing_schema(connection)
            else:
                print("Schema already exists. Use '--rebuild' to drop and recreate.")
                return

        cursor = connection.cursor()

        schema_sql = read_schema_file(schema_file_path)
        schema_sql = schema_sql.replace("{{db_schema_name}}", db_schema_name)
        cursor.execute(schema_sql)

        connection.commit()
        print("Schema uploaded successfully.")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == "__main__":
    rebuild = '--rebuild' in sys.argv
    upload_schema(rebuild)