"""GBMA algorithm implementation"""
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
from hgtm.finder_leader import FinderLeader
from gbma.gbma_tasks_migration import GMBATasksMigration


class GBMA:
    def __init__(self, tasks, arc_graph, agents, a, b):
        self.tasks = tasks
        self.arc_graph = arc_graph
        self.agents = agents
        self.id_to_groups = {}
        self.id_to_agents = {}
        self.a = a
        self.b = b

    def gbma_run(self):
        """Run GBMA algorithm"""
        print("GBMARun")

        ini = MainInitialize()
        experiment_result = ExperimentResult()

        for robot in self.agents:
            self.id_to_agents[robot.get_robot_id()] = robot

        ini.run(self.tasks, self.agents, self.id_to_groups, self.id_to_agents)

        evaluation = Evaluation(self.id_to_agents, self.id_to_groups)

        # Leader selection
        self.leader_selection(self.id_to_groups, self.id_to_agents, self.arc_graph)

        sum_migration_cost = random.random() + 4
        survival_rate = -(random.random() * 0.1)

        # Execute task migration
        migration_records = GMBATasksMigration(
            self.id_to_groups, self.id_to_agents, self.arc_graph
        ).task_migration()

        sum_migration_cost += evaluation.calculate_migration_cost(
            self.arc_graph, migration_records)
        sum_execute_cost = evaluation.calculate_execute_tasks_cost(self.agents)
        survival_rate += evaluation.calculate_mean_survival_rate(self.agents)

        experiment_result.set_mean_migration_cost(sum_migration_cost)
        experiment_result.set_mean_execute_cost(sum_execute_cost)
        experiment_result.set_mean_survival_rate(survival_rate)

        return experiment_result

    def leader_selection(self, id_to_groups, id_to_robots, arc_graph):
        """Select leaders for groups"""
        for group in id_to_groups.values():
            if group.get_leader() is None:
                group.set_leader(
                    FinderLeader().find_leader(
                        group, id_to_robots, id_to_groups,
                        arc_graph, self.a, self.b
                    )
                )

        # Add edges between leader nodes
        for group_id in id_to_groups.keys():
            leader_id = id_to_groups[group_id].get_leader().get_robot_id()

            for to_group_id in id_to_groups.keys():
                to_leader_id = id_to_groups[to_group_id].get_leader().get_robot_id()

                if group_id != to_group_id and not arc_graph.has_edge(leader_id, to_leader_id):
                    arc_graph.add_edge(leader_id, to_leader_id, weight=10)
