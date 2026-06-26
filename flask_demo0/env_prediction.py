import sys  # 导入sys模块，用于处理命令行参数
import numpy as np  # 导入numpy库，用于数组和数学运算
import json  # 导入json库，用于数据的JSON格式化
from sklearn.linear_model import LinearRegression  # 从sklearn库中导入线性回归模型


# 模拟训练数据和模型（实际使用中应加载真实训练好的模型）
def train_model():
    # 创建一个模拟的训练数据集
    data = np.array([
        [400, 0.01, 0.1, 10, 20, 25, 60, 0.2],  # 低风险
        [450, 0.02, 0.12, 15, 25, 26, 55, 0.25],  # 低风险
        [600, 0.03, 0.2, 30, 40, 30, 70, 0.5],  # 中等风险
        [800, 0.05, 0.3, 50, 80, 32, 75, 0.7],  # 较高风险
        [1000, 0.08, 0.4, 70, 150, 35, 80, 0.85],  # 高风险
        [1200, 0.1, 0.5, 90, 180, 37, 85, 0.9],  # 高风险
        [1500, 0.12, 0.6, 110, 200, 38, 90, 0.95]  # 高风险
    ])

    # 分割特征数据和目标数据
    X = data[:, :-1]  # 特征数据（前7列）
    y = data[:, -1]  # 目标数据（最后1列：风险等级）

    # 创建线性回归模型并用数据进行训练
    model = LinearRegression().fit(X, y)

    # 返回训练好的模型
    return model


def predict_risk_level(model, co2, ch2o, tvoc, pm2_5, pm10, temp, hum):
    # 将输入的传感器数据打包成一个二维数组
    features = np.array([[co2, ch2o, tvoc, pm2_5, pm10, temp, hum]])

    # 使用模型预测风险等级
    risk_level = model.predict(features)[0]

    # 确保风险等级在0到1之间
    return min(max(risk_level, 0), 1)


def main():
    # 检查命令行参数的数量
    if len(sys.argv) != 8:
        print("Usage: env_pre.py co2 ch2o tvoc pm2_5 pm10 temp hum")
        return

    # 从命令行参数中读取数据
    co2, ch2o, tvoc, pm2_5, pm10, temp, hum = map(float, sys.argv[1:])

    # 训练模型（实际使用中应加载真实训练好的模型）
    model = train_model()

    # 预测风险等级
    risk_level = predict_risk_level(model, co2, ch2o, tvoc, pm2_5, pm10, temp, hum)

    # 输出风险等级的JSON格式结果
    print(json.dumps({"risk_level": risk_level}))


if __name__ == "__main__":
    main()
