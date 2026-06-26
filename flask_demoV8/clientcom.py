import socket
import struct
import time
import traceback
import cv2
import numpy as np


class Client(object):
    """客户端"""

    def __init__(self, addr_port=('192.168.43.242', 11000)):
        # 连接的服务器的地址
        self.addr_port = addr_port
        # 创建套接字
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 地址端口可以复用
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # 分辨率
        self.resolution = (640, 480)

    def connect(self):
        """链接服务器"""
        try:
            self.client.connect(self.addr_port)
            print('连接服务器成功')
            return True
        except Exception as e:
            traceback.print_exc()  # 打印原始的异常信息
            print('连接失败')
            return False

    def send2server(self, fps=60):
        """读摄像头数据 发送给服务器"""
        camera = cv2.VideoCapture('/dev/video0')  # 使用OpenCV原生的VideoCapture打开摄像头
        print('isOpened:', camera.isOpened())

        if not camera.isOpened():
            print("无法打开摄像头")
            return

        # Calculate the time to sleep between frames to achieve the desired FPS
        delay = 1.0 / fps

        while camera.isOpened():
            try:
                start_time = time.time()

                # Capture frame-by-frame
                ret, frame = camera.read()
                if not ret:
                    print("无法读取摄像头帧")
                    break

                # Resize and compress the frame
                frame = cv2.resize(frame, self.resolution)
                ret, img = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])  # Reduced quality for faster transmission

                # Convert to numpy array and then to binary data
                img_code = np.array(img)
                img = img_code.tobytes()

                # Get the data length
                length = len(img)

                # Pack the data and send it
                all_data = struct.pack('ihh', length, self.resolution[0], self.resolution[1]) + img
                self.client.send(all_data)

                # Calculate the processing time and sleep to maintain the frame rate
                elapsed_time = time.time() - start_time
                if elapsed_time < delay:
                    time.sleep(delay - elapsed_time)
            except Exception as e:
                camera.release()  # 释放摄像头
                traceback.print_exc()
                break

        camera.release()


if __name__ == '__main__':
    client = Client()
    if client.connect():
        client.send2server(fps=20)  # Set the desired FPS (e.g., 20 FPS)
