# TCSS - Task-based Cascading-failure Systems Simulator

多机器人系统中的任务迁移算法 - Python 实现

## 🚀 快速开始

### 方式1: 批量运行所有算法（推荐）

一键运行所有算法在所有测试案例上，并生成 Excel 报告：

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行批量测试
python run_all_tests.py
```

运行完成后会生成类似 `algorithm_results_20251104_143529.xlsx` 的 Excel 文件。

### 方式2: 运行单个算法

运行 HGTM 算法：

```bash
python main.py
```

## 📊 算法说明

本项目实现了四种任务迁移算法：

| 算法 | 说明 | 特点 |
|------|------|------|
| **HGTM** | Hierarchical Group Task Migration | 分层组任务迁移，基于势场和分组策略 |
| **MPFTM** | Multi-layer Potential Field Task Migration | 多层势场任务迁移 |
| **GBMA** | Greedy-Based Migration Algorithm | 基于贪心的迁移算法，选择最短路径 |
| **MMLMA** | Min-Max Load Migration Algorithm | 最小-最大负载迁移算法，平衡容量和负载 |

## 📁 项目结构

```
tcss/
├── main.py                          # 单算法入口（运行 HGTM）
├── run_all_tests.py                 # 批量测试入口（运行所有算法）
├── requirements.txt                 # Python 依赖
├── README.md                        # 本文件
├── README_PYTHON.md                 # Python 实现说明
├── README_BATCH_TEST.md             # 批量测试说明
│
├── python_src/                      # Python 源代码
│   ├── input/                       # 数据类和文件读取
│   │   ├── agent.py                # 机器人/智能体类
│   │   ├── task.py                 # 任务类
│   │   ├── group.py                # 组/群体类
│   │   ├── reader.py               # 文件读取器
│   │   └── ...
│   │
│   ├── main/                        # 主要工具
│   │   ├── function.py             # 工具函数
│   │   └── initialize.py           # 初始化逻辑
│   │
│   ├── hgtm/                        # HGTM 算法
│   │   ├── hgtm.py                 # 主算法
│   │   ├── finder_leader.py        # 领导节点选择
│   │   ├── finder_ad_leaders.py    # 备份领导选择
│   │   ├── groupform.py            # 分组算法
│   │   └── ...
│   │
│   ├── mpftm/                       # MPFTM 算法
│   │   ├── mpftm.py                # 主算法
│   │   ├── calculate_pon_field.py  # 势场计算
│   │   └── ...
│   │
│   ├── gbma/                        # GBMA 算法
│   │   ├── gbma.py                 # 主算法
│   │   └── gbma_tasks_migration.py # 任务迁移
│   │
│   ├── mmlma/                       # MMLMA 算法
│   │   ├── mmlma.py                # 主算法
│   │   └── mmlma_tasks_migration.py# 任务迁移
│   │
│   └── evaluation/                  # 评估指标
│       ├── evaluation.py           # 成本和存活率计算
│       └── evaluation_extra_target.py # 统计指标
│
├── Task*.txt                        # 任务配置文件
├── Graph*.txt                       # 网络拓扑文件
└── RobotsInformation*.txt          # 机器人配置文件
```

## 📈 输出指标

运行后会输出以下指标：

| 指标 | 说明 |
|------|------|
| **执行成本 (Execute Cost)** | 任务执行的总成本 |
| **迁移成本 (Migration Cost)** | 任务迁移的总成本 |
| **总成本 (Total Cost)** | 执行成本 + 迁移成本 |
| **存活率 (Survival Rate)** | 系统组件存活率 |
| **运行时间 (Execution Time)** | 算法运行时间（毫秒） |

## 📊 Excel 报告

批量测试会生成包含多个工作表的 Excel 文件：

- **All Results** - 所有测试的完整数据
- **HGTM** - HGTM 算法结果
- **MPFTM** - MPFTM 算法结果
- **GBMA** - GBMA 算法结果
- **MMLMA** - MMLMA 算法结果
- **Summary** - 汇总统计（平均值）

## 🔧 测试案例

系统自动识别以下测试文件：

| 案例 | 任务文件 | 网络文件 | 机器人文件 |
|------|----------|----------|------------|
| case_default | Task.txt | Graph.txt | RobotsInformation2.txt |
| case_6 | Task6.txt | Graph2.txt | RobotsInformation2.txt |
| case_12 | Task12.txt | Graph3.txt | RobotsInformation3.txt |
| case_18 | Task18.txt | Graph3.txt | RobotsInformation3.txt |
| case_24 | Task24.txt | Graph4.txt | RobotsInformation4.txt |
| case_30 | Task30.txt | Graph5.txt | RobotsInformation5.txt |

## 📊 示例结果

```
算法性能汇总:
Algorithm  Test Cases  Avg Execution Time (ms)  Avg Execute Cost  Avg Migration Cost  Avg Total Cost  Avg Survival Rate
     HGTM           6                     4.30           20.9508             10.9417         31.8925             0.8295
    MPFTM           6                     3.88           25.3000              6.0067         31.3067             0.7883
     GBMA           6                     0.77           33.7333             11.4123         45.1456             0.7522
    MMLMA           6                     0.25           29.5694             11.7486         41.3181             0.7484
```

从结果可以看出：
- **HGTM** 和 **MPFTM** 在总成本方面表现最好（~31）
- **HGTM** 有最高的存活率（0.8295）
- **MMLMA** 和 **GBMA** 运行速度最快（<1ms）

## 🛠️ 系统要求

- Python 3.7+
- networkx >= 2.6.3 (图处理)
- openpyxl >= 3.0.0 (Excel 生成)
- pandas >= 1.3.0 (数据处理)

## 📝 输入文件格式

### Task 文件
```
task_id size arrive_time
0 10 -1
1 8 -1
2 12 0
```

### Graph 文件
```
node1 node2 weight
0 1 1
1 2 2
2 3 1
```

### RobotsInformation 文件
```
robot_id capacity group_id
0 10 0
1 8 0
2 12 1
```

## 🔄 从 Java 到 Python

本项目是从 Java 代码库完整转换而来：

| Java | Python | 说明 |
|------|--------|------|
| JGraphT | NetworkX | 图处理库 |
| Maven | pip | 依赖管理 |
| Main.java | main.py / run_all_tests.py | 入口文件 |
| Lombok @Data | Getter/Setter 方法 | 数据类 |

## 📚 相关文档

- [Python 实现说明](README_PYTHON.md)
- [批量测试说明](README_BATCH_TEST.md)

## 🤝 贡献

欢迎提交问题和改进建议！

## 📄 License

与原 Java 实现相同。

---

**快速命令参考：**

```bash
# 安装依赖
pip install -r requirements.txt

# 运行单个算法（HGTM）
python main.py

# 运行所有算法并生成 Excel 报告
python run_all_tests.py
```
