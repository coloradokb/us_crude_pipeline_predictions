import os
from dotenv import load_dotenv
import mysql.connector

class DatabaseConnector:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        # Read database connection parameters from environment variables
        self.host = os.getenv("DB_HOST")
        self.database = os.getenv("DB_DATABASE")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")

    def get_connection(self):
        # Establish a database connection and return it
        try:
            connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            print("Connected to the database")
            return connection
        except mysql.connector.Error as e:
            print(f"Error connecting to the database: {e}")
            return None

# Example usage
#if __name__ == "__main__":
#    db_connector = DatabaseConnector()
#    connection = db_connector.get_connection()
    # Use the connection for database operations
    # Remember to close the connection when done: connection.close()

