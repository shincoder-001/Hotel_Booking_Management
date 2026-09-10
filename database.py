import os
import MySQLdb


def get_connection():
    connection = MySQLdb.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        passwd=os.environ["DB_PASSWORD"],
        db=os.environ["DB_NAME"],
        port=int(os.environ.get("DB_PORT", "3306"))
    )

    return connection