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

        # Build robot and group ID mappings from already-initialized robots
        for robot in self.robots:
            rid = robot.get_robot_id()
            gid = robot.get_group_id()
            self.id_to_robots[rid] = robot

            if gid not in self.id_to_groups:
                from python_src.input.group import Group
                group = Group()
                group.set_group_id(gid)
                group.set_robot_id_in_group(set())
                group.set_group_capacity(0.0)
                group.set_group_load(0.0)
                self.id_to_groups[gid] = group

            # Add robot to group
            self.id_to_groups[gid].get_robot_id_in_group().add(rid)
            self.id_to_groups[gid].set_group_capacity(
                self.id_to_groups[gid].get_group_capacity() + robot.get_capacity()
            )
            self.id_to_groups[gid].set_group_load(
                self.id_to_groups[gid].get_group_load() + robot.get_load()
            )

        # Create evaluation with proper mappings
        evaluation = Evaluation(self.id_to_robots, self.id_to_groups)
        experiment_result = ExperimentResult()

        # Execute task migration
        migration_records = MMLMATasksMigration(
            self.id_to_groups, self.id_to_robots, self.arc_graph
        ).task_migration()

        # Calculate performance metrics
        sum_migration_cost = evaluation.calculate_migration_cost(
            self.arc_graph, migration_records
        )
        sum_execute_cost = evaluation.calculate_execute_tasks_cost(self.robots)
        survival_rate = evaluation.calculate_mean_survival_rate(self.robots)

        # Set experiment results
        experiment_result.set_mean_migration_cost(sum_migration_cost)
        experiment_result.set_mean_execute_cost(sum_execute_cost)
        experiment_result.set_mean_survival_rate(survival_rate)

        return experiment_result
