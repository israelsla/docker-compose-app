from flask import Flask, request, make_response
import os
import datetime
import mysql.connector

app = Flask(__name__)
counter = 0

# פרטי חיבור למסד הנתונים (חשוב לשנות לפרטים שלכם!)
mydb = mysql.connector.connect(
  host="db",  # שם השירות ב-docker-compose
  user="my_user",       # **חשוב מאוד לשנות!**
  password="my_password",   # **חשוב מאוד לשנות!**
  database="my_database" # **חשוב מאוד לשנות!**
)

@app.route("/")
def home():
    global counter
    cursor = mydb.cursor()
    try:
        cursor.execute("SELECT counter FROM counter_table")
        result = cursor.fetchone()

        if result:
            counter = result[0]
        else:
            cursor.execute("CREATE TABLE IF NOT EXISTS counter_table (counter INT)")
            cursor.execute("INSERT INTO counter_table (counter) VALUES (0)")
            mydb.commit()

        counter += 1
        cursor.execute("UPDATE counter_table SET counter = %s", (counter,))
        mydb.commit()
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return "Error connecting to database", 500

    internal_ip = os.environ.get("HOSTNAME")  # כתובת ה-IP הפנימית של הקונטיינר

    resp = make_response(internal_ip)
    resp.set_cookie('my_cookie', internal_ip, max_age=300)  # cookie ל-5 דקות

    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)  # כתובת ה-IP של הלקוח
    now = datetime.datetime.now()
    try:
        cursor.execute("CREATE TABLE IF NOT EXISTS access_log (timestamp DATETIME, client_ip VARCHAR(255), internal_ip VARCHAR(255))")
        cursor.execute("INSERT INTO access_log (timestamp, client_ip, internal_ip) VALUES (%s, %s, %s)", (now, client_ip, internal_ip))
        mydb.commit()
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return "Error connecting to database", 500
    cursor.close()

    return resp

@app.route("/showcount")
def show_count():
    return str(counter)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)  # האזנה בכל הכתובות ובפורט 5000
