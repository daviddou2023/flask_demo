from flask import Flask, jsonify, render_template
import sqlite3

app = Flask(__name__)
DATABASE_PATH = r'E:\qt_data\sensordata.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM env_data ORDER BY timestamp DESC LIMIT 20")
    rows = cursor.fetchall()
    conn.close()

    data = {
        "timestamp": [row["timestamp"] for row in rows],
        "co2": [row["co2"] for row in rows],
        "ch2o": [row["ch2o"] for row in rows],
        "tvoc": [row["tvoc"] for row in rows],
        "pm2_5": [row["pm2_5"] for row in rows],
        "pm10": [row["pm10"] for row in rows],
        "temp": [row["temp"] for row in rows],
        "hum": [row["hum"] for row in rows],
    }

    return jsonify(data)

@app.route('/gps_data')
def gps_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT latitude, longitude FROM gps_data ORDER BY timestamp DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    data = {
        "latitude": row["latitude"],
        "longitude": row["longitude"]
    }

    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
