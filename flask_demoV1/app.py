from flask import Flask, jsonify, render_template
import sqlite3

app = Flask(__name__)

# 设置数据库的绝对路径
DATABASE_PATH = r'Z\home\sensordata.db'

def get_latest_data():
    # 使用绝对路径连接到 SQLite 数据库
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM env_data ORDER BY timestamp DESC LIMIT 1''')
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            'id': row[0],
            'co2': row[1],
            'ch2o': row[2],
            'tvoc': row[3],
            'pm2_5': row[4],
            'pm10': row[5],
            'temp': row[6],
            'hum': row[7],
            'timestamp': row[8]
        }
    return {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    return jsonify(get_latest_data())

if __name__ == '__main__':
    app.run(debug=True)
