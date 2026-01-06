# LLBP 实验复现 (Last-Level Branch Predictor)

本仓库包含了针对 MICRO 2024 论文 **"The Last-Level Branch Predictor"** 的实验复现过程及结果。本项目基于原作者提供的 LLBP 模拟器框架，在特定的实验环境下重新运行了所有基准测试（Benchmarks），并验证了 LLBP 在提升分支预测准确率方面的表现。

## 1. 实验环境说明

为了确保实验结果的可追溯性，以下是本次复现所使用的环境：

- **操作系统**：Ubuntu 22.04.2 LTS
- **编译器**：gcc 11.4.0
- **构建工具**：cmake 3.31.1
- **模拟器**：Champsim
- **Python 环境**：Python 3.10.12 (用于结果分析与绘图)

------

## 2. 快速开始

### 安装依赖

```bash
# Install cmake
sudo apt install -y cmake libboost-all-dev build-essential pip parallel

# Python dependencies for plotting.
pip install -r analysis/requirements.txt
```

### 获取实验数据

实验使用基于 gem5 生成的服务器负载 Trace（ChampSim 格式）。

这些trace数据用于评估在 gem5 上以全系统模式运行服务器应用程序所收集的 LLBP。磁盘镜像的操作系统为 Ubuntu 20.04，内核版本为 5.4.84。trace数据采用[ChampSim](https://github.com/ChampSim/ChampSim)格式，包含用户空间和内核空间指令。这些trace数据可在 Zenodo 上获取，地址为[10.5281/zenodo.13133242](https://doi.org/10.5281/zenodo.13133242)。

utils 文件夹中的脚本`download_traces.sh`将从 Zenodo 下载所有trace信息并将其存储到该`traces`目录中。

```bash
./utils/download_traces.sh
```

### 构建项目

```bash
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Debug ..
cd ..

cmake --build ./build -j 8
```

------

## 3. 运行分支预测模型

可以使用以下命令运行模拟器，其输入包括trace文件、分支预测模型、预热指令数和仿真指令数。本次复现涵盖了四种主要的分支预测器模型：`tage64kscl`, `tage512kscl`, `llbp`, 以及 `llbp-timing`。

> 分支预测模型的定义可以在`bpmodels/base_predictor.cc`文件中找到。

```bash
./build/predictor --model <predictor> -w <warmup instructions> -n <simulation instructions> <trace>
```

------

## 4. 附加测试实验：上下文长度敏感性分析

为了进一步探索 LLBP 的微架构特性，本次复现针对nodeapp-nodeapp、mwnginxfpm-wiki两个trace新增了关于**上下文长度**的对比实验。

### 实验操作

通过手动修改源文件 `bpmodels/llbp/llbp.h` 中的 `numContexts` 宏定义，我们重新编译并测试了不同上下文深度下的预测准确率。

- **修改位置**: `bpmodels/llbp/llbp.h`
- **测试变量**: `numContexts` (分别测试 4k, 8k, 14k, 28k 长度的上下文)。
- **实验目的**: 探究 RCR（递归调用寄存器）记录的调用链深度对模式预取命中率的影响。

### 运行步骤

1. 修改 numContexts 的值，重新编译

```bash
# 修改 llbp.h 的 numContexts 为 3584（4k），编译并存档
cmake --build ./build -j$(nproc)
mv ./build/predictor ./build/predictor_short

# 修改 llbp.h 的 numContexts 为 7168（8k），编译并存档
cmake --build ./build -j$(nproc)
mv ./build/predictor ./build/predictor_medium

# 修改 llbp.h 的 numContexts 为 1024*28（28k），编译并存档
cmake --build ./build -j$(nproc)
mv ./build/predictor ./build/predictor_extralong
```

2. 运行脚本 run_sensitivity.sh

```bash
./run_sensitivity.sh
```

运行完成后，会在 results/sensitivity 目录下生成对应的结果文件

## 5. 复现结果展示

### 分支预测准确率 (MPKI)

通过运行 `analysis/mpki.ipynb` 中的绘图脚本，我们得到了复现后的 MPKI 对比图（对应原论文 Figure 9）。

Jupyter notebook ( `./analysis/mpki.ipynb`) 可用于解析统计文件并绘制不同分支预测模型的分支 MPKI。

为了重现与论文中类似的图表（图 9），我们提供了一个单独的脚本（`./eval_all.sh`），该脚本运行所有评估的分支预测模型和基准的实验。

> *注：*由于我们在论文中将 LLBP 与 ChampSim 集成，因此结果可能与论文中给出的数字略有不同。

脚本可按如下方式运行：

```bash
./eval_all.sh
```

运行完成后，打开 Jupyter notebook 并点击运行所有单元格。

### 实验结果绘制脚本

运行脚本可查看实验结果图：

```bash
#绘制 TAGE 64K SCL、512K SCL、LLBP、LLBP-Timing 在不同trace下的MPKI对比图
./plot_MPKI_analysis.py

#绘制 TAGE 64K SCL、512K SCL、LLBP、LLBP-Timing 在不同trace下的IPC对比图
./plot_ipc_analysis.py

#绘制 TAGE 512K SCL、LLBP、LLBP-Timing 在不同trace下的MPKI下降率(对比 64K SCL)。对比论文Fig 9
./plot_MPKI_reduction.py

#绘制 TAGE 512K SCL、LLBP、LLBP-Timing 在不同trace下的speedup(对比 64K SCL)。对比论文Fig 10
./plot_ipc_speedup.py

#绘制 LLBP 在不同上下文长度下MPKI的对比图
./plot_context_sensitivity.py
```

所有的实验结果图都保存在 results/images 目录下

### 结果分析

- **LLBP vs TAGE-64KB**: 在大多数服务器负载中，LLBP 显著降低了每千条指令的分支预测错误数（MPKI）。
- **容量优势**: LLBP 通过高容量存储结构，在性能上接近甚至在部分场景下超过了传统的 512KiB 大型 TAGE 预测器，同时保持了较低的访问延迟。
- **预取有效性**: `llbp-timing` 的结果验证了通过 RCR（Rolling Context Register）进行上下文预取的策略能有效掩盖高容量存储的访问延迟。

- **性能趋势**: 随着 `numContexts` 的增加，MPKI 在初期呈现下降趋势，这表明更长的调用链提供了更细粒度的程序上下文识别。
- **收益递减**: 当上下文长度超过 14k 后，准确率提升趋于平缓，且增加了 `PatternBuffer` 的查找开销。

------

## 6. 代码说明

- **其他：**
  - 该`main.cc`文件包含模拟器的主入口点。它读取trace文件，初始化分支预测模型，并运行模拟。
  - 该`bpmodel`目录包含 TAGE-SCL 和 LLBP 分支预测模型的实现。
  
- **TAGE：**
  - TAGE-SCL 由 TAGE 和 SCL 两个组件构成。代码取自 CBP5 框架，并经过修改，加入了额外的统计信息以评估分支预测器。
  - 512KiB TAGE-SCL 的唯一区别在于 TAGE 预测器中的条目数量增加了 8 倍。
  
- **LLBP：**
  
  - LLBP 继承自 TAGE-SCL 基类，并重写了几个方法来实现 LLBP 功能。
  - LLBP 有两个版本：`llbp`和`llbp-timing`。两者功能相同，但后者模拟模式集的预取，可用于研究延迟预取的影响。
  - 高容量的 LLBP 结构用于`LLBPStorage`存储所有模式集。而`PatternBuffer`小型快速结构则用于存储即将到来的上下文的模式。
  - 该类`RCR`实现了计算程序上下文的所有功能。

------

## 7. 结论

本次复现实验成功验证了 LLBP 论文中的核心主张。实验数据表明，LLBP 能够有效利用程序上下文来预取分支模式，打破了传统分支预测器在容量与延迟之间的权衡。

## 8. 致谢

本项目是对LLBP分支预测器的复现。原始框架及研究成果来源于David Schall (University of Edinburgh/Arm Ltd)。

- **原作者项目地址**: [dhschall/LLBP](https://github.com/dhschall/LLBP)
- **论文引用**: [10.1109/MICRO61859.2024.00042](https://doi.org/10.1109/MICRO61859.2024.00042)