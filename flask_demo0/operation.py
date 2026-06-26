import serial
import time
import serial.tools.list_ports

ports_list = list(serial.tools.list_ports.comports())
if len(ports_list) <= 0:
    print("无串口设备。")
else:
    print("可用的串口设备如下：")
    for comport in ports_list:
        print(list(comport)[0], list(comport)[1])

ser = serial.Serial('COM15', 115200)  # 创建一个串行端口对象

try:
    while True:
        if ser.in_waiting >= 88:  # 如果串口缓冲区中有至少 88 个字节的数据可读取
            data = ser.read(88)  # 读取 88 个字节的数据
            hex_data = ' '.join(format(byte, '02X') for byte in data)  # 将读取到的数据转换为 16 进制格式
            print("Hex数据:", hex_data)  # 打印读取到的 16 进制数据

            heart_rate = int(hex_data[195:197], 16)
            spo2 = int(hex_data[198:200], 16)
            # # rsv3 = hex_data[210:212]
            # # rsv4 = hex_data[213:215]
            #
            print("心率:", int(hex_data[195:197], 16))
            print("血氧:", int(hex_data[198:200], 16))
            # print("保留字段3:", int(hex_data[210:212], 16))
            # print("保留字段4:", int(hex_data[213:215], 16))
finally:
    ser.close()  # 关闭串行端口
