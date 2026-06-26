from flask import Flask, jsonify, render_template, Response, request
import sqlite3
import socket
import struct
import threading
import cv2
import numpy as np
import paramiko  # 用于通过SSH执行命令

app = Flask(__name__)
DATABASE_PATH = r'E:\qt_data\sensordata.db'
REMOTE_HOST = '192.168.43.101'  # 开发板的IP地址
REMOTE_USER = 'root'  # SSH登录用户名
REMOTE_PASSWORD = '123456'  # SSH登录密码


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


def generate_video_stream():
    """Generate video stream for Flask."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('192.168.43.242', 11000))
    server_socket.listen(1)
    print("等待视频客户端连接...")
    client_socket, _ = server_socket.accept()
    print("视频客户端已连接")

    try:
        while True:
            # 接收图片的长度和分辨率
            data = client_socket.recv(8)
            if not data:
                break
            length, width, height = struct.unpack('ihh', data)

            # 接收完整的图像数据
            img_data = b''  # 存放最终的图片数据
            while length > 0:
                temp_data = client_socket.recv(length)
                if not temp_data:
                    break
                img_data += temp_data
                length -= len(temp_data)

            # 把二进制数据还原
            img_array = np.frombuffer(img_data, dtype='uint8')

            # 还原成图像
            image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if image is None:
                print("解码失败，接收到的图像数据可能有误。")
                continue

            # 将图像编码为 JPEG 格式
            ret, jpeg = cv2.imencode('.jpg', image)
            if not ret:
                continue

            # 以 multipart/x-mixed-replace 格式流式传输
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

    finally:
        client_socket.close()
        server_socket.close()


@app.route('/video_feed')
def video_feed():
    return Response(generate_video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/remote_monitor', methods=['POST'])
def remote_monitor():
    """通过SSH启动远程摄像头并返回视频流URL"""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(REMOTE_HOST, username=REMOTE_USER, password=REMOTE_PASSWORD)

        # 执行远程命令以启动摄像头
        stdin, stdout, stderr = ssh.exec_command('python3 /home/clientcom.py &')
        output = stdout.read().decode()
        error = stderr.read().decode()

        ssh.close()

        if error:
            return jsonify({"status": "error", "message": error}), 500

        # 假设远程摄像头的URL是固定的
        video_url = f"http://{REMOTE_HOST}:11000/video_feed"
        return jsonify({"status": "success", "video_url": video_url})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/remote_reminder', methods=['POST'])
def remote_reminder():
    """通过SSH执行远程脚本"""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(REMOTE_HOST, username=REMOTE_USER, password=REMOTE_PASSWORD)

        # 执行远程脚本
        stdin, stdout, stderr = ssh.exec_command('sh /home/set_led.sh &')
        output = stdout.read().decode()
        error = stderr.read().decode()

        ssh.close()

        if error:
            return jsonify({"status": "error", "message": error}), 500
        return jsonify({"status": "success", "message": output})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
