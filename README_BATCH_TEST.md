# 批量测试说明 / Batch Testing Guide

## 一键运行所有算法和测试案例

本项目提供了批量测试脚本，可以一键运行所有算法在所有测试案例上，并自动生成 Excel 报告。

### 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行批量测试
python run_all_tests.py
```

### 运行结果

运行完成后，会生成一个带时间戳的 Excel 文件，例如：
- `algorithm_results_20251104_143529.xlsx`

### Excel 报告内容

生成的 Excel 文件包含多个工作表：

1. **All Results** - 所有测试结果的完整数据
2. **HGTM** - HGTM 算法的测试结果
3. **MPFTM** - MPFTM 算法的测试结果
4. **GBMA** - GBMA 算法的测试结果
5. **MMLMA** - MMLMA 算法的测试结果
6. **Summary** - 汇总统计数据

### 支持的算法

1. **HGTM** - Hierarchical Group Task Migration
2. **MPFTM** - Multi-layer Potential Field Task Migration
3. **GBMA** - Greedy-Based Migration Algorithm
4. **MMLMA** - Min-Max Load Migration Algorithm

### 测试案例

系统会自动检测项目目录中的测试文件：
- Task*.txt - 任务文件
- Graph*.txt - 网络拓扑文件
- RobotsInformation*.txt - 机器人配置文件

### 输出指标

每个测试结果包含以下指标：
- **执行时间 (Execution Time)** - 算法运行时间（毫秒）
- **执行成本 (Execute Cost)** - 任务执行成本
- **迁移成本 (Migration Cost)** - 任务迁移成本
- **总成本 (Total Cost)** - 执行成本 + 迁移成本
- **存活率 (Survival Rate)** - 系统存活率
- **任务数量 (Num Tasks)** - 测试案例中的任务数量
- **机器人数量 (Num Robots)** - 测试案例中的机器人数量
- 以及其他统计信息...

### 示例输出

```
================================================================================
批量运行所有算法测试
Batch Running All Algorithm Tests
================================================================================

找到 6 个测试案例:
  1. case_default: Task.txt, Graph.txt, RobotsInformation2.txt
  2. case_12: Task12.txt, Graph3.txt, RobotsInformation3.txt
  3. case_18: Task18.txt, Graph3.txt, RobotsInformation3.txt
  4. case_24: Task24.txt, Graph4.txt, RobotsInformation4.txt
  5. case_30: Task30.txt, Graph5.txt, RobotsInformation5.txt
  6. case_6: Task6.txt, Graph2.txt, RobotsInformation2.txt

[进度] 运行 HGTM 在 case_default...
  ✓ 完成 - 执行时间: 6.60ms
    执行成本: 30.3800
    迁移成本: 8.4500
    总成本: 38.8300
    存活率: 0.8113

... (更多测试结果)

✓ 结果已保存到: algorithm_results_20251104_143529.xlsx

总共运行: 24 个测试 (6 个案例 × 4 个算法)

算法性能汇总:
Algorithm  Test Cases  Avg Execution Time (ms)  Avg Execute Cost  Avg Migration Cost  Avg Total Cost  Avg Survival Rate
     HGTM           6                     4.30           20.9508             10.9417         31.8925             0.8295
    MPFTM           6                     3.88           25.3000              6.0067         31.3067             0.7883
     GBMA           6                     0.77           33.7333             11.4123         45.1456             0.7522
    MMLMA           6                     0.25           29.5694             11.7486         41.3181             0.7484
```

### 自定义测试

如果需要运行特定的测试案例，可以修改测试文件或直接使用单算法脚本：

```bash
# 单独运行 HGTM 算法
python main.py
```

### 技术细节

- 使用 `pandas` 和 `openpyxl` 生成 Excel 报告
- 使用 `copy.deepcopy()` 确保每次测试的数据独立
- 自动捕获和报告错误
- 支持并行测试（如需要可扩展）

### 注意事项

1. 确保所有测试文件（Task, Graph, RobotsInformation）都在项目根目录
2. 测试过程中会打印详细的进度信息
3. 如果某个测试失败，会继续运行其他测试
4. 生成的 Excel 文件会自动包含时间戳，不会覆盖之前的结果

## 系统要求

- Python 3.7+
- networkx >= 2.6.3
- openpyxl >= 3.0.0
- pandas >= 1.3.0

## License

Same as the original Java implementation.
