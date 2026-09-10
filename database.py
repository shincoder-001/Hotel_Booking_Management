import os
import MySQLdb

def get_connection():
    connection = MySQLdb.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        passwd=os.getenv("DB_PASSWORD"),
        db=os.getenv("DB_NAME", "hotel_management"),
        port=int(os.getenv("DB_PORT", "3306"))
    )
    return connection