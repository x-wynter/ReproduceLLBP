#!/bin/bash
TRACE_DIR="./traces"
mkdir -p $TRACE_DIR

# 定义挑选的核心 trace
CORE_TRACES=(
    "nodeapp-nodeapp"
    "mwnginxfpm-wiki"
    "benchbase-tpcc"
    "whiskey.426708"
)

for fn in "${CORE_TRACES[@]}"; do
    echo "正在下载: $fn ..."
    # -c 参数支持断点续传，防止下载失败重来
    wget -c -O $TRACE_DIR/$fn.champsim.trace.gz "https://zenodo.org/records/13133243/files/$fn.champsim.trace.gz?download=1"
done

echo "核心 Trace 下载完成！"