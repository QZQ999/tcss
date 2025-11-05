"""
Comprehensive Semiconductor Supply Chain Experiment

This script provides a complete analysis including:
1. Multiple algorithm comparison (HGTM vs. baselines)
2. Supply chain network theory analysis
3. Rich visualizations with supply chain meaning
4. Country/region dependency heatmaps
5. Critical node and vulnerability analysis
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
from typing import Dict, List

# Add python_src to path
sys.path.append('python_src')

# Import modules
from semiconductor_network_builder import SemiconductorNetworkBuilder
from supply_chain_analysis import SupplyChainAnalyzer
from baseline_algorithms import get_all_baseline_algorithms
from input.reader import Reader
from hgtm.hgtm import Hgtm
from evaluation.evaluation_extra_target import EvaluationExtraTarget


class ComprehensiveSupplyChainExperiment:
    """Complete experimental framework with theoretical analysis"""

    def __init__(self, data_dir: str = "data", output_dir: str = "results_comprehensive"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.builder = SemiconductorNetworkBuilder(data_dir=str(self.data_dir))
        self.experiment_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {}
        self.sc_analysis_results = None

    def setup_experiment(self):
        """Build network and generate inputs"""
        print("\n" + "="*70)
        print("STEP 1: Setup Experiment and Build Network")
        print("="*70)

        self.builder.build_complete_experiment(output_prefix="semiconductor")
        print("\n✓ Experiment setup completed")

    def run_supply_chain_analysis(self):
        """Run theoretical supply chain network analysis"""
        print("\n" + "="*70)
        print("STEP 2: Supply Chain Network Theory Analysis")
        print("="*70)

        # Create analyzer
        analyzer = SupplyChainAnalyzer(
            network=self.builder.network,
            providers_df=self.builder.providers_df,
            inputs_df=self.builder.inputs_df,
            provision_df=self.builder.provision_df,
            stages_df=self.builder.stages_df
        )

        # Add sequence data if available
        if hasattr(self.builder, 'sequence_df'):
            analyzer.sequence_df = self.builder.sequence_df

        # Run full analysis
        self.sc_analysis_results = analyzer.run_full_analysis()

        # Export results
        analyzer.export_results(
            self.sc_analysis_results,
            str(self.output_dir / f"supply_chain_analysis_{self.experiment_id}.json")
        )

        print("\n✓ Supply chain analysis completed")

    def run_algorithm_comparison(self, num_runs: int = 5, a: float = 0.1, b: float = 0.9):
        """
        Run multiple algorithms and compare performance.

        Supply Chain Metrics Meaning:
        - Execution Cost: Resource utilization efficiency (lower = better capacity usage)
        - Migration Cost: Supply chain reconfiguration cost (lower = less disruption)
        - Survival Rate: System resilience to disruptions (higher = more robust)
        - Target Optimization: Overall supply chain performance (lower = better)
        """
        print("\n" + "="*70)
        print("STEP 3: Multi-Algorithm Comparison")
        print("="*70)
        print(f"Running {num_runs} iterations for each algorithm...")

        task_file = "Task_semiconductor.txt"
        robot_file = "RobotsInformation_semiconductor.txt"
        graph_file = "Graph_semiconductor.txt"

        # Initialize reader once
        reader = Reader()

        # Storage for results
        all_algorithms_results = {}

        # Read input files
        print("\nLoading experiment data...")
        tasks = reader.read_file_to_tasks(task_file)
        robots_template = reader.read_file_to_robots(robot_file)
        arc_graph = reader.read_file_to_graph(graph_file)

        print(f"  - {len(tasks)} tasks")
        print(f"  - {len(robots_template)} agents")
        print(f"  - {arc_graph.number_of_edges()} edges")

        # Test algorithms
        algorithms_to_test = [
            ('HGTM', 'hgtm'),
            ('Random', 'random'),
            ('Greedy', 'greedy'),
            ('LoadBalance', 'load_balance'),
            ('NearestNeighbor', 'nearest')
        ]

        for algo_name, algo_type in algorithms_to_test:
            print(f"\n--- Testing {algo_name} Algorithm ---")
            algo_results = []

            for run_id in range(num_runs):
                # Deep copy robots for each run
                import copy
                robots = copy.deepcopy(robots_template)

                start_time = time.time()

                try:
                    if algo_type == 'hgtm':
                        # Run HGTM
                        hgtm = Hgtm(tasks, arc_graph, robots, a, b)
                        experiment_result = hgtm.hgtm_run()

                        mean_execute_cost = experiment_result.get_mean_execute_cost()
                        mean_migration_cost = experiment_result.get_mean_migration_cost()
                        mean_survival_rate = experiment_result.get_mean_survival_rate()

                    else:
                        # Run baseline algorithm
                        baseline_algos = get_all_baseline_algorithms(tasks, arc_graph, robots, a, b)
                        algo_map = {
                            'random': 0,
                            'greedy': 1,
                            'load_balance': 2,
                            'nearest': 3
                        }
                        selected_algo = baseline_algos[algo_map[algo_type]]
                        experiment_result = selected_algo.run()

                        mean_execute_cost = experiment_result.get_mean_execute_cost()
                        mean_migration_cost = experiment_result.get_mean_migration_cost()
                        mean_survival_rate = experiment_result.get_mean_survival_rate()

                    # Calculate statistics
                    evaluation_extra_target = EvaluationExtraTarget()
                    robot_capacity_std = evaluation_extra_target.calculate_robot_capacity_std(robots)
                    task_size_std = evaluation_extra_target.calculate_task_size_std(tasks)

                    # Calculate target optimization
                    target_opt = a * (mean_execute_cost + mean_migration_cost) - b * mean_survival_rate

                    result = {
                        'run_id': run_id + 1,
                        'algorithm': algo_name,
                        'meanExecuteCost': mean_execute_cost,
                        'meanMigrationCost': mean_migration_cost,
                        'meanSurvivalRate': mean_survival_rate,
                        'robotLoadStd': robot_capacity_std,
                        'taskSizeStd': task_size_std,
                        'targetOpt': target_opt,
                        'execution_time_ms': (time.time() - start_time) * 1000
                    }

                    algo_results.append(result)
                    print(f"  Run {run_id + 1}/{num_runs}: Target Opt = {target_opt:.4f}, Time = {result['execution_time_ms']:.0f}ms")

                except Exception as e:
                    print(f"  ✗ Run {run_id + 1} failed: {str(e)}")
                    continue

            if algo_results:
                all_algorithms_results[algo_name] = algo_results
                df_results = pd.DataFrame(algo_results)
                print(f"  ✓ {algo_name}: Avg Target Opt = {df_results['targetOpt'].mean():.4f} ± {df_results['targetOpt'].std():.4f}")

        self.results['algorithm_comparison'] = all_algorithms_results

        # Create comparison summary
        self._create_comparison_summary()

        print("\n✓ Algorithm comparison completed")

    def _create_comparison_summary(self):
        """Create summary table comparing all algorithms"""
        summary_data = []

        for algo_name, results in self.results['algorithm_comparison'].items():
            df = pd.DataFrame(results)

            summary_data.append({
                'Algorithm': algo_name,
                'Target Opt (mean)': df['targetOpt'].mean(),
                'Target Opt (std)': df['targetOpt'].std(),
                'Exec Cost (mean)': df['meanExecuteCost'].mean(),
                'Migr Cost (mean)': df['meanMigrationCost'].mean(),
                'Survival Rate (mean)': df['meanSurvivalRate'].mean(),
                'Load Std (mean)': df['robotLoadStd'].mean(),
                'Time (ms)': df['execution_time_ms'].mean()
            })

        self.comparison_summary = pd.DataFrame(summary_data)
        self.comparison_summary = self.comparison_summary.sort_values('Target Opt (mean)')

        print("\n" + "="*90)
        print("Algorithm Comparison Summary")
        print("="*90)
        print(self.comparison_summary.to_string(index=False))
        print("="*90)

    def export_to_excel(self, filename: str = None):
        """Export all results to Excel"""
        print("\n" + "="*70)
        print("STEP 4: Export Results to Excel")
        print("="*70)

        if filename is None:
            filename = f"comprehensive_experiment_{self.experiment_id}.xlsx"

        output_path = self.output_dir / filename

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Sheet 1: Algorithm Comparison Summary
            if hasattr(self, 'comparison_summary'):
                self.comparison_summary.to_excel(writer, sheet_name='Algorithm Comparison', index=False)

            # Sheet 2-N: Detailed results for each algorithm
            for algo_name, results in self.results.get('algorithm_comparison', {}).items():
                df = pd.DataFrame(results)
                sheet_name = f"{algo_name} Details"[:31]  # Excel sheet name limit
                df.to_excel(writer, sheet_name=sheet_name, index=False)

            # Sheet: Critical Nodes
            if self.sc_analysis_results:
                critical_nodes = pd.DataFrame(
                    self.sc_analysis_results['critical_nodes']['centrality_rankings'][:50]
                )
                critical_nodes.to_excel(writer, sheet_name='Critical Nodes', index=False)

            # Sheet: Market Concentration
            if self.sc_analysis_results:
                concentration_data = []
                for input_name, hhi in self.sc_analysis_results['market_concentration']['input_concentration'].items():
                    concentration_data.append({'Input': input_name, 'HHI': hhi})

                df_concentration = pd.DataFrame(concentration_data)
                df_concentration = df_concentration.sort_values('HHI', ascending=False)
                df_concentration.to_excel(writer, sheet_name='Market Concentration', index=False)

            # Sheet: Country Dependencies
            if self.sc_analysis_results:
                dep_data = []
                for rel in self.sc_analysis_results['country_dependencies']['critical_relationships']:
                    dep_data.append(rel)

                df_deps = pd.DataFrame(dep_data)
                df_deps.to_excel(writer, sheet_name='Country Dependencies', index=False)

        print(f"✓ Results exported to: {output_path}")

    def create_comprehensive_visualizations(self):
        """Create all visualizations with supply chain context"""
        print("\n" + "="*70)
        print("STEP 5: Create Comprehensive Visualizations")
        print("="*70)

        fig_dir = self.output_dir / "figures"
        fig_dir.mkdir(exist_ok=True)

        # Set style
        plt.style.use('seaborn-v0_8-paper')
        sns.set_palette("husl")

        # Figure 1: Algorithm Comparison
        self._create_algorithm_comparison_figure(fig_dir)

        # Figure 2: Country Dependency Heatmap
        self._create_country_dependency_heatmap(fig_dir)

        # Figure 3: Critical Nodes and Market Concentration
        self._create_critical_nodes_figure(fig_dir)

        # Figure 4: Supply Chain Resilience Dashboard
        self._create_resilience_dashboard(fig_dir)

        # Figure 5: Stage Analysis
        self._create_stage_analysis_figure(fig_dir)

        print(f"\n✓ All visualizations saved to: {fig_dir}")

    def _create_algorithm_comparison_figure(self, fig_dir):
        """Create algorithm comparison visualization"""
        if not hasattr(self, 'comparison_summary'):
            return

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Algorithm Performance Comparison\nSupply Chain Optimization Metrics',
                     fontsize=14, fontweight='bold')

        df = self.comparison_summary

        # Plot 1: Target Optimization
        ax = axes[0, 0]
        x_pos = np.arange(len(df))
        ax.bar(x_pos, df['Target Opt (mean)'], yerr=df['Target Opt (std)'],
               capsize=5, alpha=0.7, color='steelblue')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(df['Algorithm'], rotation=45, ha='right')
        ax.set_ylabel('Target Optimization Value')
        ax.set_title('(a) Overall Performance (Lower = Better)')
        ax.grid(True, alpha=0.3, axis='y')

        # Plot 2: Execution vs Migration Cost
        ax = axes[0, 1]
        width = 0.35
        x = np.arange(len(df))
        ax.bar(x - width/2, df['Exec Cost (mean)'], width, label='Execution Cost', alpha=0.8)
        ax.bar(x + width/2, df['Migr Cost (mean)'], width, label='Migration Cost', alpha=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(df['Algorithm'], rotation=45, ha='right')
        ax.set_ylabel('Cost')
        ax.set_title('(b) Cost Components Breakdown')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        # Plot 3: Survival Rate (Resilience)
        ax = axes[1, 0]
        ax.bar(x_pos, df['Survival Rate (mean)'], alpha=0.7, color='green')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(df['Algorithm'], rotation=45, ha='right')
        ax.set_ylabel('Survival Rate')
        ax.set_title('(c) Supply Chain Resilience (Higher = Better)')
        ax.set_ylim([0, 1.1])
        ax.grid(True, alpha=0.3, axis='y')

        # Plot 4: Load Balance
        ax = axes[1, 1]
        ax.bar(x_pos, df['Load Std (mean)'], alpha=0.7, color='orange')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(df['Algorithm'], rotation=45, ha='right')
        ax.set_ylabel('Load Standard Deviation')
        ax.set_title('(d) Load Distribution (Lower = Better Balance)')
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        fig_path = fig_dir / f"algorithm_comparison_{self.experiment_id}.png"
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Algorithm comparison figure saved")

    def _create_country_dependency_heatmap(self, fig_dir):
        """Create country-to-country dependency heatmap"""
        if not self.sc_analysis_results:
            return

        dep_matrix = self.sc_analysis_results['country_dependencies']['dependency_matrix']

        # Select top countries by total dependencies
        row_sums = dep_matrix.sum(axis=1) + dep_matrix.sum(axis=0)
        top_countries = row_sums.nlargest(20).index

        # Filter matrix
        matrix_subset = dep_matrix.loc[top_countries, top_countries]

        fig, ax = plt.subplots(figsize=(14, 12))

        sns.heatmap(matrix_subset, annot=False, fmt='.2f', cmap='YlOrRd',
                   center=0, square=True, linewidths=0.5, cbar_kws={"shrink": 0.8},
                   ax=ax)

        ax.set_title('Country-to-Country Supply Chain Dependencies\n' +
                    '(Row: Importer, Column: Exporter, Value: Dependency Strength)',
                    fontsize=13, fontweight='bold', pad=20)
        ax.set_xlabel('Exporting Country', fontsize=11, fontweight='bold')
        ax.set_ylabel('Importing Country', fontsize=11, fontweight='bold')

        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        plt.setp(ax.get_yticklabels(), rotation=0)

        plt.tight_layout()
        fig_path = fig_dir / f"country_dependencies_{self.experiment_id}.png"
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Country dependency heatmap saved")

    def _create_critical_nodes_figure(self, fig_dir):
        """Create critical nodes and market concentration figure"""
        if not self.sc_analysis_results:
            return

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Critical Nodes and Market Concentration Analysis',
                     fontsize=14, fontweight='bold')

        # Plot 1: Top Critical Nodes by Centrality
        ax = axes[0, 0]
        critical_nodes = pd.DataFrame(
            self.sc_analysis_results['critical_nodes']['centrality_rankings'][:15]
        )
        y_pos = np.arange(len(critical_nodes))
        ax.barh(y_pos, critical_nodes['combined_score'], alpha=0.7)
        ax.set_yticks(y_pos)
        ax.set_yticklabels([f"{row['provider_name'][:20]}\n({row['country']})"
                            for _, row in critical_nodes.iterrows()], fontsize=8)
        ax.set_xlabel('Combined Centrality Score')
        ax.set_title('(a) Top 15 Critical Nodes')
        ax.invert_yaxis()
        ax.grid(True, alpha=0.3, axis='x')

        # Plot 2: Bottleneck Nodes (High Betweenness)
        ax = axes[0, 1]
        bottlenecks = pd.DataFrame(
            self.sc_analysis_results['critical_nodes']['bottleneck_nodes'][:15]
        )
        y_pos = np.arange(len(bottlenecks))
        ax.barh(y_pos, bottlenecks['betweenness'], alpha=0.7, color='orange')
        ax.set_yticks(y_pos)
        ax.set_yticklabels([f"{row['provider_name'][:20]}\n({row['country']})"
                            for _, row in bottlenecks.iterrows()], fontsize=8)
        ax.set_xlabel('Betweenness Centrality')
        ax.set_title('(b) Top 15 Bottleneck Nodes')
        ax.invert_yaxis()
        ax.grid(True, alpha=0.3, axis='x')

        # Plot 3: Market Concentration (HHI) Distribution
        ax = axes[1, 0]
        hhi_values = list(self.sc_analysis_results['market_concentration']['input_concentration'].values())
        ax.hist(hhi_values, bins=20, alpha=0.7, color='green', edgecolor='black')
        ax.axvline(2500, color='red', linestyle='--', linewidth=2, label='High Concentration Threshold')
        ax.set_xlabel('HHI Index')
        ax.set_ylabel('Number of Inputs')
        ax.set_title('(c) Market Concentration Distribution')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        # Plot 4: Stage Concentration
        ax = axes[1, 1]
        stage_conc = self.sc_analysis_results['market_concentration']['stage_concentration']
        stages = list(stage_conc.keys())
        hhi_vals = list(stage_conc.values())
        colors = ['red' if v > 2500 else 'green' for v in hhi_vals]
        ax.bar(range(len(stages)), hhi_vals, color=colors, alpha=0.7)
        ax.set_xticks(range(len(stages)))
        ax.set_xticklabels(stages, rotation=45, ha='right')
        ax.set_ylabel('HHI Index')
        ax.set_title('(d) Concentration by Supply Chain Stage')
        ax.axhline(2500, color='gray', linestyle='--', linewidth=1, alpha=0.5)
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        fig_path = fig_dir / f"critical_nodes_concentration_{self.experiment_id}.png"
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Critical nodes and concentration figure saved")

    def _create_resilience_dashboard(self, fig_dir):
        """Create supply chain resilience dashboard"""
        if not self.sc_analysis_results:
            return

        resilience = self.sc_analysis_results['resilience']

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Supply Chain Resilience and Vulnerability Analysis',
                     fontsize=14, fontweight='bold')

        # Plot 1: Resilience Score Gauge
        ax = axes[0, 0]
        score = resilience['resilience_score']
        theta = np.linspace(0, np.pi, 100)
        r = np.ones_like(theta)
        ax = plt.subplot(2, 2, 1, projection='polar')
        ax.plot(theta, r, 'k-', linewidth=2)
        ax.fill_between(theta[:33], 0, r[:33], alpha=0.3, color='red')
        ax.fill_between(theta[33:66], 0, r[33:66], alpha=0.3, color='yellow')
        ax.fill_between(theta[66:], 0, r[66:], alpha=0.3, color='green')
        ax.arrow(0, 0, score * np.pi, 0.7, width=0.05, head_width=0.15, head_length=0.1,
                fc='blue', ec='blue')
        ax.set_ylim(0, 1)
        ax.set_theta_zero_location('W')
        ax.set_theta_direction(1)
        ax.set_xticks([0, np.pi/2, np.pi])
        ax.set_xticklabels(['1.0\n(High)', '0.5\n(Medium)', '0.0\n(Low)'])
        ax.set_yticks([])
        ax.set_title(f'(a) Resilience Score: {score:.3f}', pad=20)

        # Plot 2: Single Points of Failure
        ax = axes[0, 1]
        spof = resilience['single_point_failures']
        if len(spof) > 0:
            spof_df = pd.DataFrame(spof[:10])
            countries = spof_df['country'].value_counts()
            ax.pie(countries.values, labels=countries.index, autopct='%1.1f%%',
                  startangle=90)
            ax.set_title('(b) Single Points of Failure by Country')
        else:
            ax.text(0.5, 0.5, 'No Single Points of Failure', ha='center', va='center')
            ax.set_title('(b) Single Points of Failure')

        # Plot 3: Node Removal Impact
        ax = axes[1, 0]
        removal_impact = resilience['node_removal_impact'][:15]
        impact_df = pd.DataFrame(removal_impact)
        colors = ['red' if x else 'green' for x in impact_df['is_critical']]
        y_pos = np.arange(len(impact_df))
        ax.barh(y_pos, impact_df['connectivity_impact'], color=colors, alpha=0.7)
        ax.set_yticks(y_pos)
        ax.set_yticklabels([f"{row['provider_name'][:15]}" for _, row in impact_df.iterrows()],
                           fontsize=8)
        ax.set_xlabel('Connectivity Impact')
        ax.set_title('(c) Critical Node Removal Impact')
        ax.invert_yaxis()
        ax.grid(True, alpha=0.3, axis='x')

        # Plot 4: Path Redundancy
        ax = axes[1, 1]
        avg_redundancy = resilience['alternative_paths']['average_redundancy']
        categories = ['Current\nRedundancy', 'Ideal\nRedundancy']
        values = [min(avg_redundancy, 5), 5]
        colors_bar = ['orange', 'green']
        ax.bar(categories, values, color=colors_bar, alpha=0.7)
        ax.set_ylabel('Average Number of Paths')
        ax.set_title('(d) Supply Path Redundancy')
        ax.set_ylim([0, 6])
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        fig_path = fig_dir / f"resilience_dashboard_{self.experiment_id}.png"
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Resilience dashboard saved")

    def _create_stage_analysis_figure(self, fig_dir):
        """Create supply chain stage analysis figure"""
        if not self.sc_analysis_results:
            return

        stage_stats = self.sc_analysis_results['stage_analysis']['stage_statistics']

        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.suptitle('Supply Chain Stage Analysis',
                     fontsize=14, fontweight='bold')

        stages = list(stage_stats.keys())

        # Plot 1: Number of Inputs per Stage
        ax = axes[0]
        inputs = [stage_stats[s]['num_inputs'] for s in stages]
        ax.bar(range(len(stages)), inputs, alpha=0.7, color='steelblue')
        ax.set_xticks(range(len(stages)))
        ax.set_xticklabels(stages, rotation=45, ha='right')
        ax.set_ylabel('Number of Inputs')
        ax.set_title('(a) Inputs by Stage')
        ax.grid(True, alpha=0.3, axis='y')

        # Plot 2: Number of Providers per Stage
        ax = axes[1]
        providers = [stage_stats[s]['num_providers'] for s in stages]
        ax.bar(range(len(stages)), providers, alpha=0.7, color='green')
        ax.set_xticks(range(len(stages)))
        ax.set_xticklabels(stages, rotation=45, ha='right')
        ax.set_ylabel('Number of Providers')
        ax.set_title('(b) Providers by Stage')
        ax.grid(True, alpha=0.3, axis='y')

        # Plot 3: Number of Countries per Stage
        ax = axes[2]
        countries = [stage_stats[s]['num_countries'] for s in stages]
        ax.bar(range(len(stages)), countries, alpha=0.7, color='orange')
        ax.set_xticks(range(len(stages)))
        ax.set_xticklabels(stages, rotation=45, ha='right')
        ax.set_ylabel('Number of Countries')
        ax.set_title('(c) Geographic Diversity by Stage')
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        fig_path = fig_dir / f"stage_analysis_{self.experiment_id}.png"
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Stage analysis figure saved")

    def run_complete_experiment(self, num_runs: int = 5):
        """Run complete comprehensive experiment"""
        print("\n" + "="*80)
        print(" "*15 + "COMPREHENSIVE SUPPLY CHAIN EXPERIMENT")
        print(" "*10 + "Theory-Driven Analysis + Algorithm Comparison")
        print("="*80)

        start_time = time.time()

        try:
            # Step 1: Setup
            self.setup_experiment()

            # Step 2: Supply Chain Analysis
            self.run_supply_chain_analysis()

            # Step 3: Algorithm Comparison
            self.run_algorithm_comparison(num_runs=num_runs)

            # Step 4: Export to Excel
            self.export_to_excel()

            # Step 5: Create Visualizations
            self.create_comprehensive_visualizations()

            total_time = time.time() - start_time

            print("\n" + "="*80)
            print("✓ COMPREHENSIVE EXPERIMENT COMPLETED SUCCESSFULLY")
            print("="*80)
            print(f"Total execution time: {total_time:.2f}s")
            print(f"\nResults location: {self.output_dir.absolute()}")
            print("\nGenerated outputs:")
            print(f"  - Excel: comprehensive_experiment_{self.experiment_id}.xlsx")
            print(f"  - JSON: supply_chain_analysis_{self.experiment_id}.json")
            print(f"  - Figures: figures/ directory (5 comprehensive visualizations)")
            print("\n" + "="*80)

        except Exception as e:
            print(f"\n✗ Experiment failed: {str(e)}")
            import traceback
            traceback.print_exc()


def main():
    """Main entry point"""
    experiment = ComprehensiveSupplyChainExperiment(
        data_dir="data",
        output_dir="results_comprehensive"
    )

    # Run with 5 iterations per algorithm (adjust as needed)
    experiment.run_complete_experiment(num_runs=5)


if __name__ == "__main__":
    main()
