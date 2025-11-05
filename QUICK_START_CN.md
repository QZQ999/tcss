# 半导体供应链实验 - 快速开始指南

## 🚀 一键运行

```bash
./run_experiment.sh
```

这将自动：
1. 安装所需依赖包
2. 构建半导体供应链网络
3. 运行HGTM算法实验（10次）
4. 生成Excel结果文件
5. 创建学术论文风格的可视化图表
6. 生成实验报告

## 📂 输出文件位置

所有结果保存在 `results/` 目录：

```
results/
├── semiconductor_experiment_YYYYMMDD_HHMMSS.xlsx    # Excel结果
├── experiment_report_YYYYMMDD_HHMMSS.md             # 实验报告
└── figures/                                         # 可视化图表
    ├── performance_metrics_*.png                    # 性能指标
    ├── distribution_analysis_*.png                  # 分布分析
    ├── correlation_heatmap_*.png                    # 相关性热图
    └── network_topology_*.png                       # 网络拓扑
```

## 🔧 手动运行步骤

### 步骤1: 安装依赖
```bash
pip install -r requirements.txt
```

### 步骤2: 构建网络（可选）
```bash
python3 semiconductor_network_builder.py
```

### 步骤3: 运行实验
```bash
python3 run_semiconductor_experiment.py
```

### 步骤4: 快速测试（3次运行）
```bash
python3 quick_test.py
```

## 📊 主要输出

### Excel文件（3个工作表）
1. **Summary**: 汇总统计（均值、标准差）
2. **Detailed Results**: 每次运行的详细指标
3. **Network Statistics**: 网络拓扑统计信息

### 可视化图表（学术论文风格）
1. **性能指标图**: 4个子图展示目标优化、执行成本、迁移成本、存活率
2. **分布分析图**: 直方图、箱线图、散点图
3. **相关性热图**: 指标间的相关系数矩阵
4. **网络拓扑图**: 供应链网络可视化

### Markdown报告
- 实验概述和配置
- 详细结果表格
- 性能分析和结论
- 参考文献

## 🔑 关键指标解读

| 指标 | 含义 | 优化目标 |
|------|------|----------|
| Target Optimization | 总体优化值（成本-存活率） | 越低越好 |
| Execution Cost | 任务执行成本 | 越低越好 |
| Migration Cost | 任务迁移成本 | 越低越好 |
| Survival Rate | 代理存活率（容错能力） | 越高越好 |
| Robot Load Std | 负载均衡程度 | 越低越好 |

## ⚙️ 自定义参数

编辑 `run_semiconductor_experiment.py`:

```python
# 修改运行次数
experiment.run_complete_experiment(num_runs=20)  # 默认10

# 修改优化权重
results = self.run_hgtm_experiment(
    num_runs=10,
    a=0.2,  # 成本权重（默认0.1）
    b=0.8   # 存活率权重（默认0.9）
)
```

## 📖 完整文档

查看详细文档: `SEMICONDUCTOR_EXPERIMENT_README.md`

## 🌐 数据来源

- **数据集**: CSET Semiconductor Supply Chain Dataset
- **包含**: 397个供应商，126个半导体输入，1305条供应关系
- **覆盖**: 全球20+个国家，3个供应链阶段（设计、制造、封测）

## ❓ 常见问题

**Q: 实验运行需要多长时间？**
A: 10次运行约1-3分钟

**Q: 如何修改故障率？**
A: 修改 `python_src/main/initialize.py` 中 `initialization()` 的第三个参数（默认0.3）

**Q: 网络有多少节点和边？**
A: 393个节点（供应商），4250条边（供应关系）

**Q: 可以使用自己的数据吗？**
A: 可以，准备相同格式的CSV文件放在 `data/` 目录

## 📧 技术支持

查看代码注释或参考文档：
- `SEMICONDUCTOR_EXPERIMENT_README.md` - 完整实验说明
- `semiconductor_network_builder.py` - 网络构建代码
- `run_semiconductor_experiment.py` - 实验运行代码

---

**祝实验顺利！Happy Experimenting!** 🎉
