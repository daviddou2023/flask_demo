import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import torch


import torch.nn as nn
import torch.optim as optim
from torch.utils.mobile_optimizer import optimize_for_mobile

# 数据
data = {
    'heart_rate': [50, 40, 70, 75, 80, 85, 90, 60, 65, 78,
                   82, 88, 72, 77, 83, 87, 91, 62, 67, 79,
                   84, 89, 74, 76, 81, 86, 92, 61, 66, 69,
                   73, 95, 150, 140],
    'blood_oxygen': [75, 70, 98, 97, 95, 96, 95, 99, 98, 96,
                     95, 98, 97, 96, 95, 97, 96, 100, 99, 97,
                     95, 93, 96, 97, 93, 94, 90, 98, 97, 96,
                     94, 89, 80, 82],
    'fatigue_level': [0.92, 0.9, 0.2, 0.13, 0.14, 0.17, 0.2, 0.7, 0.3, 0.32,
                      0.25, 0.45, 0.25, 0.35, 0.42, 0.53, 0.32, 0.32, 0.33, 0.15,
                      0.57, 0.67, 0.17, 0.27, 0.38, 0.48, 0.55, 0.32, 0.33, 0.44,
                      0.54, 0.78, 0.93, 0.92]
}

# 转换为DataFrame
df = pd.DataFrame(data)

# 准备数据
X = df[['heart_rate', 'blood_oxygen']].values
y = df['fatigue_level'].values

# 划分训练和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 转换为Pytorch张量
X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
y_train_tensor = torch.tensor(y_train, dtype=torch.float32)
X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
y_test_tensor = torch.tensor(y_test, dtype=torch.float32)


# 定义神经网络模型
class NeuralNet(nn.Module):
    def __init__(self):
        super(NeuralNet, self).__init__()
        self.fc1 = nn.Linear(2, 10)
        self.fc2 = nn.Linear(10, 1)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x


model = NeuralNet()

# 定义损失函数和优化器
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

# 训练模型
num_epochs = 1000
for epoch in range(num_epochs):
    model.train()
    optimizer.zero_grad()
    outputs = model(X_train_tensor)
    loss = criterion(outputs.squeeze(), y_train_tensor)
    loss.backward()
    optimizer.step()

# 评估模型
model.eval()
# 保存模型参数
torch.save(model.state_dict(), 'fatigue_model.pth')
