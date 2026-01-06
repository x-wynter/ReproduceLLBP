#!/bin/bash
TRACES=("nodeapp-nodeapp" "mwnginxfpm-wiki" "benchbase-tpcc" "whiskey.426708")
MODELS=("tage64k" "tage64kscl" "tage512kscl" "llbp" "llbp-timing")
#MODELS=("llbp" "tage64kscl")
#MODELS=("tage64k" "tage512kscl" "llbp-timing")
OUT_DIR="./results/core_eval"
WARM=50000000   # 50M 预热
SIM=100000000   # 100M 模拟

mkdir -p $OUT_DIR

for trace_name in "${TRACES[@]}"; do
    for model in "${MODELS[@]}"; do
        echo "Running $model on $trace_name..."
        ./build/predictor ./traces/${trace_name}.champsim.trace.gz \
            --model $model \
            -w $WARM -n $SIM \
            --output "$OUT_DIR/${trace_name}_${model}" \
            > "$OUT_DIR/${trace_name}_${model}.txt" 2>&1
    done
done