#!/bin/bash

# 1. 定义测试的负载 (选择两个最敏感的 Web 负载)
TRACES=("nodeapp-nodeapp" "mwnginxfpm-wiki")

# 2. 定义新编译的变体
#VARIANTS=("short" "medium" "extralong")
VARIANTS=("short" "medium")

# 3. 设置路径
OUT_DIR="./results/sensitivity"
mkdir -p $OUT_DIR

# 4. 设置模拟参数 (建议与基准保持一致: 50M 预热, 100M ROI)
WARM=50000000
SIM=100000000

echo "开始敏感性测试..."

for trace in "${TRACES[@]}"; do
    for var in "${VARIANTS[@]}"; do
        BINARY="./build/predictor_$var"
        OUTPUT="$OUT_DIR/${trace}_${var}.txt"
        
        if [ -f "$BINARY" ]; then
            echo "------------------------------------------------"
            echo "正在运行: $trace | 版本: $var"
            echo "二进制文件: $BINARY"
            
            # 执行模拟
            $BINARY ./traces/${trace}.champsim.trace.gz \
                --model llbp \
                -w $WARM -n $SIM \
                > "$OUTPUT" 2>&1
                
            echo "完成，结果已保存至: $OUTPUT"
        else
            echo "错误: 找不到二进制文件 $BINARY，请检查编译和重命名是否成功。"
        fi
    done
done

echo "------------------------------------------------"
echo "所有新变体运行完毕！"