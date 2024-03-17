import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

load_dotenv()

# Database connection parameters - update these with your database credentials
db_params = {
    'dbname': 'stocks_db',
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': 'localhost'
}

# SQL command to create a table
create_table_command = sql.SQL("""
    CREATE TABLE IF NOT EXISTS market (
        timestamp BIGINT,
        open DECIMAL,
        high DECIMAL,
        low DECIMAL,
        close DECIMAL,
        volume INTEGER,
        symbol VARCHAR(10)
    );
""")

def create_table():
    try:
        # Connect to your postgres DB
        conn = psycopg2.connect(**db_params)

        # Open a cursor to perform database operations
        cur = conn.cursor()

        # Execute SQL command
        cur.execute(create_table_command)

        # Commit changes
        conn.commit()

        # Close communication with the database
        cur.close()
        conn.close()
        print("Table created successfully")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    create_table()
