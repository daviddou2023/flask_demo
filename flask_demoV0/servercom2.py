import socket
import struct
import threading
import traceback

import cv2
import numpy as np
import os


class Server:
    def __init__(self, ip='192.168.43.242', port=11000):
        # 设置tcp服务端的socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 设置重复使用
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        # 绑定地址和端口
        self.server.bind((ip, port))
        # 设置被动监听
        self.server.listen(128)

    def run(self):
        while True:
            print('等待客户端连接')
            # 等待客户端连接
            client, addr = self.server.accept()
            print(f"客户端已连接: {addr}")
            ProcessClient(client).start()


class ProcessClient(threading.Thread):

    def __init__(self, client):
        super().__init__()
        self.client = client

        # 初始化图片保存的编号
        self.i = 0
        self.path = "E:/sample"
        os.makedirs(self.path, exist_ok=True)  # 如果文件夹不存在，创建它

        # 获取现有图片的最大序号
        file_list = [int(f.split('.')[0]) for f in os.listdir(self.path) if f.endswith('.jpg')]
        if file_list:
            self.i = max(file_list) + 1

    def run(self):
        try:
            while True:
                # 接收图片的长度和分辨率
                data = self.client.recv(8)
                if not data:
                    break
                length, width, height = struct.unpack('ihh', data)

                # 接收完整的图像数据
                img_data = b''  # 存放最终的图片数据
                while length > 0:
                    temp_data = self.client.recv(min(length, 4096))  # 分块接收
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

                # 显示图像
                cv2.imshow('capture', image)

                # 检查键盘输入保存或退出
                k = cv2.waitKey(1)
                if k == ord('k'):
                    cv2.imwrite(f"{self.path}/{self.i}.jpg", image)  # 存储路径
                    print(f"保存图片: {self.i}.jpg")
                    self.i += 1

                if k == ord('q'):
                    break

        except Exception as e:
            print(f"发生错误: {e}")
            traceback.print_exc()

        finally:
            # 断开连接时关闭窗口
            self.client.close()
            cv2.destroyAllWindows()


if __name__ == '__main__':
    server = Server()
    server.run()
