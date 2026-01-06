import os
import re
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# 路径设置 - 这里的 RESULTS_DIR 指向包含各个 trace 文件夹的根目录
RESULTS_DIR = "./results"
SAVE_DIR = "./results/images"

# 自动创建保存目录
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# 包含所有测试结果中出现的 Trace
TRACES = [
    "nodeapp-nodeapp", "mwnginxfpm-wiki", "benchbase-tpcc", "whiskey.426708",
    "benchbase-twitter", "benchbase-wikipedia", "charlie.1006518", "dacapo-kafka",
    "dacapo-spring", "dacapo-tomcat", "delta.507252", "merced.467915",
    "renaissance-finagle-chirper", "renaissance-finagle-http"
]

# 模型列表保持不变
MODELS = ["llbp-timing", "llbp", "tage512kscl"]
BASELINE_MODEL = "tage64kscl"

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

# 1. 提取原始数据
data = []
for trace in TRACES:
    # 修改路径拼接逻辑：RESULTS_DIR / trace_name / model_name-ae.txt
    base_file = os.path.join(RESULTS_DIR, trace, f"{BASELINE_MODEL}-ae.txt")
    base_mpki = extract_mpki(base_file)
    
    row = {'Trace': trace}
    for model in MODELS:
        target_file = os.path.join(RESULTS_DIR, trace, f"{model}-ae.txt")
        target_mpki = extract_mpki(target_file)
        
        if base_mpki is not None and target_mpki is not None:
            # 计算减少百分比
            reduction = (1 - (target_mpki / base_mpki)) * 100
            row[model] = reduction
        else:
            row[model] = 0
    data.append(row)

df = pd.DataFrame(data)

# 2. 绘图设置
plt.style.use('seaborn-v0_8-whitegrid')
# 增加画布宽度以容纳更多 Trace
fig, ax = plt.subplots(figsize=(20, 7))

x = np.arange(len(TRACES))
width = 0.25 

# 定义颜色与标签
colors = ['#0a2f1f', '#3d6161', '#c9dadd']
labels = ['LLBP(Timing)', 'LLBP(Ideal)', 'TAGE-512K-TSL']
plot_models = ["llbp-timing", "llbp", "tage512kscl"]

# 3. 循环绘制每一组柱子
for i, model in enumerate(plot_models):
    offset = (i - 1) * width
    bars = ax.bar(x + offset, df[model], width, label=labels[i], 
                  color=colors[i], edgecolor='black', linewidth=0.8)
    
    # 在柱子上方标注百分比数值
    for bar in bars:
        height = bar.get_height()
        if height != 0:
            ax.annotate(f'{height:.1f}%',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=12, rotation=45)

# 4. 纵坐标
ax.set_ylim(0, 60.0)                
ax.set_yticks(np.arange(0, 61, 10)) 

# 5. 图表修饰
ax.set_ylabel('Branch MPKI Reduction [%]', fontsize=18, fontweight='bold')
ax.set_title('Branch Misprediction Reduction over 64K TSL', fontsize=18)
ax.set_xticks(x)
# 旋转标签以防重叠
ax.set_xticklabels(TRACES, fontsize=18, rotation=30, ha='right')

# 图例放在上方，防止遮挡柱子
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), frameon=True, shadow=True, ncol=3)

plt.tight_layout()
save_path = os.path.join(SAVE_DIR, 'MPKI_reduction.png')
plt.savefig(save_path, dpi=300)
print(f"\n✅ 减少百分比对比图已保存为:{save_path}")
plt.show()