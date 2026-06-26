from flask import Flask, jsonify, render_template
import sqlite3
import serial


app = Flask(__name__)
DATABASE_PATH = r'E:\qt_data\sensordata.db'

# 添加timeout参数
ser = serial.Serial('COM15', 115200,8, 'N', 1)

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

@app.route('/health_data')
def health_data():
    # 如果串口未打开，尝试打开串口
    if not ser.is_open:
        try:
            ser.open()
        except serial.SerialException as e:
            return jsonify({"error": f"无法打开串口: {str(e)}"})

    try:
        # 检查是否有足够的数据可供读取
        if ser.in_waiting >= 88:
            data = ser.read(88)
            hex_data = ' '.join(format(byte, '02X') for byte in data)

            # 计算心率和血氧数据
            try:
                heart_rate = int(hex_data[195:197], 16)
                spo2 = int(hex_data[198:200], 16)
                return jsonify({"heart_rate": heart_rate, "spo2": spo2})
            except (ValueError, IndexError) as e:
                return jsonify({"error": f"数据处理错误: {str(e)}"})
        else:
            return jsonify({"heart_rate": None, "spo2": None})
    finally:
        # 无论是否发生异常，都要关闭串口
        ser.close()

if __name__ == '__main__':
    app.run()

