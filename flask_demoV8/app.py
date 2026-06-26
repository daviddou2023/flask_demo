from flask import Flask, request, jsonify, render_template, Response
import sqlite3
import socket
import struct
import threading
import cv2
import numpy as np
import os
import queue
import paramiko  # 用于通过SSH执行命令

app = Flask(__name__)
# DATABASE_PATH = r'E:\qt_data\sensordata.db'
# VIDEO_PORT = 11001
REMOTE_HOST = '192.168.43.101'  # 开发板的IP地址
REMOTE_USER = 'root'  # SSH登录用户名
REMOTE_PASSWORD = '123456'  # SSH登录密码
gps_data = {"latitude": 0.0, "longitude": 0.0}
env_data = {"co2": 0, "ch2o": 0, "tvoc": 0, "pm2_5": 0, "pm10": 0, "temp": 0.0, "hum": 0.0, "risk_level": 0}
@app.route('/')
def main():
    return render_template('main.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/api/gps', methods=['POST'])
def receive_gps():
    global gps_data
    data = request.json
    gps_data["latitude"] = data.get("latitude", 0.0)
    gps_data["longitude"] = data.get("longitude", 0.0)
    return jsonify({"status": "success"}), 200

@app.route('/api/env', methods=['POST'])
def receive_env():
    global env_data
    data = request.json
    env_data["co2"] = data.get("co2", 0)
    env_data["ch2o"] = data.get("ch2o", 0)
    env_data["tvoc"] = data.get("tvoc", 0)
    env_data["pm2_5"] = data.get("pm2_5", 0)
    env_data["pm10"] = data.get("pm10", 0)
    env_data["temp"] = data.get("temp", 0.0)
    env_data["hum"] = data.get("hum", 0.0)
    env_data["risk_level"] = data.get("risk_level", 0)
    return jsonify({"status": "success"}), 200

# 获取最新的GPS和环境传感器数据
@app.route('/api/get_latest_data', methods=['GET'])
def get_latest_data():
    return jsonify({"gps": gps_data, "env": env_data})

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
