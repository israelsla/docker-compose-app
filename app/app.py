# app/app.py
from flask import Flask, request, make_response
import os
import pymysql  # Install: pip install pymysql
import datetime
import socket

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")
SERVER_IP = os.environ.get("SERVER_IP")  # Get the internal IP

counter = 0  # Global counter (in-memory, will reset on container restart)
try:
    conn = pymysql.connect(DATABASE_URL)
    with conn.cursor() as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS access_log (timestamp DATETIME, client_ip VARCHAR(255), server_ip VARCHAR(255))")
        cursor.execute("CREATE TABLE IF NOT EXISTS counter_table (count INT)")
        cursor.execute("SELECT count FROM counter_table")
        result = cursor.fetchone()
        if result:
          counter = result[0]
        else:
          cursor.execute("INSERT INTO counter_table (count) VALUES (0)")
          conn.commit()
    conn.close()
except Exception as e:
    print(f"Error connecting to database or creating table: {e}")


@app.route("/")
def index():
    global counter
    try:
        conn = pymysql.connect(DATABASE_URL)
        with conn.cursor() as cursor:
            counter += 1
            cursor.execute("UPDATE counter_table SET count = %s", (counter,))
            cursor.execute("INSERT INTO access_log (timestamp, client_ip, server_ip) VALUES (%s, %s, %s)", (datetime.datetime.now(), request.remote_addr, SERVER_IP))
            conn.commit()

        conn.close()

    except Exception as e:
        print(f"Database error in index: {e}")

    response = make_response(f"Internal IP: {SERVER_IP}")
    response.set_cookie('SERVER', value=SERVER_IP, max_age=300)  # 5 minutes
    return response

@app.route("/showcount")
def show_count():
    return f"Count: {counter}"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
