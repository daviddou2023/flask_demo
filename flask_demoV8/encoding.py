import math
import matplotlib.pyplot as plt
from heapq import heappop, heappush


# Shannon 编码
def shannon_encoding(probabilities):
    codes = []
    cumulative_prob = 0
    for p in probabilities:
        if p > 0:
            code_length = math.ceil(-math.log2(p))
            cumulative_prob += p
            code = f"{int(cumulative_prob * (2 ** code_length)):#0{code_length + 1}b}"[2:]
            codes.append(code)
        else:
            raise ValueError("Probability must be greater than 0.")
    return codes


# Fano 编码
def fano_encoding(symbols, probabilities):
    def fano_recursive(symbols, probs, code=""):
        if len(symbols) == 1:
            return {symbols[0]: code}
        # 找到分割点，使得概率尽可能均等
        total_prob = sum(probs)
        split_idx = 0
        accum_prob = 0
        for i, p in enumerate(probs):
            accum_prob += p
            if accum_prob >= total_prob / 2:
                split_idx = i + 1
                break
        # 左右递归
        left_codes = fano_recursive(symbols[:split_idx], probs[:split_idx], code + "0")
        right_codes = fano_recursive(symbols[split_idx:], probs[split_idx:], code + "1")
        return {**left_codes, **right_codes}

    sorted_symbols_probs = sorted(zip(symbols, probabilities), key=lambda x: x[1], reverse=True)
    symbols, probs = zip(*sorted_symbols_probs)
    return fano_recursive(symbols, probs)


# Huffman 编码
def huffman_encoding(symbols, probabilities):
    heap = [[weight, [symbol, ""]] for symbol, weight in zip(symbols, probabilities)]
    while len(heap) > 1:
        low1 = heappop(heap)
        low2 = heappop(heap)
        for pair in low1[1:]:
            pair[1] = "0" + pair[1]
        for pair in low2[1:]:
            pair[1] = "1" + pair[1]
        heappush(heap, [low1[0] + low2[0]] + low1[1:] + low2[1:])
    return dict(sorted(heappop(heap)[1:], key=lambda p: symbols.index(p[0])))


# 计算平均码长
def calculate_average_length(codes, probabilities):
    return sum(len(code) * prob for code, prob in zip(codes, probabilities))


# 示例概率和符号
symbols = ['s1', 's2', 's3', 's4']
probabilities = [0.5, 0.25, 0.125, 0.125]

# Shannon 编码
shannon_codes = shannon_encoding(probabilities)
shannon_avg_length = calculate_average_length(shannon_codes, probabilities)

# Fano 编码
fano_codes = fano_encoding(symbols, probabilities)
fano_avg_length = calculate_average_length([fano_codes[symbol] for symbol in symbols], probabilities)

# Huffman 编码
huffman_codes = huffman_encoding(symbols, probabilities)
huffman_avg_length = calculate_average_length([huffman_codes[symbol] for symbol in symbols], probabilities)

# 输出编码结果
print("Shannon Codes:", shannon_codes)
print("Fano Codes:", fano_codes)
print("Huffman Codes:", huffman_codes)
print("\nAverage Code Lengths:")
print("Shannon Average Length:", shannon_avg_length)
print("Fano Average Length:", fano_avg_length)
print("Huffman Average Length:", huffman_avg_length)

# 绘制平均码长对比图
encoding_methods = ['Shannon', 'Fano', 'Huffman']
average_lengths = [shannon_avg_length, fano_avg_length, huffman_avg_length]

plt.bar(encoding_methods, average_lengths, color=['blue', 'orange', 'green'])
plt.xlabel('Encoding Methods')
plt.ylabel('Average Code Length')
plt.title('Average Code Length Comparison')
plt.show()
