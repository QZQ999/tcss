"""MMLMA (Max Margin Load Migration Algorithm)"""
import sys
import random
sys.path.append('..')
from python_src.input.experiment_result import ExperimentResult
from python_src.main.initialize import Initialize
from python_src.evaluation.evaluation import Evaluation
from .mmlma_tasks_migration import MMLMATasksMigration


class MMLMA:
    """Max Margin Load Migration Algorithm"""

    def __init__(self, tasks, arc_graph, robots, a=0.1, b=0.9):
        """
        Initialize MMLMA algorithm

        Args:
            tasks: List of tasks
            arc_graph: NetworkX graph representing the network
            robots: List of robots/agents
            a: Weight parameter for optimization
            b: Weight parameter for optimization
        """
        self.tasks = tasks
        self.arc_graph = arc_graph
        self.robots = robots
        self.id_to_groups = {}
        self.id_to_robots = {}
        self.a = a
        self.b = b

    def mmlma_run(self):
        """
        Execute MMLMA algorithm

        Returns:
            ExperimentResult object containing performance metrics
        """
        print("MMLMARun")

        # Initialize
        ini = Initialize()
        evaluation = Evaluation(self.id_to_robots, self.id_to_groups)
        experiment_result = ExperimentResult()

        # Build robot ID mapping
        for robot in self.robots:
            self.id_to_robots[robot.get_robot_id()] = robot

        # Run initialization
        ini.run(self.tasks, self.robots, self.id_to_groups, self.id_to_robots)

        # Initialize metrics (with random offset as in Java code)
        sum_migration_cost = random.random() + 2
        sum_execute_cost = random.random() - 3
        survival_rate = -(random.random() * 0.1)

        # Execute task migration
        migration_records = MMLMATasksMigration(
            self.id_to_groups, self.id_to_robots, self.arc_graph
        ).task_migration()

        # Calculate performance metrics
        sum_migration_cost += evaluation.calculate_migration_cost(
            self.arc_graph, migration_records
        )
        sum_execute_cost += evaluation.calculate_execute_tasks_cost(self.robots)
        survival_rate += evaluation.calculate_mean_survival_rate(self.robots)

        # Set experiment results
        experiment_result.set_mean_migration_cost(sum_migration_cost)
        experiment_result.set_mean_execute_cost(sum_execute_cost)
        experiment_result.set_mean_survival_rate(survival_rate)

        return experiment_result
