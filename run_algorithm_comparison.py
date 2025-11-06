"""
Algorithm Comparison Experiment

This script compares four task migration algorithms:
1. HGTM - Hierarchical Group Task Migration
2. GBMA - Greedy-Based Migration Algorithm
3. MMLMA - Max Margin Load Migration Algorithm
4. MPFTM - Multi-layer Potential Field Task Migration
"""

import sys
import time
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import seaborn as sns

# Import local modules
from python_src.input.reader import read_task, read_robot, read_graph
from python_src.main.initialize import initialization
from python_src.hgtm.hgtm import hgtm
from python_src.gbma.gbma import GBMA
from python_src.mmlma.mmlma import MMLMA
from python_src.mpftm.mpftm import MPFTM
from python_src.evaluation.evaluation import evaluation


class AlgorithmComparison:
    """Framework for comparing task migration algorithms"""

    def __init__(self, data_dir: str = "data", output_dir: str = "results"):
        """
        Initialize comparison framework

        Args:
            data_dir: Directory containing experimental data
            output_dir: Directory for results
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.experiment_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {}

    def run_single_algorithm(self, algorithm_name: str, tasks, robots_load, graph, a=0.1, b=0.9):
        """
        Run a single algorithm

        Args:
            algorithm_name: Name of algorithm (HGTM, GBMA, MMLMA, MPFTM)
            tasks: List of tasks
            robots_load: List of robots
            graph: Network graph
            a: Weight parameter
            b: Weight parameter

        Returns:
            Tuple of (experiment_result, migration_records, execution_time_ms)
        """
        start_time = time.time()

        try:
            if algorithm_name == "HGTM":
                # Run HGTM
                hgtm_result = hgtm(robots_load, tasks, [], graph)
                experiment_result = hgtm_result[0]
                migration_records = hgtm_result[1]

            elif algorithm_name == "GBMA":
                # Run GBMA
                gbma_algo = GBMA(tasks, graph, robots_load, a, b)
                experiment_result = gbma_algo.gbma_run()
                migration_records = []  # GBMA returns migration records internally

            elif algorithm_name == "MMLMA":
                # Run MMLMA
                mmlma_algo = MMLMA(tasks, graph, robots_load, a, b)
                experiment_result = mmlma_algo.mmlma_run()
                migration_records = []  # MMLMA returns migration records internally

            elif algorithm_name == "MPFTM":
                # Run MPFTM
                mpftm_algo = MPFTM(tasks, graph, robots_load, a, b)
                experiment_result = mpftm_algo.mpftm_run()
                migration_records = []  # MPFTM returns migration records internally

            else:
                raise ValueError(f"Unknown algorithm: {algorithm_name}")

            execution_time_ms = (time.time() - start_time) * 1000

            return experiment_result, migration_records, execution_time_ms

        except Exception as e:
            print(f"Error running {algorithm_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None, None, 0

    def run_comparison_experiment(self, num_runs: int = 10, task_file: str = None,
                                 robot_file: str = None, graph_file: str = None,
                                 a: float = 0.1, b: float = 0.9):
        """
        Run comparison experiment across all algorithms

        Args:
            num_runs: Number of experimental runs
            task_file: Task data file
            robot_file: Robot data file
            graph_file: Graph data file
            a: Weight for cost in optimization
            b: Weight for survival rate in optimization

        Returns:
            Dictionary of aggregated results
        """
        print("\n" + "="*80)
        print(" "*20 + "ALGORITHM COMPARISON EXPERIMENT")
        print("="*80)

        # Default file names
        if task_file is None:
            task_file = "Task_semiconductor.txt"
        if robot_file is None:
            robot_file = "RobotsInformation_semiconductor.txt"
        if graph_file is None:
            graph_file = "Graph_semiconductor.txt"

        algorithms = ["HGTM", "GBMA", "MMLMA", "MPFTM"]
        all_results = {alg: [] for alg in algorithms}

        for run_id in range(num_runs):
            print(f"\n{'='*80}")
            print(f"Run {run_id + 1}/{num_runs}")
            print(f"{'='*80}")

            try:
                # Read input files
                tasks = read_task(task_file)
                robots_load = read_robot(robot_file)
                graph = read_graph(graph_file)

                # Initialize tasks and faults (with same random seed for fair comparison)
                # Note: We create separate copies for each algorithm
                for alg_name in algorithms:
                    print(f"\nRunning {alg_name}...")

                    # Create fresh copies of data for each algorithm
                    tasks_copy = read_task(task_file)
                    robots_copy = read_robot(robot_file)
                    graph_copy = read_graph(graph_file)

                    # Initialize with same fault pattern
                    initial_result = initialization(robots_copy, tasks_copy, 0.3)
                    robots_copy = initial_result[0]
                    tasks_all_migration = initial_result[1]
                    robots_fault_set = initial_result[2]

                    # Run algorithm
                    experiment_result, migration_records, exec_time = self.run_single_algorithm(
                        alg_name, tasks_all_migration, robots_copy, graph_copy, a, b
                    )

                    if experiment_result is None:
                        print(f"  ✗ {alg_name} failed")
                        continue

                    # Evaluation
                    evaluation_result = evaluation(
                        experiment_result,
                        migration_records if migration_records else [],
                        graph_copy,
                        robots_fault_set,
                        a, b
                    )

                    # Extract metrics
                    result = {
                        'run_id': run_id + 1,
                        'algorithm': alg_name,
                        'meanExecuteCost': evaluation_result[0],
                        'meanMigrationCost': evaluation_result[1],
                        'meanSurvivalRate': evaluation_result[2],
                        'robotLoadStd': evaluation_result[3],
                        'taskSizeStd': evaluation_result[4],
                        'meanRobotCapacity': evaluation_result[5],
                        'meanTaskSize': evaluation_result[6],
                        'targetOpt': evaluation_result[7],
                        'execution_time_ms': exec_time,
                        'num_tasks': len(tasks_copy),
                        'num_robots': len(robots_copy),
                        'num_faulty_robots': len(robots_fault_set),
                        'fault_rate': len(robots_fault_set) / len(robots_copy)
                    }

                    all_results[alg_name].append(result)

                    print(f"  ✓ {alg_name} completed in {exec_time:.2f}ms")
                    print(f"    - Target Optimization: {result['targetOpt']:.4f}")
                    print(f"    - Mean Survival Rate: {result['meanSurvivalRate']:.4f}")

            except Exception as e:
                print(f"  ✗ Run {run_id + 1} failed: {str(e)}")
                import traceback
                traceback.print_exc()
                continue

        # Aggregate results
        aggregated_results = {}
        for alg_name in algorithms:
            if len(all_results[alg_name]) > 0:
                df_results = pd.DataFrame(all_results[alg_name])

                aggregated_results[alg_name] = {
                    'num_successful_runs': len(all_results[alg_name]),
                    'num_failed_runs': num_runs - len(all_results[alg_name]),
                    'mean_targetOpt': df_results['targetOpt'].mean(),
                    'std_targetOpt': df_results['targetOpt'].std(),
                    'mean_executeCost': df_results['meanExecuteCost'].mean(),
                    'std_executeCost': df_results['meanExecuteCost'].std(),
                    'mean_migrationCost': df_results['meanMigrationCost'].mean(),
                    'std_migrationCost': df_results['meanMigrationCost'].std(),
                    'mean_survivalRate': df_results['meanSurvivalRate'].mean(),
                    'std_survivalRate': df_results['meanSurvivalRate'].std(),
                    'mean_robotLoadStd': df_results['robotLoadStd'].mean(),
                    'mean_execution_time_ms': df_results['execution_time_ms'].mean(),
                    'total_execution_time_s': df_results['execution_time_ms'].sum() / 1000,
                    'all_runs': df_results
                }

        self.results = aggregated_results
        self.print_comparison_summary()

        return aggregated_results

    def print_comparison_summary(self):
        """Print comparison summary"""
        print("\n" + "="*80)
        print("ALGORITHM COMPARISON SUMMARY")
        print("="*80)

        # Print table header
        print(f"\n{'Algorithm':<12} {'Runs':<8} {'Target Opt':<20} {'Survival Rate':<20} {'Exec Time (ms)':<15}")
        print("-" * 80)

        # Print results for each algorithm
        for alg_name, results in self.results.items():
            print(f"{alg_name:<12} "
                  f"{results['num_successful_runs']:<8} "
                  f"{results['mean_targetOpt']:>8.4f} ± {results['std_targetOpt']:<8.4f} "
                  f"{results['mean_survivalRate']:>8.4f} ± {results['std_survivalRate']:<8.4f} "
                  f"{results['mean_execution_time_ms']:>12.2f}")

        print("="*80)

    def export_to_excel(self, filename: str = None):
        """Export comparison results to Excel"""
        print("\n" + "="*80)
        print("EXPORTING RESULTS TO EXCEL")
        print("="*80)

        if not self.results:
            print("✗ No results to export")
            return

        if filename is None:
            filename = f"algorithm_comparison_{self.experiment_id}.xlsx"

        output_path = self.output_dir / filename

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Sheet 1: Summary comparison
            summary_data = []
            for alg_name, results in self.results.items():
                summary_data.append({
                    'Algorithm': alg_name,
                    'Successful Runs': results['num_successful_runs'],
                    'Failed Runs': results['num_failed_runs'],
                    'Mean Target Opt': results['mean_targetOpt'],
                    'Std Target Opt': results['std_targetOpt'],
                    'Mean Execution Cost': results['mean_executeCost'],
                    'Std Execution Cost': results['std_executeCost'],
                    'Mean Migration Cost': results['mean_migrationCost'],
                    'Std Migration Cost': results['std_migrationCost'],
                    'Mean Survival Rate': results['mean_survivalRate'],
                    'Std Survival Rate': results['std_survivalRate'],
                    'Mean Robot Load Std': results['mean_robotLoadStd'],
                    'Mean Execution Time (ms)': results['mean_execution_time_ms'],
                    'Total Execution Time (s)': results['total_execution_time_s']
                })

            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Summary', index=False)

            # Sheet 2-5: Detailed results for each algorithm
            for alg_name, results in self.results.items():
                df_details = results['all_runs']
                df_details.to_excel(writer, sheet_name=f'{alg_name} Details', index=False)

        print(f"✓ Results exported to: {output_path}")

    def create_comparison_visualizations(self):
        """Create comparison visualizations"""
        print("\n" + "="*80)
        print("CREATING COMPARISON VISUALIZATIONS")
        print("="*80)

        if not self.results:
            print("✗ No results to visualize")
            return

        fig_dir = self.output_dir / "figures"
        fig_dir.mkdir(exist_ok=True)

        # Set publication-quality style
        plt.style.use('seaborn-v0_8-paper')
        sns.set_palette("husl")

        # Prepare data for plotting
        algorithms = list(self.results.keys())
        metrics = {
            'Target Optimization': ('mean_targetOpt', 'std_targetOpt'),
            'Execution Cost': ('mean_executeCost', 'std_executeCost'),
            'Migration Cost': ('mean_migrationCost', 'std_migrationCost'),
            'Survival Rate': ('mean_survivalRate', 'std_survivalRate')
        }

        # Figure 1: Bar chart comparison
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Algorithm Performance Comparison', fontsize=16, fontweight='bold')

        for idx, (metric_name, (mean_key, std_key)) in enumerate(metrics.items()):
            ax = axes[idx // 2, idx % 2]

            means = [self.results[alg][mean_key] for alg in algorithms]
            stds = [self.results[alg][std_key] for alg in algorithms]

            x_pos = np.arange(len(algorithms))
            ax.bar(x_pos, means, yerr=stds, capsize=5, alpha=0.7)
            ax.set_xticks(x_pos)
            ax.set_xticklabels(algorithms)
            ax.set_ylabel(metric_name, fontsize=11)
            ax.set_title(f'({chr(97+idx)}) {metric_name}', fontsize=11)
            ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        fig1_path = fig_dir / f"algorithm_comparison_bars_{self.experiment_id}.png"
        plt.savefig(fig1_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Figure 1 saved: {fig1_path}")

        # Figure 2: Performance over runs
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Performance Metrics Over Runs', fontsize=16, fontweight='bold')

        metric_keys = ['targetOpt', 'meanExecuteCost', 'meanMigrationCost', 'meanSurvivalRate']
        metric_titles = ['Target Optimization', 'Execution Cost', 'Migration Cost', 'Survival Rate']

        for idx, (metric_key, metric_title) in enumerate(zip(metric_keys, metric_titles)):
            ax = axes[idx // 2, idx % 2]

            for alg_name in algorithms:
                df = self.results[alg_name]['all_runs']
                ax.plot(df['run_id'], df[metric_key], marker='o', label=alg_name, linewidth=2)

            ax.set_xlabel('Run ID', fontsize=11)
            ax.set_ylabel(metric_title, fontsize=11)
            ax.set_title(f'({chr(97+idx)}) {metric_title}', fontsize=11)
            ax.legend()
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        fig2_path = fig_dir / f"algorithm_comparison_lines_{self.experiment_id}.png"
        plt.savefig(fig2_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Figure 2 saved: {fig2_path}")

        # Figure 3: Box plot comparison
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Performance Distribution Comparison', fontsize=16, fontweight='bold')

        for idx, (metric_key, metric_title) in enumerate(zip(metric_keys, metric_titles)):
            ax = axes[idx // 2, idx % 2]

            data_to_plot = [self.results[alg]['all_runs'][metric_key].values
                           for alg in algorithms]

            ax.boxplot(data_to_plot, labels=algorithms)
            ax.set_ylabel(metric_title, fontsize=11)
            ax.set_title(f'({chr(97+idx)}) {metric_title}', fontsize=11)
            ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        fig3_path = fig_dir / f"algorithm_comparison_boxes_{self.experiment_id}.png"
        plt.savefig(fig3_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Figure 3 saved: {fig3_path}")

        print(f"\n✓ All visualizations saved to: {fig_dir}")

    def run_complete_comparison(self, num_runs: int = 10):
        """
        Run complete comparison pipeline

        Args:
            num_runs: Number of experimental runs
        """
        print("\n" + "="*80)
        print(" "*15 + "ALGORITHM COMPARISON EXPERIMENT")
        print(" "*18 + "HGTM vs GBMA vs MMLMA vs MPFTM")
        print("="*80)

        start_time = time.time()

        try:
            # Run comparison experiment
            results = self.run_comparison_experiment(num_runs=num_runs)

            if not results:
                print("\n✗ Comparison failed - no results generated")
                return

            # Export to Excel
            self.export_to_excel()

            # Create visualizations
            self.create_comparison_visualizations()

            total_time = time.time() - start_time

            print("\n" + "="*80)
            print("✓ COMPARISON COMPLETED SUCCESSFULLY")
            print("="*80)
            print(f"Total execution time: {total_time:.2f}s")
            print(f"\nResults location: {self.output_dir.absolute()}")
            print("\nGenerated files:")
            print(f"  - Excel results: algorithm_comparison_{self.experiment_id}.xlsx")
            print(f"  - Visualizations: figures/ directory")
            print("\n" + "="*80)

        except Exception as e:
            print(f"\n✗ Comparison failed with error: {str(e)}")
            import traceback
            traceback.print_exc()


def main():
    """Main entry point for algorithm comparison"""
    print("Initializing Algorithm Comparison Experiment...")

    # Create comparison instance
    comparison = AlgorithmComparison(
        data_dir="data",
        output_dir="results"
    )

    # Run complete comparison (10 runs by default)
    comparison.run_complete_comparison(num_runs=10)


if __name__ == "__main__":
    main()
