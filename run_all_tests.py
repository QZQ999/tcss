#!/usr/bin/env python3
"""
批量运行所有算法在所有测试案例上，并将结果保存到 Excel
Run all algorithms on all test cases and save results to Excel
"""
import sys
import time
import os
import glob
import pandas as pd
from datetime import datetime

sys.path.append('python_src')

from input.reader import Reader
from hgtm.hgtm import Hgtm
from mpftm.mpftm import MPFTM
from gbma.gbma import GBMA
from mmlma.mmlma import MMLMA
from evaluation.evaluation_extra_target import EvaluationExtraTarget


def find_test_cases():
    """查找所有测试案例"""
    task_files = sorted(glob.glob("Task*.txt"))
    graph_files = sorted(glob.glob("Graph*.txt"))
    robot_files = sorted(glob.glob("RobotsInformation*.txt"))

    # 匹配文件（通过数字后缀）
    test_cases = []

    # 特殊处理：Task.txt 对应 Graph.txt 和默认 robot 文件
    if "Task.txt" in task_files and "Graph.txt" in graph_files:
        # 查找对应的 robot 文件
        robot_file = "RobotsInformation2.txt" if "RobotsInformation2.txt" in robot_files else None
        if robot_file:
            test_cases.append(("Task.txt", "Graph.txt", robot_file, "case_default"))

    # 其他数字编号的案例
    for task_file in task_files:
        if task_file == "Task.txt":
            continue

        # 提取数字
        import re
        match = re.search(r'Task(\d+)\.txt', task_file)
        if match:
            num = match.group(1)
            graph_file = f"Graph{num}.txt" if num != "24" else "Graph4.txt"
            robot_file = f"RobotsInformation{num}.txt" if num != "24" else "RobotsInformation4.txt"

            # 简化：使用固定的对应关系
            # Task6 -> Graph2
            # Task12 -> Graph3
            # Task18 -> Graph3
            # Task24 -> Graph4
            # Task30 -> Graph5
            mapping = {
                "6": ("Graph2.txt", "RobotsInformation2.txt"),
                "12": ("Graph3.txt", "RobotsInformation3.txt"),
                "18": ("Graph3.txt", "RobotsInformation3.txt"),
                "24": ("Graph4.txt", "RobotsInformation4.txt"),
                "30": ("Graph5.txt", "RobotsInformation5.txt"),
            }

            if num in mapping:
                graph_file, robot_file = mapping[num]
                if os.path.exists(graph_file) and os.path.exists(robot_file):
                    test_cases.append((task_file, graph_file, robot_file, f"case_{num}"))

    return test_cases


def run_algorithm(algorithm_name, tasks, arc_graph, robots, a, b):
    """运行单个算法"""
    try:
        # 需要深拷贝数据，因为算法会修改输入
        import copy
        tasks_copy = copy.deepcopy(tasks)
        graph_copy = arc_graph.copy()
        robots_copy = copy.deepcopy(robots)

        start_time = time.time()

        if algorithm_name == "HGTM":
            algorithm = Hgtm(tasks_copy, graph_copy, robots_copy, a, b)
            result = algorithm.hgtm_run()
        elif algorithm_name == "MPFTM":
            algorithm = MPFTM(tasks_copy, graph_copy, robots_copy, a, b)
            result = algorithm.mpftm_run()
        elif algorithm_name == "GBMA":
            algorithm = GBMA(tasks_copy, graph_copy, robots_copy, a, b)
            result = algorithm.gbma_run()
        elif algorithm_name == "MMLMA":
            algorithm = MMLMA(tasks_copy, graph_copy, robots_copy, a, b)
            result = algorithm.mmlma_run()
        else:
            return None

        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # Convert to ms

        return {
            'algorithm': algorithm_name,
            'execution_time_ms': round(execution_time, 2),
            'mean_execute_cost': round(result.get_mean_execute_cost(), 4),
            'mean_migration_cost': round(result.get_mean_migration_cost(), 4),
            'mean_survival_rate': round(result.get_mean_survival_rate(), 4),
            'total_cost': round(result.get_mean_execute_cost() + result.get_mean_migration_cost(), 4)
        }
    except Exception as e:
        print(f"Error running {algorithm_name}: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """主函数"""
    print("="*80)
    print("批量运行所有算法测试")
    print("Batch Running All Algorithm Tests")
    print("="*80)

    # 参数设置
    a = 0.1
    b = 1 - a

    # 算法列表
    algorithms = ["HGTM", "MPFTM", "GBMA", "MMLMA"]

    # 查找测试案例
    test_cases = find_test_cases()
    print(f"\n找到 {len(test_cases)} 个测试案例:")
    for i, (task_file, graph_file, robot_file, case_name) in enumerate(test_cases, 1):
        print(f"  {i}. {case_name}: {task_file}, {graph_file}, {robot_file}")

    # 初始化结果列表
    results = []
    reader = Reader()
    evaluation_extra = EvaluationExtraTarget()

    # 运行所有测试
    total_tests = len(test_cases) * len(algorithms)
    current_test = 0

    for task_file, graph_file, robot_file, case_name in test_cases:
        print(f"\n{'='*80}")
        print(f"测试案例: {case_name}")
        print(f"  Task File: {task_file}")
        print(f"  Graph File: {graph_file}")
        print(f"  Robot File: {robot_file}")
        print(f"{'='*80}")

        try:
            # 读取数据
            tasks = reader.read_file_to_tasks(task_file)
            arc_graph = reader.read_file_to_graph(graph_file)
            robots = reader.read_file_to_robots(robot_file)

            # 计算统计信息
            robot_capacity_std = evaluation_extra.calculate_robot_capacity_std(robots)
            task_size_std = evaluation_extra.calculate_task_size_std(tasks)
            mean_robot_capacity = evaluation_extra.calculate_mean_robot_capacity(robots)
            mean_task_size = evaluation_extra.calculate_mean_task_size(tasks)

            # 运行每个算法
            for algorithm_name in algorithms:
                current_test += 1
                print(f"\n[{current_test}/{total_tests}] 运行 {algorithm_name}...")

                result = run_algorithm(algorithm_name, tasks, arc_graph, robots, a, b)

                if result:
                    # 添加案例信息和统计信息
                    result_row = {
                        'test_case': case_name,
                        'task_file': task_file,
                        'graph_file': graph_file,
                        'robot_file': robot_file,
                        'num_tasks': len(tasks),
                        'num_robots': len(robots),
                        'mean_task_size': round(mean_task_size, 2),
                        'task_size_std': round(task_size_std, 2),
                        'mean_robot_capacity': round(mean_robot_capacity, 2),
                        'robot_capacity_std': round(robot_capacity_std, 2),
                        **result
                    }

                    results.append(result_row)

                    # 打印结果
                    print(f"  ✓ 完成 - 执行时间: {result['execution_time_ms']:.2f}ms")
                    print(f"    执行成本: {result['mean_execute_cost']:.4f}")
                    print(f"    迁移成本: {result['mean_migration_cost']:.4f}")
                    print(f"    总成本: {result['total_cost']:.4f}")
                    print(f"    存活率: {result['mean_survival_rate']:.4f}")
                else:
                    print(f"  ✗ 失败")

        except Exception as e:
            print(f"错误: 无法处理测试案例 {case_name}: {e}")
            import traceback
            traceback.print_exc()
            continue

    # 创建 DataFrame
    df = pd.DataFrame(results)

    # 生成文件名（带时间戳）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_filename = f"algorithm_results_{timestamp}.xlsx"

    # 保存到 Excel
    print(f"\n{'='*80}")
    print("保存结果到 Excel...")

    with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
        # 保存完整结果
        df.to_excel(writer, sheet_name='All Results', index=False)

        # 为每个算法创建单独的工作表
        for algorithm in algorithms:
            df_algo = df[df['algorithm'] == algorithm].copy()
            if not df_algo.empty:
                df_algo.to_excel(writer, sheet_name=algorithm, index=False)

        # 创建汇总表
        summary_data = []
        for algorithm in algorithms:
            df_algo = df[df['algorithm'] == algorithm]
            if not df_algo.empty:
                summary_data.append({
                    'Algorithm': algorithm,
                    'Test Cases': len(df_algo),
                    'Avg Execution Time (ms)': round(df_algo['execution_time_ms'].mean(), 2),
                    'Avg Execute Cost': round(df_algo['mean_execute_cost'].mean(), 4),
                    'Avg Migration Cost': round(df_algo['mean_migration_cost'].mean(), 4),
                    'Avg Total Cost': round(df_algo['total_cost'].mean(), 4),
                    'Avg Survival Rate': round(df_algo['mean_survival_rate'].mean(), 4)
                })

        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='Summary', index=False)

    print(f"✓ 结果已保存到: {excel_filename}")
    print(f"\n总共运行: {len(results)} 个测试 ({len(test_cases)} 个案例 × {len(algorithms)} 个算法)")
    print("="*80)

    # 打印汇总
    print("\n算法性能汇总:")
    print(df_summary.to_string(index=False))
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
