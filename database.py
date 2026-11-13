
import os
import MySQLdb


def get_connection():
    connection = MySQLdb.connect(
        host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
        user="3xgBpZ5k6S1RDUj.root",
        passwd=os.environ["DB_PASSWORD"],
        db="hotel_management",
        port=4000,
        connect_timeout=20,
        ssl={
            "ca": "/etc/ssl/certs/ca-certificates.crt"
        }
    )

    return connection
