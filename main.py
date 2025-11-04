#!/usr/bin/env python3
"""
HGTM Algorithm Main Entry Point
Run the HGTM algorithm with a single command: python main.py
"""
import sys
import time
sys.path.append('python_src')

from input.reader import Reader
from hgtm.hgtm import Hgtm
from evaluation.evaluation_extra_target import EvaluationExtraTarget


def print_experiment_result(a, b, robot_capacity_std, task_size_std,
                           mean_robot_capacity, mean_task_size, experiment_result):
    """Print experiment results"""
    mean_execute_cost = experiment_result.get_mean_execute_cost()
    mean_migration_cost = experiment_result.get_mean_migration_cost()
    mean_survival_rate = experiment_result.get_mean_survival_rate()

    target_opt = calculate_target_opt(a, b,
                                     mean_execute_cost + mean_migration_cost,
                                     mean_survival_rate)

    print(f"meanExecuteCost: {mean_execute_cost}")
    print(f"meanMigrationCost: {mean_migration_cost}")
    print(f"meanSurvivalRate: {mean_survival_rate}")
    print(f"robotLoadStd: {robot_capacity_std}")
    print(f"taskSizeStd: {task_size_std}")
    print(f"meanRobotCapacity: {mean_robot_capacity}")
    print(f"meanTaskSize: {mean_task_size}")
    print(f"targetOpt: {target_opt}")


def calculate_target_opt(a, b, mean_cost, mean_survival_rate):
    """Calculate target optimization value"""
    return a * mean_cost - b * mean_survival_rate


def main():
    """Main function"""
    # Configuration
    tasks_file = "Task24.txt"
    robot_file = "RobotsInformation4.txt"
    graph_file = "Graph4.txt"

    # Initialize reader
    reader = Reader()

    # Parameters
    a = 0.1
    b = 1 - a

    # Read input files
    print("Reading input files...")
    tasks = reader.read_file_to_tasks(tasks_file)
    arc_graph = reader.read_file_to_graph(graph_file)
    robots = reader.read_file_to_robots(robot_file)

    # Calculate statistics
    evaluation_extra_target = EvaluationExtraTarget()
    robot_capacity_std = evaluation_extra_target.calculate_robot_capacity_std(robots)
    task_size_std = evaluation_extra_target.calculate_task_size_std(tasks)
    mean_robot_capacity = evaluation_extra_target.calculate_mean_robot_capacity(robots)
    mean_task_size = evaluation_extra_target.calculate_mean_task_size(tasks)

    # Run HGTM algorithm
    print("\n" + "="*50)
    print("Running HGTM Algorithm...")
    print("="*50)
    start_time = time.time()

    hgtm = Hgtm(tasks, arc_graph, robots, a, b)
    experiment_result_hgtm = hgtm.hgtm_run()

    end_time = time.time()

    print(f"\nProgram running time: {(end_time - start_time) * 1000:.2f}ms")
    print("\nResults:")
    print("-"*50)
    print_experiment_result(a, b, robot_capacity_std, task_size_std,
                          mean_robot_capacity, mean_task_size, experiment_result_hgtm)
    print("="*50)


if __name__ == "__main__":
    main()
