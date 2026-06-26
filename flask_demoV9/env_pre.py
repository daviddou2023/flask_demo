import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score


data = np.array([
    [400, 0.01, 0.1, 10, 20, 25, 60, 0.2],  # 低风险
    [450, 0.02, 0.12, 15, 25, 26, 55, 0.25],  # 低风险
    [600, 0.03, 0.2, 30, 40, 30, 70, 0.5],  # 中等风险
    [800, 0.05, 0.3, 50, 80, 32, 75, 0.7],  # 较高风险
    [1000, 0.08, 0.4, 70, 150, 35, 80, 0.85],  # 高风险
    [1200, 0.1, 0.5, 90, 180, 37, 85, 0.9],  # 高风险
    [1500, 0.12, 0.6, 120, 200, 40, 90, 0.95],  # 极高风险
    [1800, 0.15, 0.7, 150, 220, 42, 95, 1.0],  # 极高风险
    [500, 0.02, 0.15, 20, 30, 27, 65, 0.35],  # 中等风险
    [700, 0.04, 0.25, 40, 60, 28, 72, 0.55],  # 中等风险
    [900, 0.06, 0.35, 60, 100, 31, 78, 0.75],  # 较高风险
    [1100, 0.09, 0.45, 80, 160, 33, 82, 0.8],  # 高风险
    [1300, 0.11, 0.55, 100, 180, 36, 88, 0.9],  # 高风险
    [1600, 0.14, 0.65, 130, 210, 39, 92, 0.98],  # 极高风险
    [2000, 0.16, 0.75, 170, 240, 43, 97, 1.0],  # 极高风险
    # 更多数据...
])

# 数据与标签分离
X = data[:, :-1]
y = data[:, -1]

# 数据归一化处理
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# 将数据分为训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# 创建线性回归模型
model = LinearRegression()

# 训练模型
model.fit(X_train, y_train)

# 评估模型
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f"测试集均方误差: {mse}")
print(f"测试集R²: {r2}")

# 预测作业风险等级
new_data = np.array([[500, 0.02, 0.15, 20, 30, 27, 65]])  # 新的环境数据
new_data_scaled = scaler.transform(new_data)
predicted_risk_level = model.predict(new_data_scaled)
print(f"预测的作业风险等级: {predicted_risk_level[0]}")
