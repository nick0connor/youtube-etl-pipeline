import os
from dotenv import load_dotenv
import psycopg
from datetime import datetime

load_dotenv()

db_username = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")

with psycopg.connect(f"dbname=py-proj user={db_username} password={db_password} host=localhost port=5432") as connection:
    with connection.cursor() as cursor:
        
        cursor.execute("SELECT * FROM video_info;")
        records = cursor.fetchall()
        print("Data from Database:- ", records)
        
        values = ('New Version Video', datetime.now(), 1738)
        cursor.execute(
            "INSERT INTO video_info (video_name, upload_date, like_count) \
                VALUES (%s, %s, %s)",
            values
        )
        connection.commit()
        print("Pushed video")
        
        cursor.execute("SELECT * FROM video_info;")
        records = cursor.fetchall()
        print("Data from Database:- ", records)