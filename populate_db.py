import psycopg2
from psycopg2 import sql
from utils.preprocess import convert_to_unix_timestamp
from utils.io import read_csv_as_objects
from dotenv import load_dotenv
import os

load_dotenv()

# Database connection parameters
db_params = {
    'dbname': 'stocks_db',
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': 'localhost'
}

insert_command = sql.SQL("""
    INSERT INTO market (timestamp, open, high, low, close, volume, symbol)
    VALUES (%(timestamp)s, %(open)s, %(high)s, %(low)s, %(close)s, %(volume)s, %(symbol)s)
""")

def insert_data(data):
    try:
        # Connect to your postgres DB
        conn = psycopg2.connect(**db_params)

        # Open a cursor to perform database operations
        cur = conn.cursor()

        # Execute SQL command
        cur.execute(insert_command, data)

        # Commit changes
        conn.commit()

        # Close communication with the database
        cur.close()
        conn.close()
        print("Data inserted successfully")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    for data_object in read_csv_as_objects('data/msft_data.csv'):
        input("Press Enter to insert data...")
        data_object['open'] = float(data_object['open'])
        data_object['high'] = float(data_object['high'])
        data_object['low'] = float(data_object['low'])
        data_object['close'] = float(data_object['close'])
        data_object['volume'] = int(data_object['volume'])
        data_object['symbol'] = 'MSFT'
        data_object['timestamp'] = convert_to_unix_timestamp(data_object['timestamp'])
        insert_data(data_object)


