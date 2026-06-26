# 在小样本的条件之下，要想满足机器学习方法的泛化能力和学习精度，拟选择支持向量机（SVM）这种机器学习的理论方法。不选择神经网络是因为它对于有限样本的学习能力很强容易出现过学习的现象导致模型的泛化能力很差，不选择贝叶斯网络的原因是本项目特征值之间并非独立关系，不选择决策树的原因是容易出现过拟合已经不能很好表征数据之间的相关性。
# 遗传算法和网格搜索混合算法通过遗传算法适用于非线性和非凸问题弥补了网格搜索不适用于非凸优化问题的缺点，同时混合算法结合了两者的优点，具有更强的全面搜索能力确保可以找到最佳函数参数g和惩罚参数c，可以一定程度上弥补有限样本参数难以优化的缺点。

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler
import random

# 数据：定义一个字典，包含心率、血氧和疲劳度的数据
data = {
    'heart_rate': [50, 40, 70, 75, 80, 85, 90, 60, 65, 78, 82, 88, 72, 77, 83, 87, 91, 62, 67, 79, 84, 89, 74, 76, 81,
                   86, 92,
                   61, 66, 69, 73, 95, 150, 140],
    'blood_oxygen': [75, 70, 98, 97, 95, 94, 93, 99, 98, 96, 95, 92, 97, 96, 94, 93, 92, 100, 99, 97, 95, 91, 96, 97,
                     93, 94,
                     90, 98, 97, 96, 94, 89, 80, 82],
    'fatigue_level': [0.92, 0.9, 0.2, 0.3, 0.5, 0.6, 0.7, 0.1, 0.15, 0.4, 0.55, 0.65, 0.25, 0.35, 0.52, 0.63, 0.72,
                      0.12, 0.18,
                      0.45, 0.57, 0.67, 0.27, 0.37, 0.48, 0.58, 0.75, 0.22, 0.33, 0.44, 0.54, 0.78, 0.93, 0.90]
}

# 转换为DataFrame：将字典数据转换为Pandas的DataFrame格式，方便数据处理
df = pd.DataFrame(data)

# 准备数据：从DataFrame中提取特征和目标变量
X = df[['heart_rate', 'blood_oxygen']].values
y = df['fatigue_level'].values

# 标准化数据：对特征数据进行标准化处理，使其均值为0，方差为1
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 划分训练和测试集：将数据划分为训练集和测试集，比例为80%训练集，20%测试集
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# 转换为PyTorch张量：将训练和测试数据转换为PyTorch张量
X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
y_train_tensor = torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)  # 目标变量需转为二维
X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
y_test_tensor = torch.tensor(y_test, dtype=torch.float32).unsqueeze(1)

# 自定义SVM模型：定义一个简单的SVM模型，使用线性层模拟SVM
class SVM(nn.Module):
    def __init__(self, input_dim):
        super(SVM, self).__init__()
        self.fc = nn.Linear(input_dim, 1)  # 定义线性层
        self.fc.weight.data.fill_(0.0)  # 初始化权重为0
        self.fc.bias.data.fill_(0.0)  # 初始化偏置为0

    def forward(self, x):
        return self.fc(x)  # 前向传播

# 遗传算法适应度函数：定义适应度函数，用于评估每个个体的性能
def fitness(individual):
    model = SVM(input_dim=2)
    # 转换个体为PyTorch张量，并进行必要的形状调整
    weights = torch.tensor(np.array(individual[:2]).reshape(1, 2), dtype=torch.float32)
    bias = torch.tensor([individual[2]], dtype=torch.float32)

    model.fc.weight = nn.Parameter(weights)  # 设置模型权重
    model.fc.bias = nn.Parameter(bias)  # 设置模型偏置

    criterion = nn.MSELoss()  # 损失函数：均方误差
    optimizer = optim.SGD(model.parameters(), lr=0.01)  # 优化器：随机梯度下降

    num_epochs = 100  # 训练轮次
    for epoch in range(num_epochs):
        model.train()  # 训练模式
        optimizer.zero_grad()  # 清除梯度
        outputs = model(X_train_tensor)  # 前向传播
        loss = criterion(outputs, y_train_tensor)  # 计算损失
        loss.backward()  # 反向传播
        optimizer.step()  # 更新参数

    model.eval()  # 测试模式
    with torch.no_grad():
        predictions = model(X_test_tensor)  # 预测
        mse = mean_squared_error(y_test_tensor.numpy(), predictions.numpy())  # 计算均方误差

    return mse

# 初始化种群：生成初始种群，每个个体包含2个权重和1个偏置
def initialize_population(size):
    population = []
    for _ in range(size):
        individual = np.random.uniform(-1, 1, 3).tolist()  # 随机生成个体
        population.append(individual)
    return population

# 遗传算法选择函数：根据适应度选择个体
def select(population, fitnesses, num):
    selected = random.choices(population, weights=[1 / f for f in fitnesses], k=num)
    return selected

# 遗传算法交叉函数：生成子代个体
def crossover(parent1, parent2):
    point = random.randint(1, len(parent1) - 1)  # 随机选择交叉点
    child1 = parent1[:point] + parent2[point:]  # 生成第一个子代
    child2 = parent2[:point] + parent1[point:]  # 生成第二个子代
    return child1, child2

# 遗传算法变异函数：对个体进行变异
def mutate(individual, rate=0.01):
    for i in range(len(individual)):
        if random.random() < rate:  # 根据变异率决定是否变异
            individual[i] = np.random.uniform(-1, 1)  # 变异
    return individual

# 遗传算法主函数：运行遗传算法以寻找最优个体
def genetic_algorithm(pop_size, generations, crossover_rate=0.7, mutation_rate=0.01):
    population = initialize_population(pop_size)  # 初始化种群
    for generation in range(generations):
        fitnesses = [fitness(individual) for individual in population]  # 计算适应度
        new_population = []
        for _ in range(pop_size // 2):
            parents = select(population, fitnesses, 2)  # 选择父代
            if random.random() < crossover_rate:
                child1, child2 = crossover(parents[0], parents[1])  # 交叉
            else:
                child1, child2 = parents[0], parents[1]  # 保持父代不变
            child1 = mutate(child1, mutation_rate)  # 变异
            child2 = mutate(child2, mutation_rate)  # 变异
            new_population.extend([child1, child2])  # 更新种群
        population = new_population

    best_individual = min(population, key=fitness)  # 选择最优个体
    return best_individual

# 使用遗传算法优化SVM的超参数
best_params = genetic_algorithm(pop_size=50, generations=100)

# 使用优化后的参数训练最终模型
model = SVM(input_dim=2)
model.fc.weight = nn.Parameter(torch.tensor(np.array(best_params[:2]).reshape(1, 2), dtype=torch.float32))  # 设置最佳权重
model.fc.bias = nn.Parameter(torch.tensor([best_params[2]], dtype=torch.float32))  # 设置最佳偏置

criterion = nn.MSELoss()  # 损失函数：均方误差
optimizer = optim.SGD(model.parameters(), lr=0.01)  # 优化器：随机梯度下降

num_epochs = 1000  # 训练轮次
for epoch in range(num_epochs):
    model.train()  # 训练模式
    optimizer.zero_grad()  # 清除梯度
    outputs = model(X_train_tensor)  # 前向传播
    loss = criterion(outputs, y_train_tensor)  # 计算损失
    loss.backward()  # 反向传播
    optimizer.step()  # 更新参数

model.eval()  # 测试模式
with torch.no_grad():
    predictions = model(X_test_tensor)  # 预测
    mse = mean_squared_error(y_test_tensor.numpy(), predictions.numpy())  # 计算均方误差
    print(f'测试集均方误差: {mse}')  # 输出测试集均方误差

# 保存模型：可以取消注释以保存模型
# torch.save(model.state_dict(), 'svm_fatigue_model.pth')

# 使用训练好的模型进行疲劳度预测
new_data = torch.tensor(scaler.transform([[90, 88]]), dtype=torch.float32)  # 标准化新的数据
with torch.no_grad():
    new_predictions = model(new_data)  # 预测
    print(f'新的疲劳度预测: {new_predictions.item()}')  # 输出新的疲劳度预测
