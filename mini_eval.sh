#!/bin/bash

# 设置基础变量
TRACE="./traces/nodeapp-nodeapp-small.champsim.trace.gz"
MODELS=("llbp" "llbp-timing" "tage64kscl" "tage512kscl")
OUT_DIR="./results/mini_eval"
WARM=1000000     # 1M 预热
SIM=10000000     # 10M 模拟

# 检查 Trace 文件是否存在
if [ ! -f "$TRACE" ]; then
    echo "错误: 找不到文件 $TRACE"
    exit 1
fi

mkdir -p $OUT_DIR

echo "开始对比实验..."
echo "Trace: $TRACE"
echo "------------------------------------"

for model in "${MODELS[@]}"; do
    echo "正在运行模型: $model ..."
    
    # 执行模拟并将日志保存到 .txt 文件，同时在控制台显示进度
    ./build/predictor -i "$TRACE" \
        --model "$model" \
        -w $WARM -n $SIM \
        --output "$OUT_DIR/$model" \
        > "$OUT_DIR/$model.txt" 2>&1

    # 从生成的日志中提取关键的 MPKI 数据并显示
    mpki=$(grep "ROI MPKI" "$OUT_DIR/$model.txt" | awk '{print $4}')
    echo "完成! ROI MPKI: $mpki"
    echo "------------------------------------"
done

echo "实验结束。详细日志查看: $OUT_DIR"

# 自动生成一个简单的汇总表
echo -e "\n模型汇总报告 (MPKI):"
echo "--------------------------"
printf "%-15s | %-10s\n" "Model" "MPKI"
echo "--------------------------"
for model in "${MODELS[@]}"; do
    mpki=$(grep "ROI MPKI" "$OUT_DIR/$model.txt" | awk '{print $4}')
    printf "%-15s | %-10s\n" "$model" "$mpki"
done
echo "--------------------------"