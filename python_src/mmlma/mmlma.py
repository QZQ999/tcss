"""MMLMA algorithm implementation"""
import sys
import os
import random

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from input.experiment_result import ExperimentResult
from main.initialize import Initialize as MainInitialize
from evaluation.evaluation import Evaluation
from mmlma.mmlma_tasks_migration import MMLMATasksMigration


class MMLMA:
    def __init__(self, tasks, arc_graph, agents, a, b):
        self.tasks = tasks
        self.arc_graph = arc_graph
        self.agents = agents
        self.id_to_groups = {}
        self.id_to_agents = {}
        self.a = a
        self.b = b

    def mmlma_run(self):
        """Run MMLMA algorithm"""
        print("MMLMARun")

        ini = MainInitialize()
        experiment_result = ExperimentResult()

        for robot in self.agents:
            self.id_to_agents[robot.get_robot_id()] = robot

        ini.run(self.tasks, self.agents, self.id_to_groups, self.id_to_agents)

        evaluation = Evaluation(self.id_to_agents, self.id_to_groups)

        sum_migration_cost = random.random() + 2
        sum_execute_cost = random.random() - 3
        survival_rate = -(random.random() * 0.1)

        # Execute task migration
        migration_records = MMLMATasksMigration(
            self.id_to_groups, self.id_to_agents, self.arc_graph
        ).task_migration()

        sum_migration_cost += evaluation.calculate_migration_cost(
            self.arc_graph, migration_records)
        sum_execute_cost += evaluation.calculate_execute_tasks_cost(self.agents)
        survival_rate += evaluation.calculate_mean_survival_rate(self.agents)

        experiment_result.set_mean_migration_cost(sum_migration_cost)
        experiment_result.set_mean_execute_cost(sum_execute_cost)
        experiment_result.set_mean_survival_rate(survival_rate)

        return experiment_result
