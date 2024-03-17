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


def create_table():
    try:
        # Connect to your postgres DB
        conn = psycopg2.connect(**db_params)

        # Open a cursor to perform database operations
        cur = conn.cursor()

        # Execute SQL command
        cur.execute("""
                    SELECT tablename FROM pg_tables WHERE schemaname = 'public';
                    """)

        tables = cur.fetchall()

        # Drop each table
        for table in tables:
            cur.execute(f"DROP TABLE IF EXISTS {table[0]} CASCADE;")


        # Commit changes
        conn.commit()

        # Close communication with the database
        cur.close()
        conn.close()
        print("All tables have been dropped.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    create_table()
