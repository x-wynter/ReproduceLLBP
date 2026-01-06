import os
import re
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# 1. 路径与保存设置
RESULTS_DIR = "./results"  # 根目录包含子文件夹
SAVE_DIR = "./results/images"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# 包含所有 14 个 Trace
TRACES = [
    "nodeapp-nodeapp", "mwnginxfpm-wiki", "benchbase-tpcc", "whiskey.426708",
    "benchbase-twitter", "benchbase-wikipedia", "charlie.1006518", "dacapo-kafka",
    "dacapo-spring", "dacapo-tomcat", "delta.507252", "merced.467915",
    "renaissance-finagle-chirper", "renaissance-finagle-http"
]

MODELS = ["llbp-timing", "llbp", "tage512kscl"]
BASELINE_MODEL = "tage64kscl"
PENALTY = 20

def extract_raw_data(file_path):
    """从日志中提取原始计数器"""
    if not os.path.exists(file_path): 
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            instr = re.search(r"ROI INSTRUCTIONS\s*:\s*(\d+)", content)
            misp = re.search(r"ROI MISPREDICTIONS\s*:\s*(\d+)", content)
            ticks = re.search(r"Ticks:(\d+)", content)
            
            if instr and misp and ticks:
                return {
                    'instr': float(instr.group(1)),
                    'misp': float(misp.group(1)),
                    'ticks': float(ticks.group(1))
                }
    except:
        return None
    return None

def calc_ipc(stats, use_perfect=False):
    """计算 IPC，perfect=True 则不计误预测罚时"""
    if stats is None: return 0
    if use_perfect:
        return stats['instr'] / stats['ticks']
    else:
        adjusted_cycles = stats['ticks'] + (stats['misp'] * PENALTY)
        return stats['instr'] / adjusted_cycles

# 1. 提取数据并计算 Speedup
data = []
for trace in TRACES:
    # 路径拼接逻辑更新
    base_file = os.path.join(RESULTS_DIR, trace, f"{BASELINE_MODEL}-ae.txt")
    base_stats = extract_raw_data(base_file)
    base_ipc = calc_ipc(base_stats)
    
    row = {'Trace': trace}
    for model in MODELS:
        target_file = os.path.join(RESULTS_DIR, trace, f"{model}-ae.txt")
        target_stats = extract_raw_data(target_file)
        target_ipc = calc_ipc(target_stats)
        row[model] = target_ipc / base_ipc if base_ipc > 0 else 1.0
    
    # Perfect BP 计算
    perfect_ipc = calc_ipc(base_stats, use_perfect=True)
    row['perfect'] = perfect_ipc / base_ipc if base_ipc > 0 else 1.0
    data.append(row)

df = pd.DataFrame(data)

# 2. 绘图设置
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(22, 8)) # 增大宽度以容纳 14 个 Trace

x = np.arange(len(TRACES))
plot_models = ["llbp-timing", "llbp", "tage512kscl", "perfect"]
labels = ['LLBP(Timing)', 'LLBP(Ideal)', 'TAGE-512K-TSL', 'Perfect BP']
colors = ['#0a2f1f', '#3d6161', '#c9dadd', '#ffffff'] 

width = 0.2 
Y_LIMIT = 2 # 保持 1.6 的上限以展示高瓶颈负载

# 3. 绘制柱状图
for i, model in enumerate(plot_models):
    offset = (i - 1.5) * width
    e_color = 'black' if model != "perfect" else '#999999'
    l_width = 0.8 if model != "perfect" else 0.5
    
    bars = ax.bar(x + offset, df[model], width, label=labels[i], 
                  color=colors[i], edgecolor=e_color, linewidth=l_width)

    # 4. 数值标注 (针对 Perfect BP)
    if model == "perfect":
        for j, val in enumerate(df['perfect']):
            if val > Y_LIMIT:
                ax.text(j + offset, Y_LIMIT - 0.005, f'↑{val:.2f}', 
                        ha='center', va='top', color='red', fontsize=12, fontweight='bold')

# 5. 纵坐标设置
ax.set_ylim(1.0, Y_LIMIT)
ax.set_yticks(np.arange(1.0, Y_LIMIT + 0.01, 0.1))

# 6. 图表修饰
ax.set_ylabel('Speedup', fontsize=18, fontweight='bold')
ax.set_title('Estimated IPC Speedup Comparison', fontsize=18)
ax.set_xticks(x)
ax.set_xticklabels(TRACES, fontsize=18, rotation=30, ha='right')

# 基准线
ax.axhline(1.0, color='black', linewidth=1)

# 图例放置在上方
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12), ncol=4, frameon=True, shadow=True)

# 辅助网格
ax.yaxis.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
save_path = os.path.join(SAVE_DIR, 'ipc_speedup.png')
plt.savefig(save_path, dpi=300)
print(f"\n✅ 加速比对比图已保存至: {save_path}")
plt.show()