import os
import re
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# 1. 路径与配置设置
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

# 包含所有 5 个对比模型
MODELS = ["tage64kscl", "tage512kscl", "llbp", "llbp-timing"]
PENALTY = 20  # 误预测惩罚周期

def extract_ipc(file_path):
    """从日志提取数据并计算 IPC"""
    if not os.path.exists(file_path): 
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 提取核心计数器：指令数、误预测数、运行周期
            instr = re.search(r"ROI INSTRUCTIONS\s*:\s*(\d+)", content)
            misp = re.search(r"ROI MISPREDICTIONS\s*:\s*(\d+)", content)
            ticks = re.search(r"Ticks:(\d+)", content)
            
            if instr and misp and ticks:
                i = float(instr.group(1))
                m = float(misp.group(1))
                t = float(ticks.group(1))
                # 修正后的 IPC 计算公式：总指令 / (无阻塞周期 + 误预测总罚时)
                # 这种计算方式能直观体现分支预测器改进对系统性能的最终贡献
                return i / (t + (m * PENALTY))
    except Exception as e:
        print(f"解析 {file_path} 出错: {e}")
    return None

# 2. 提取并整合数据
data = []
for trace in TRACES:
    row = {'Trace': trace}
    for model in MODELS:
        # 路径拼接：results / trace_name / model_name-ae.txt
        file_path = os.path.join(RESULTS_DIR, trace, f"{model}-ae.txt")
        ipc = extract_ipc(file_path)
        row[model] = ipc if ipc else 0
    data.append(row)

df = pd.DataFrame(data)

# 3. 绘图设置
plt.style.use('seaborn-v0_8-whitegrid')
# 增加画布宽度以容纳 14 个 Trace 的 5 柱状图
fig, ax = plt.subplots(figsize=(24, 8))

x = np.arange(len(TRACES))
width = 0.15  # 5 个柱子

# 颜色定义：基准模型灰色系，核心创新模型彩色
colors = ['#adb5bd', '#6c757d', '#1f77b4', '#d62728']
labels = ['TAGE-64K-SCL', 'TAGE-512K-SCL', 'LLBP (Ideal)', 'LLBP (Timing)']

# 4. 循环绘制柱状图
for i, model in enumerate(MODELS):
    offset = (i - 2) * width
    bars = ax.bar(x + offset, df[model], width, label=labels[i], 
                  color=colors[i], edgecolor='black', linewidth=0.6)
    
    # 标注数值：为了整洁，数值较小时使用垂直旋转
    for bar in bars:
        h = bar.get_height()
        if h > 0:
            ax.annotate(f'{h:.2f}',
                        xy=(bar.get_x() + bar.get_width() / 2, h),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=12, rotation=45)

# 5. 图表修饰
ax.set_ylabel('Instructions Per Cycle (IPC)', fontsize=18, fontweight='bold')
ax.set_title(f'Performance Comparison (IPC)', fontsize=18)
ax.set_xticks(x)
ax.set_xticklabels(TRACES, fontsize=18, rotation=30, ha='right')

# 将图例置于上方并横向排列
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=5, frameon=True, shadow=True)

# 自动留出顶部空间以便显示数值标注
if not df.empty:
    max_val = df[MODELS].max().max()
    ax.set_ylim(0, max_val * 1.3)

plt.tight_layout()
save_path = os.path.join(SAVE_DIR, 'ipc_comparison.png')
plt.savefig(save_path, dpi=300, bbox_inches='tight')
print(f"\n✅ 全量 IPC 对比图已保存至: {save_path}")
plt.show()