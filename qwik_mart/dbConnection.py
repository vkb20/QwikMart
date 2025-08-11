import mysql.connector
from mysql.connector import Error

def createConnection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345",
            database="qwik_mart",
            use_pure=True
        )
    except Error as e:
        print(f"Error: {e}")

    return connection
