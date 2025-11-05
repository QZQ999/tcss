# 半导体产业链网络实验说明
# Semiconductor Supply Chain Network Experiment Documentation

## 📋 目录 / Table of Contents

1. [实验概述](#实验概述)
2. [数据说明](#数据说明)
3. [网络构建](#网络构建)
4. [实验设计](#实验设计)
5. [运行实验](#运行实验)
6. [结果解读](#结果解读)
7. [文件说明](#文件说明)

---

## 1. 实验概述 / Experiment Overview

### 1.1 研究目标

本实验基于真实的全球半导体产业链数据，构建供应链网络模型，并应用**层次化分组任务迁移（HGTM）算法**评估供应链在故障条件下的韧性和任务分配效率。

**This experiment constructs a supply chain network model based on real global semiconductor industry data and applies the Hierarchical Group Task Migration (HGTM) algorithm to evaluate supply chain resilience and task allocation efficiency under fault conditions.**

### 1.2 核心问题

- 半导体供应链如何应对节点（企业/国家）故障？
- 任务（芯片生产环节）如何高效迁移和重新分配？
- 网络拓扑结构对供应链韧性的影响？

**Core Questions:**
- How does the semiconductor supply chain respond to node (company/country) failures?
- How can tasks (chip production stages) be efficiently migrated and reallocated?
- What is the impact of network topology on supply chain resilience?

### 1.3 算法简介：HGTM (Hierarchical Group Task Migration)

HGTM是一种分布式任务迁移算法，专为多智能体系统设计，具有以下特点：

- **层次化结构**：将代理组织成分组，每组有领导者和备用领导者
- **故障容错**：自动检测并处理节点故障（功能故障和过载故障）
- **势场引导**：基于势场理论进行任务迁移决策
- **负载均衡**：优化整体网络的任务分配

**HGTM Features:**
- **Hierarchical Structure**: Organizes agents into groups with leaders and backup leaders
- **Fault Tolerance**: Automatically detects and handles node failures (functional and overload)
- **Potential Field Guidance**: Task migration decisions based on potential field theory
- **Load Balancing**: Optimizes task distribution across the network

---

## 2. 数据说明 / Data Description

### 2.1 数据来源

- **数据集**: CSET Semiconductor Supply Chain Dataset
- **来源机构**: Center for Security and Emerging Technology (CSET)
- **发布时间**: 2021年（2022年增强）
- **数据规模**: 1,993条记录
- **参考报告**: [The Semiconductor Supply Chain: Assessing National Competitiveness](https://cset.georgetown.edu/publication/semiconductor-supply-chain/)

### 2.2 数据文件

#### `data/providers.csv` (398行)
供应商信息，包括公司和国家：

| 字段 | 说明 | 示例 |
|------|------|------|
| provider_id | 供应商唯一标识 | 1, 2, 3... |
| provider_name | 供应商名称 | Intel, TSMC, Samsung, USA, China |
| provider_type | 类型 | Company, Country |
| country | 所属国家 | USA, Taiwan, South Korea |

**主要供应商**: Intel, AMD, TSMC, Samsung, ASML, Applied Materials, 等

#### `data/inputs.csv` (145行)
半导体生产输入和工艺：

| 字段 | 说明 | 示例 |
|------|------|------|
| input_id | 输入唯一标识 | I001, I002... |
| input_name | 输入名称 | CPUs, GPUs, Lithography Tools |
| type | 类型 | Product, Equipment, Material |
| stage_id | 供应链阶段 | S1, S2, S3 |
| stage_name | 阶段名称 | Design, Fabrication, ATP |

**供应链阶段**:
- **S1-Design**: 芯片设计（CPU、GPU、FPGA、EDA工具等）
- **S2-Fabrication**: 晶圆制造（光刻、刻蚀、沉积、离子注入等）
- **S3-Assembly/Testing/Packaging (ATP)**: 封装测试

#### `data/provision.csv` (1,306行)
供应关系映射：

| 字段 | 说明 | 示例 |
|------|------|------|
| provider_id | 供应商ID | 1 |
| provider_name | 供应商名称 | Intel |
| provided_id | 提供的输入ID | I001 |
| provided_name | 提供的输入名称 | CPUs |
| share_provided | 市场份额 | 15.5 |
| year | 年份 | 2021 |

#### `data/stages.csv` (4行)
供应链阶段定义

#### `data/sequence.csv` (140行)
输入之间的层次关系和依赖关系

---

## 3. 网络构建 / Network Construction

### 3.1 网络拓扑结构

**节点 (Nodes):**
- 每个节点代表一个供应商（公司或国家）
- 节点属性：名称、类型、国家

**边 (Edges):**
- 连接提供相同输入的供应商（供应链合作伙伴）
- 边权重：基于市场份额的反向关系（市场份额越高，连接越强，权重越低）
- 权重计算：`weight = max(1.0, 10.0 - combined_share * 9.0)`

**连通性保证:**
- 如果网络出现孤立组件，自动连接最大度节点以确保全连通

### 3.2 网络构建算法

```python
1. 加载providers.csv，为每个供应商创建节点
2. 解析provision.csv，识别共同提供同一输入的供应商对
3. 为供应商对创建边，权重基于市场份额
4. 检查并确保网络连通性
5. 输出网络统计信息
```

### 3.3 网络统计

根据实际数据，网络规模约为：
- **节点数**: ~398个供应商
- **边数**: 根据供应关系动态生成
- **平均度**: 依赖于供应商间的合作关系密度
- **直径**: 网络最长最短路径

---

## 4. 实验设计 / Experimental Design

### 4.1 实验输入生成

#### 任务 (Tasks)
- **来源**: `inputs.csv` 中的每个半导体输入
- **任务大小**: 基于供应链阶段和市场重要性
  - `size = base_size × stage_multiplier × random(0.8, 1.5)`
  - 后期阶段（S2、S3）任务更复杂，尺寸更大
- **到达时间**: 按供应链阶段分层到达
  - 设计阶段(S1)最早，封装测试(S3)最晚
- **输出格式**: `Task_semiconductor.txt`
  ```
  task_id size arrive_time
  0 15.23 0
  1 18.45 1
  ...
  ```

#### 代理 (Agents/Robots)
- **来源**: `providers.csv` 中的供应商
- **容量 (Capacity)**: 基于供应商类型
  - 国家: 80-150（更高容量）
  - 公司: 30-100（可变容量）
- **分组 (Group)**: 使用社区检测算法自动分组
  - 默认10个组
  - 基于网络模块度优化
- **输出格式**: `RobotsInformation_semiconductor.txt`
  ```
  robot_id capacity group_id
  1 95.32 0
  2 67.89 1
  ...
  ```

#### 图拓扑 (Graph)
- **来源**: 构建的网络 `G`
- **输出格式**: `Graph_semiconductor.txt`
  ```
  node1 node2 weight
  1 2 3.5
  2 3 5.2
  ...
  ```

### 4.2 实验参数

| 参数 | 值 | 说明 |
|------|-----|------|
| 实验运行次数 | 10 | 重复实验以获得统计显著性 |
| 故障率 | 30% | 代理故障比例（默认） |
| 故障类型 | fault_a, fault_o | 功能故障和过载故障 |
| 优化权重 a | 0.1 | 成本项权重 |
| 优化权重 b | 0.9 | 存活率权重 |
| 备用领导数 | 2 | 每组的备用领导者数量 |

### 4.3 评估指标

#### 主要指标

1. **目标优化值 (Target Optimization)**
   - 公式: `targetOpt = a × totalCost - b × survivalRate`
   - 越低越好（平衡成本和存活率）

2. **执行成本 (Execution Cost)**
   - 公式: `sum(task_size / agent_capacity)`
   - 衡量任务处理负担

3. **迁移成本 (Migration Cost)**
   - 基于网络中的最短路径距离
   - 衡量任务重新分配的开销

4. **存活率 (Survival Rate)**
   - 公式: `(1 - fault_a) × (1 - fault_o)`
   - 反映网络容错能力

#### 辅助指标

5. **负载标准差 (Robot Load Std Dev)**: 负载均衡程度
6. **任务规模标准差 (Task Size Std Dev)**: 任务分布均匀性
7. **执行时间 (Execution Time)**: 算法性能

---

## 5. 运行实验 / Running the Experiment

### 5.1 环境要求

- **Python版本**: Python 3.7+
- **依赖包**: 见 `requirements.txt`
  ```
  networkx>=2.6.3
  pandas>=1.3.0
  numpy>=1.21.0
  matplotlib>=3.4.0
  seaborn>=0.11.0
  openpyxl>=3.0.0
  ```

### 5.2 一键运行（推荐）

使用提供的Shell脚本一键运行完整实验：

```bash
chmod +x run_experiment.sh
./run_experiment.sh
```

脚本自动完成：
1. 检查Python环境
2. 安装依赖包
3. 运行完整实验流程
4. 生成所有结果文件

### 5.3 手动运行

#### 步骤1: 安装依赖
```bash
pip install -r requirements.txt
```

#### 步骤2: 构建网络（可选，独立运行）
```bash
python3 semiconductor_network_builder.py
```

输出文件：
- `Task_semiconductor.txt`
- `RobotsInformation_semiconductor.txt`
- `Graph_semiconductor.txt`
- `semiconductor_metadata.json`

#### 步骤3: 运行完整实验
```bash
python3 run_semiconductor_experiment.py
```

### 5.4 自定义参数

修改 `run_semiconductor_experiment.py` 中的参数：

```python
# 在 main() 函数中修改
experiment.run_complete_experiment(num_runs=20)  # 改为20次运行

# 或修改 HGTM 参数
results = self.run_hgtm_experiment(
    num_runs=10,
    a=0.2,  # 增加成本权重
    b=0.8   # 减少存活率权重
)
```

---

## 6. 结果解读 / Results Interpretation

### 6.1 输出文件

实验运行后，`results/` 目录包含：

```
results/
├── semiconductor_experiment_YYYYMMDD_HHMMSS.xlsx    # Excel结果
├── experiment_report_YYYYMMDD_HHMMSS.md             # Markdown报告
└── figures/
    ├── performance_metrics_YYYYMMDD_HHMMSS.png      # 性能指标图
    ├── distribution_analysis_YYYYMMDD_HHMMSS.png    # 分布分析图
    ├── correlation_heatmap_YYYYMMDD_HHMMSS.png      # 相关性热图
    └── network_topology_YYYYMMDD_HHMMSS.png         # 网络拓扑图
```

### 6.2 Excel文件结构

#### Sheet 1: Summary
汇总统计信息：
- 成功/失败运行次数
- 各指标的均值和标准差
- 总执行时间

#### Sheet 2: Detailed Results
每次运行的详细结果：
- run_id: 运行编号
- targetOpt: 目标优化值
- meanExecuteCost: 平均执行成本
- meanMigrationCost: 平均迁移成本
- meanSurvivalRate: 平均存活率
- execution_time_ms: 执行时间（毫秒）
- 其他辅助指标

#### Sheet 3: Network Statistics
网络统计信息：
- 节点数、边数
- 连通性
- 平均度
- 供应商和输入数量

### 6.3 可视化图表

#### Figure 1: Performance Metrics Over Runs
四个子图展示实验过程中的性能指标变化：
- (a) 目标优化函数
- (b) 执行成本
- (c) 迁移成本
- (d) 代理存活率

**解读要点**:
- 红色虚线表示均值
- 观察指标的稳定性（标准差小表示算法稳定）
- 比较不同指标的相对大小

#### Figure 2: Distribution Analysis
展示结果分布特征：
- (a)(b) 直方图：目标优化和执行成本的分布
- (c) 箱线图：标准化后的多指标对比
- (d) 散点图：执行时间与性能的关系

**解读要点**:
- 直方图反映结果的集中程度
- 箱线图中位线越接近说明各指标平衡性好
- 散点图颜色深浅反映性能好坏

#### Figure 3: Correlation Heatmap
性能指标间的相关性矩阵：
- 红色：正相关
- 蓝色：负相关
- 数值：相关系数 (-1 到 1)

**解读要点**:
- targetOpt与成本项的相关性（预期正相关）
- survivalRate与targetOpt的相关性（预期负相关，因为b>a）
- 执行时间与性能指标的关系

#### Figure 4: Network Topology
供应链网络可视化：
- 节点：供应商
- 边：供应关系
- 标注：高度数节点（关键供应商）

**解读要点**:
- 识别网络中的关键节点（枢纽）
- 观察社区结构（聚类情况）
- 评估网络密度和连通性

### 6.4 Markdown报告

自动生成的报告包含：

1. **实验概述**: 目标和配置
2. **实验结果**: 统计表格
3. **分析**:
   - 算法性能评价
   - 成本分析
   - 负载均衡评估
4. **结论**: 主要发现和建议
5. **参考文献**: 数据来源

---

## 7. 文件说明 / File Descriptions

### 7.1 核心脚本

| 文件名 | 功能 | 说明 |
|--------|------|------|
| `semiconductor_network_builder.py` | 网络构建器 | 从CSV数据构建网络并生成实验输入 |
| `run_semiconductor_experiment.py` | 实验运行器 | 执行HGTM实验、生成结果和可视化 |
| `run_experiment.sh` | 一键脚本 | Bash脚本，自动安装依赖并运行实验 |
| `main.py` | 原始入口 | 原始HGTM算法的示例运行脚本 |

### 7.2 算法模块

```
python_src/
├── input/           # 输入处理模块
│   ├── reader.py           # 文件读取
│   ├── agent.py            # 代理类定义
│   ├── task.py             # 任务类定义
│   └── ...
├── hgtm/            # HGTM算法核心
│   ├── hgtm.py             # 主算法流程
│   ├── finder_leader.py    # 领导者选择（中介中心性）
│   ├── groupform.py        # 分组形成
│   └── ...
├── mpftm/           # 多机器人势场任务迁移
│   └── ...
├── main/            # 工具函数
│   ├── function.py
│   └── initialize.py       # 初始化和故障注入
└── evaluation/      # 评估模块
    └── evaluation.py       # 性能指标计算
```

### 7.3 数据文件

| 文件 | 类型 | 大小 | 说明 |
|------|------|------|------|
| `data/providers.csv` | CSV | 398行 | 供应商信息 |
| `data/inputs.csv` | CSV | 145行 | 半导体输入 |
| `data/provision.csv` | CSV | 1306行 | 供应关系 |
| `data/stages.csv` | CSV | 4行 | 供应链阶段 |
| `data/sequence.csv` | CSV | 140行 | 输入依赖关系 |

### 7.4 生成文件

**实验输入文件**:
- `Task_semiconductor.txt`: 任务列表
- `RobotsInformation_semiconductor.txt`: 代理信息
- `Graph_semiconductor.txt`: 网络拓扑
- `semiconductor_metadata.json`: 元数据

**实验输出文件**:
- `results/semiconductor_experiment_*.xlsx`: Excel结果
- `results/experiment_report_*.md`: Markdown报告
- `results/figures/*.png`: 可视化图表

---

## 8. 常见问题 / FAQ

### Q1: 实验运行时间多长？

**A**: 取决于实验运行次数和网络规模。通常：
- 10次运行：约1-3分钟
- 20次运行：约2-5分钟
- 网络节点数越多，时间越长

### Q2: 如何调整故障率？

**A**: 修改 `python_src/main/initialize.py` 中的初始化函数，或在 `run_semiconductor_experiment.py` 中的 `initialization()` 调用处修改第三个参数（默认0.3即30%）。

### Q3: 如何改变分组数量？

**A**: 修改 `semiconductor_network_builder.py` 中 `generate_agents()` 函数的 `num_groups` 参数（默认10）。

### Q4: 结果指标应该关注什么？

**A**: 主要关注：
1. **targetOpt**: 越低越好，表示成本和存活率的平衡
2. **meanSurvivalRate**: 越高越好，表示容错能力强
3. **robotLoadStd**: 越低越好，表示负载均衡好

### Q5: 如何比较不同参数设置？

**A**: 多次运行实验，修改参数（如a、b、故障率、分组数），保存不同的结果文件，然后比较Excel中的Summary表格。

### Q6: 网络构建是否可以自定义？

**A**: 可以。修改 `SemiconductorNetworkBuilder.build_network()` 方法中的边权重计算逻辑，或添加额外的连接规则。

### Q7: 如何处理实验失败？

**A**: 检查：
1. 依赖包是否正确安装
2. 数据文件是否存在于 `data/` 目录
3. 查看错误日志定位问题
4. 确保Python版本>=3.7

### Q8: 可以用自己的数据吗？

**A**: 可以。参照CSV文件格式准备数据：
- `providers.csv`: 供应商列表
- `inputs.csv`: 产品/工艺列表
- `provision.csv`: 供应关系
然后运行相同的脚本。

---

## 9. 技术支持与引用 / Support and Citation

### 9.1 数据来源引用

```
Khan, Saif M., Alexander Mann, and Dahlia Peterson.
"The Semiconductor Supply Chain: Assessing National Competitiveness."
Center for Security and Emerging Technology (CSET), January 2021.
https://cset.georgetown.edu/publication/semiconductor-supply-chain/
```

### 9.2 算法参考

HGTM算法基于分布式多智能体系统的任务迁移理论，结合：
- 中介中心性（Betweenness Centrality）用于领导者选择
- 势场理论（Potential Field Theory）用于任务迁移
- 社区检测（Community Detection）用于分组

### 9.3 联系方式

如有问题或建议，请参考：
- 原始数据集文档: https://eto.tech/dataset-docs/chipexplorer
- CSET官方网站: https://cset.georgetown.edu/

---

## 10. 附录 / Appendix

### 10.1 HGTM算法伪代码

```
Algorithm: HGTM (Hierarchical Group Task Migration)

Input:
  - robots_load: Agent集合及其负载
  - tasks: 任务集合
  - robots_fault_set: 故障代理集合
  - graph: 网络拓扑图

Output:
  - experiment_result: 实验结果
  - migration_record: 迁移记录

Steps:
1. 初始化任务分配和故障
2. 选择各组领导者（基于中介中心性）
3. 选择备用领导者
4. 处理领导者故障替换
5. 计算上下文负载
6. 计算组内和组间势场
   - 组内：吸引力
   - 组间：排斥力
7. 形成故障代理组（bags）
8. 基于势场执行任务迁移
9. 评估结果
   - 计算执行成本
   - 计算迁移成本
   - 计算存活率
   - 计算目标优化值
```

### 10.2 网络指标说明

| 指标 | 公式/定义 | 意义 |
|------|-----------|------|
| 度 (Degree) | 节点的连接边数 | 节点的直接连接数量 |
| 中介中心性 (Betweenness) | 通过节点的最短路径数量 | 节点在网络中的枢纽作用 |
| 聚类系数 (Clustering) | 邻居间连接密度 | 局部网络的紧密程度 |
| 最短路径 (Shortest Path) | 两节点间的最小跳数 | 任务迁移的距离成本 |

### 10.3 实验设计最佳实践

1. **重复实验**: 至少10次运行以获得统计显著性
2. **参数扫描**: 系统性地改变a、b、故障率等参数
3. **对照实验**: 比较HGTM与其他算法（如随机分配、贪心算法）
4. **敏感性分析**: 评估网络结构变化对结果的影响
5. **可视化验证**: 使用图表辅助理解结果

---

## 版本历史 / Version History

- **v1.0** (2024): 初始版本，完整实验框架
  - 网络构建器
  - HGTM实验运行器
  - Excel输出和可视化
  - 自动化报告生成

---

**文档结束 / End of Documentation**

如有疑问，请查阅代码注释或运行示例脚本。祝实验顺利！

For questions, please refer to code comments or run the example scripts. Happy experimenting!
