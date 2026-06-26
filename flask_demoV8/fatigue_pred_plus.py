import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.mobile_optimizer import optimize_for_mobile
import random

# 数据
data = {
    'heart_rate': [50,40,70, 75, 80, 85, 90, 60, 65, 78, 82, 88, 72, 77, 83, 87, 91, 62, 67, 79, 84, 89, 74, 76, 81, 86, 92,
                   61, 66, 69, 73, 95,150,140],
    'blood_oxygen': [75,70,98, 97, 95, 94, 93, 99, 98, 96, 95, 92, 97, 96, 94, 93, 92, 100, 99, 97, 95, 91, 96, 97, 93, 94,
                     90, 98, 97, 96, 94, 89,80,82],
    'fatigue_level': [0.92,0.9,0.2, 0.3, 0.5, 0.6, 0.7, 0.1, 0.15, 0.4, 0.55, 0.65, 0.25, 0.35, 0.52, 0.63, 0.72, 0.12, 0.18,
                      0.45, 0.57, 0.67, 0.27, 0.37, 0.48, 0.58, 0.75, 0.22, 0.33, 0.44, 0.54, 0.78,0.93,0.90]
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


# 适应度函数
def fitness(individual):
    model = NeuralNet()
    model.fc1.weight = nn.Parameter(torch.tensor(individual[:20]).reshape(10, 2))
    model.fc1.bias = nn.Parameter(torch.tensor(individual[20:30]))
    model.fc2.weight = nn.Parameter(torch.tensor(individual[30:40]).reshape(1, 10))
    model.fc2.bias = nn.Parameter(torch.tensor(individual[40:]))

    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01)

    num_epochs = 500
    for epoch in range(num_epochs):
        model.train()
        optimizer.zero_grad()
        outputs = model(X_train_tensor)
        loss = criterion(outputs.squeeze(), y_train_tensor)
        loss.backward()
        optimizer.step()

    model.eval()
    with torch.no_grad():
        predictions = model(X_test_tensor).squeeze()
        mse = mean_squared_error(y_test, predictions.numpy())

    return mse


# 初始化种群
def initialize_population(size):
    population = []
    for _ in range(size):
        individual = np.random.uniform(-1, 1, 41).tolist()
        population.append(individual)
    return population


# 选择
def select(population, fitnesses, num):
    selected = random.choices(population, weights=[1 / f for f in fitnesses], k=num)
    return selected


# 交叉
def crossover(parent1, parent2):
    point = random.randint(1, len(parent1) - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2


# 变异
def mutate(individual, rate=0.01):
    for i in range(len(individual)):
        if random.random() < rate:
            individual[i] = np.random.uniform(-1, 1)
    return individual


# 遗传算法
def genetic_algorithm(pop_size, generations, crossover_rate=0.7, mutation_rate=0.01):
    population = initialize_population(pop_size)
    for generation in range(generations):
        fitnesses = [fitness(individual) for individual in population]
        new_population = []
        for _ in range(pop_size // 2):
            parents = select(population, fitnesses, 2)
            if random.random() < crossover_rate:
                child1, child2 = crossover(parents[0], parents[1])
            else:
                child1, child2 = parents[0], parents[1]
            child1 = mutate(child1, mutation_rate)
            child2 = mutate(child2, mutation_rate)
            new_population.extend([child1, child2])
        population = new_population

    best_individual = min(population, key=fitness)
    return best_individual


# 参数优化
best_params = genetic_algorithm(pop_size=50, generations=100)

# 使用优化后的参数训练最终模型
model = NeuralNet()
model.fc1.weight = nn.Parameter(torch.tensor(best_params[:20]).reshape(10, 2))
model.fc1.bias = nn.Parameter(torch.tensor(best_params[20:30]))
model.fc2.weight = nn.Parameter(torch.tensor(best_params[30:40]).reshape(1, 10))
model.fc2.bias = nn.Parameter(torch.tensor(best_params[40:]))

criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

num_epochs = 1000
for epoch in range(num_epochs):
    model.train()
    optimizer.zero_grad()
    outputs = model(X_train_tensor)
    loss = criterion(outputs.squeeze(), y_train_tensor)
    loss.backward()
    optimizer.step()

model.eval()
torch.save(model.state_dict(), 'fatigue_model.pth')
with torch.no_grad():
    predictions = model(X_test_tensor).squeeze()
    mse = mean_squared_error(y_test, predictions.numpy())
    print(f'均方误差: {mse}')

# 使用训练好的模型进行疲劳度预测
new_data = torch.tensor([[90, 88]], dtype=torch.float32)  # 新的心率和血氧数据
new_predictions = model(new_data)
print(f'新的疲劳度预测: {new_predictions.item()}')

# 转换为TorchScript
example_input = torch.tensor(X_test, dtype=torch.float32)
traced_model = torch.jit.trace(model, example_input)



