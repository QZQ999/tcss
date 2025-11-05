# 半导体供应链实验系统 - 最终使用指南

## ✅ 系统状态

已成功创建并修复！所有组件已集成完毕，系统可以正常运行。

---

## 🎯 完成的工作

### 1. ✅ 网络构建系统
- **文件**: `semiconductor_network_builder.py`
- **功能**: 从半导体CSV数据构建供应链网络
- **输出**:
  - `Task_semiconductor.txt` (126个任务)
  - `RobotsInformation_semiconductor.txt` (397个代理)
  - `Graph_semiconductor.txt` (4250条边)
  - `semiconductor_metadata.json` (元数据)

### 2. ✅ 实验运行系统
- **文件**: `run_semiconductor_experiment.py`
- **功能**: 运行HGTM算法实验并生成结果
- **输出**:
  - Excel文件（3个工作表）
  - 4种可视化图表（PNG格式）
  - Markdown实验报告

### 3. ✅ 一键运行脚本
- **文件**: `run_experiment.sh`
- **功能**: 自动安装依赖并运行完整流程

### 4. ✅ 完整文档
- `QUICK_START_CN.md` - 快速开始指南
- `SEMICONDUCTOR_EXPERIMENT_README.md` - 完整实验说明
- `SEMICONDUCTOR_PROJECT_SUMMARY.md` - 项目技术总结
- `USAGE_GUIDE_FINAL.md` - 本文件

---

## 🚀 如何运行

### 方式一：一键运行（推荐）

```bash
chmod +x run_experiment.sh
./run_experiment.sh
```

**注意**: 由于网络规模较大（393节点，4250边），完整运行需要较长时间：
- 单次运行：约 2-5 分钟
- 10次运行：约 20-50 分钟

### 方式二：分步运行

#### 步骤1：安装依赖
```bash
pip install -r requirements.txt
```

#### 步骤2：生成网络（可选，已预生成）
```bash
python3 semiconductor_network_builder.py
```

#### 步骤3：运行实验
```bash
python3 run_semiconductor_experiment.py
```

### 方式三：手动验证网络生成

仅生成网络文件，不运行实验：
```bash
python3 semiconductor_network_builder.py
```

然后检查生成的文件：
```bash
head Task_semiconductor.txt
head RobotsInformation_semiconductor.txt
head Graph_semiconductor.txt
cat semiconductor_metadata.json
```

---

## 📊 实验配置

### 网络规模
- **节点（供应商）**: 397个
- **边（供应关系）**: 4,250条
- **任务**: 126个半导体生产任务
- **分组**: 10个社区组

### HGTM参数
- **运行次数**: 10次（可在代码中修改）
- **成本权重 (a)**: 0.1
- **存活率权重 (b)**: 0.9
- **故障率**: 30%（HGTM内部处理）

### 修改参数

编辑 `run_semiconductor_experiment.py`，找到：

```python
def main():
    experiment = SemiconductorExperiment(...)

    # 修改这里的运行次数
    experiment.run_complete_experiment(num_runs=10)  # 改为 5、20 等

# 或在 run_hgtm_experiment 方法中修改 a 和 b
def run_hgtm_experiment(self, num_runs=10, a=0.1, b=0.9):
    # a: 成本权重
    # b: 存活率权重
```

---

## 📁 输出文件

### 自动生成的输入文件
```
Task_semiconductor.txt              # 任务列表
RobotsInformation_semiconductor.txt # 代理信息
Graph_semiconductor.txt             # 网络拓扑
semiconductor_metadata.json         # 元数据
```

### 实验结果文件
```
results/
├── semiconductor_experiment_YYYYMMDD_HHMMSS.xlsx
│   ├── Summary（汇总统计）
│   ├── Detailed Results（每次运行的详细数据）
│   └── Network Statistics（网络统计）
│
├── experiment_report_YYYYMMDD_HHMMSS.md
│   └── 完整的Markdown实验报告
│
└── figures/
    ├── performance_metrics_*.png      # 性能指标趋势图
    ├── distribution_analysis_*.png    # 分布分析图
    ├── correlation_heatmap_*.png      # 相关性热图
    └── network_topology_*.png         # 网络拓扑可视化
```

---

## 📈 结果指标解释

### Excel文件 - Summary工作表

| 指标 | 含义 | 解释 |
|------|------|------|
| Mean Target Optimization | 目标优化值均值 | `a×成本 - b×存活率`，越低越好 |
| Mean Execution Cost | 执行成本均值 | 任务处理的资源消耗 |
| Mean Migration Cost | 迁移成本均值 | 任务重新分配的开销 |
| Mean Survival Rate | 存活率均值 | 系统容错能力，越高越好 |
| Mean Robot Load Std Dev | 负载标准差均值 | 负载均衡程度，越低越好 |

### 可视化图表

#### Figure 1: Performance Metrics Over Runs
- 4个子图展示关键指标的变化趋势
- 红色虚线表示均值
- 用于观察算法的稳定性

#### Figure 2: Distribution Analysis
- 直方图：结果分布特征
- 箱线图：多指标对比
- 散点图：执行时间与性能关系

#### Figure 3: Correlation Heatmap
- 展示指标间的相关性
- 红色：正相关，蓝色：负相关
- 数值范围：-1 到 1

#### Figure 4: Network Topology
- 供应链网络可视化
- 高度数节点（关键供应商）被标注
- 展示网络的连通性和社区结构

---

## ⚠️ 重要说明

### 1. 运行时间
由于半导体供应链网络规模较大：
- **单次实验**: 2-5分钟
- **10次实验**: 20-50分钟
- **建议**: 首次运行可以修改为3次或5次

### 2. 内存使用
- 网络规模：393节点 × 4250边
- 预计内存使用：约500MB-1GB
- 确保系统有足够的可用内存

### 3. 已知行为
- HGTM算法内部处理故障注入（30%故障率）
- 每次运行结果会略有不同（随机种子）
- 中介中心性计算在大规模网络上较慢

---

## 🔧 故障排除

### 问题1: ModuleNotFoundError
```bash
# 解决方案：安装依赖
pip install -r requirements.txt
```

### 问题2: 运行时间过长
```python
# 解决方案：减少运行次数
# 编辑 run_semiconductor_experiment.py
experiment.run_complete_experiment(num_runs=3)  # 改为3次
```

### 问题3: 内存不足
```bash
# 解决方案：关闭其他程序或使用更小的网络
# 可以修改 semiconductor_network_builder.py 中的网络规模
```

### 问题4: 图表显示问题
```bash
# 解决方案：使用非交互式后端（已配置）
# 代码中已设置：matplotlib.use('Agg')
```

---

## 📚 文档索引

| 文档 | 用途 | 适合人群 |
|------|------|----------|
| `QUICK_START_CN.md` | 快速开始指南 | 快速上手 |
| `SEMICONDUCTOR_EXPERIMENT_README.md` | 完整实验文档 | 深入理解 |
| `SEMICONDUCTOR_PROJECT_SUMMARY.md` | 技术总结 | 了解全貌 |
| `USAGE_GUIDE_FINAL.md` | 使用指南（本文） | 实际操作 |

---

## 🎯 典型使用流程

### 场景1: 快速验证系统
```bash
# 1. 验证文件生成
python3 semiconductor_network_builder.py

# 2. 检查生成的文件
ls -lh Task_semiconductor.txt RobotsInformation_semiconductor.txt Graph_semiconductor.txt

# 3. 查看元数据
cat semiconductor_metadata.json
```

### 场景2: 运行小规模测试
```bash
# 编辑 run_semiconductor_experiment.py，修改运行次数为3
# 然后运行
python3 run_semiconductor_experiment.py
```

### 场景3: 运行完整实验
```bash
# 使用一键脚本
./run_experiment.sh

# 等待完成后，查看结果
ls -lh results/
```

### 场景4: 分析结果
```bash
# 打开Excel文件
libreoffice results/semiconductor_experiment_*.xlsx

# 查看图表
xdg-open results/figures/performance_metrics_*.png

# 阅读报告
cat results/experiment_report_*.md
```

---

## 📊 数据来源

### CSET半导体供应链数据集
- **机构**: Center for Security and Emerging Technology (CSET)
- **年份**: 2021-2022
- **报告**: [The Semiconductor Supply Chain: Assessing National Competitiveness](https://cset.georgetown.edu/publication/semiconductor-supply-chain/)
- **文档**: https://eto.tech/dataset-docs/chipexplorer

### 数据统计
- **供应商**: 397个（公司+国家）
- **国家**: 20+个
- **半导体输入**: 126个
- **供应关系**: 1,305条
- **供应链阶段**: 3个（S1-设计, S2-制造, S3-封测）

---

## 🔬 技术栈

| 组件 | 版本 | 用途 |
|------|------|------|
| Python | 3.7+ | 主语言 |
| NetworkX | 2.6.3+ | 图论算法 |
| Pandas | 1.3.0+ | 数据处理 |
| NumPy | 1.21.0+ | 数值计算 |
| Matplotlib | 3.4.0+ | 可视化 |
| Seaborn | 0.11.0+ | 统计图表 |
| OpenPyXL | 3.0.0+ | Excel输出 |

---

## ✅ 验证清单

运行实验前，确认以下内容：

- [ ] Python 3.7+ 已安装
- [ ] 依赖包已安装 (`pip install -r requirements.txt`)
- [ ] `data/` 目录包含所有CSV文件
- [ ] 有足够的磁盘空间（至少100MB）
- [ ] 有足够的内存（至少1GB可用）
- [ ] 有充足的时间（20-50分钟用于10次运行）

---

## 🎓 学术使用建议

### 引用数据集
```
Khan, Saif M., Alexander Mann, and Dahlia Peterson.
"The Semiconductor Supply Chain: Assessing National Competitiveness."
Center for Security and Emerging Technology (CSET), January 2021.
https://cset.georgetown.edu/publication/semiconductor-supply-chain/
```

### 论文写作提示
1. **方法论**: 参考 `SEMICONDUCTOR_EXPERIMENT_README.md` 第4节
2. **结果展示**: 使用生成的高分辨率PNG图表（300 DPI）
3. **数据表格**: 直接从Excel的Summary工作表复制
4. **网络分析**: 引用网络统计数据（节点数、边数、平均度等）

---

## 🌟 下一步

实验完成后，你可以：

1. **分析结果**: 打开Excel和图表，深入分析
2. **调整参数**: 修改a、b权重，观察影响
3. **对比实验**: 运行多组不同参数的实验
4. **撰写报告**: 使用自动生成的报告作为基础
5. **扩展研究**: 基于此框架研究其他供应链

---

## 📞 支持

如有问题：
1. 查看 `SEMICONDUCTOR_EXPERIMENT_README.md` 的FAQ部分
2. 检查代码注释
3. 参考原始数据集文档

---

**实验系统已就绪！祝研究顺利！** 🎉

---

## 版本信息

- **版本**: v1.0 (2024-11-05)
- **状态**: 已测试并修复
- **Git分支**: `claude/semiconductor-supply-chain-analysis-011CUq2wrkCZCLzqGfP9XjeR`
- **提交**: 818e779

---

**End of Guide**
