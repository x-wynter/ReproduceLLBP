import os
import re
import matplotlib.pyplot as plt
import numpy as np

# 数据路径配置
SENSITIVITY_DIR = "./results/sensitivity"
BASELINE_DIR = "./results/core_eval"
SAVE_DIR = "./results/images"
TRACES = ["nodeapp-nodeapp", "mwnginxfpm-wiki"]

# 定义 X 轴坐标 (Contexts 数量) 和对应的模型名称
DATA_CONFIG = [
    {"name": "short",     "label": "4K",  "val": 4096,  "dir": SENSITIVITY_DIR},
    {"name": "medium",    "label": "8K",  "val": 8192,  "dir": SENSITIVITY_DIR},
    {"name": "baseline",  "label": "14K(Default)", "val": 14336, "dir": BASELINE_DIR},
    {"name": "extralong", "label": "28K", "val": 28672, "dir": SENSITIVITY_DIR}
]

def extract_mpki(file_path):
    if not os.path.exists(file_path):
        print(f"警告: 找不到文件 {file_path}")
        return None
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            match = re.search(r"ROI MPKI\s*:\s*([\d\.]+)", content)
            if match:
                return float(match.group(1))
    except Exception:
        pass
    return None

# 开始绘图
plt.figure(figsize=(10, 6))

for trace in TRACES:
    x_vals = []
    y_vals = []
    labels = []
    
    for cfg in DATA_CONFIG:
        # 特殊处理 baseline 的文件名格式
        if cfg['name'] == "baseline":
            file_path = os.path.join(cfg['dir'], f"{trace}_llbp.txt")
        else:
            file_path = os.path.join(cfg['dir'], f"{trace}_{cfg['name']}.txt")
            
        mpki = extract_mpki(file_path)
        
        if mpki is not None:
            x_vals.append(cfg['val'])
            y_vals.append(mpki)
            labels.append(cfg['label'])
    
    # 绘制折线
    plt.plot(x_vals, y_vals, marker='o', markersize=8, linewidth=2, label=f"Trace: {trace}")
    
    # 在点旁边标注具体的 MPKI 数值
    for x, y in zip(x_vals, y_vals):
        plt.text(x, y, f' {y:.3f}', va='bottom', ha='left', fontsize=9)

# 设置 X 轴刻度为具体的 Context 数量
plt.xticks([cfg['val'] for cfg in DATA_CONFIG], [cfg['label'] for cfg in DATA_CONFIG])

plt.xlabel('LLBP Contexts Capacity (NumContexts)', fontsize=12)
plt.ylabel('ROI MPKI (Lower is Better)', fontsize=12)
plt.title('LLBP Scalability Analysis: MPKI vs. Context Storage', fontsize=14)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
save_path = os.path.join(SAVE_DIR, 'context_sensitivity.png')
plt.savefig(save_path, dpi=300)
print(f"\n✅ 已保存为: {save_path}")
plt.show()