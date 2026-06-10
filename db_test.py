import os
from dotenv import load_dotenv
import psycopg2
from datetime import datetime

load_dotenv()

db_username = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")

connection = psycopg2.connect(database="py-proj", user=db_username, password=db_password, host="localhost", port=5432)

cursor = connection.cursor()

cursor.execute("SELECT * FROM video_info;")
record = cursor.fetchall()
print("Data from Databse:- ", record)

values = ('Python Video', datetime.now(), 7)
cursor.execute(
    "INSERT INTO video_info (video_name, upload_date, like_count) \
        VALUES (%s, %s, %s)",
    values
    )
connection.commit()

cursor.execute("SELECT * FROM video_info;")
record = cursor.fetchall()
print("Data from Databse:- ", record)