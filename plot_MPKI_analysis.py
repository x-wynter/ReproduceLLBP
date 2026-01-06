import os
import re
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# 1. 路径设置 - 指向包含子文件夹的根目录
RESULTS_DIR = "./results"
SAVE_DIR = "./results/images"

# 自动创建保存目录
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# 包含所有测试结果中出现的 14 个 Trace
TRACES = [
    "nodeapp-nodeapp", "mwnginxfpm-wiki", "benchbase-tpcc", "whiskey.426708",
    "benchbase-twitter", "benchbase-wikipedia", "charlie.1006518", "dacapo-kafka",
    "dacapo-spring", "dacapo-tomcat", "delta.507252", "merced.467915",
    "renaissance-finagle-chirper", "renaissance-finagle-http"
]

# 模型列表
MODELS = ["tage64kscl", "tage512kscl", "llbp", "llbp-timing"]

def extract_mpki(file_path):
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r"ROI MPKI\s*:\s*([\d\.]+)", content)
            if match:
                return float(match.group(1))
    except Exception as e:
        print(f"解析 {file_path} 出错: {e}")
    return None

# 1. 提取并整合数据
data = []
for trace in TRACES:
    row = {'Trace': trace}
    for model in MODELS:
        # 修改路径拼接逻辑：RESULTS_DIR / trace_name / model_name-ae.txt
        file_path = os.path.join(RESULTS_DIR, trace, f"{model}-ae.txt")
        mpki = extract_mpki(file_path)
        row[model] = mpki
    data.append(row)

df = pd.DataFrame(data)

# 打印表格以便核对数据完整性
print("\n--- 5个模型 MPKI 提取结果 ---")
print(df.to_string(index=False))

# 2. 绘图设置
plt.style.use('seaborn-v0_8-whitegrid')
# 增加画布宽度以容纳 14 个负载
fig, ax = plt.subplots(figsize=(22, 8))

x = np.arange(len(TRACES))
width = 0.15 

# 定义颜色和标签
colors = ['#bdc3c7', '#95a5a6', '#7f8c8d', '#3498db', '#e74c3c']
labels = [ 'TAGE-64K-SCL', 'TAGE-512K-SCL', 'LLBP(Ideal)', 'LLBP(Timing)']

# 3. 循环绘制每一组柱子
for i, model in enumerate(MODELS):
    offset = (i - len(MODELS)/2 + 0.5) * width
    bars = ax.bar(x + offset, df[model], width, label=labels[i], color=colors[i], edgecolor='black', linewidth=0.6)
    
    # 添加数值标注
    for bar in bars:
        height = bar.get_height()
        if not np.isnan(height) and height > 0:
            ax.annotate(f'{height:.2f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=12, rotation=45)

# 4. 图表修饰
ax.set_ylabel('ROI MPKI (Lower is Better)', fontsize=18, fontweight='bold')
ax.set_title('Branch Predictor MPKI Comparison', fontsize=18)
ax.set_xticks(x)
# 旋转标签以防文字重叠
ax.set_xticklabels(TRACES, fontsize=18, rotation=30, ha='right')

# 强制设置纵坐标起始为 0
ax.set_ylim(0, df[MODELS].max().max() * 1.2)

# 图例放置在上方
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12), ncol=5, frameon=True, shadow=True)
ax.grid(axis='y', linestyle='--', alpha=0.6)

plt.tight_layout()
save_path = os.path.join(SAVE_DIR, 'MPKI_comparison.png')
plt.savefig(save_path, dpi=300)
print(f"\n✅ 完整对比图已保存为: {save_path}")
plt.show()