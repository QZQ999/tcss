"""GBMA (Greedy-Based Migration Algorithm)"""
import sys
import random
sys.path.append('..')
from python_src.input.experiment_result import ExperimentResult
from python_src.main.initialize import Initialize
from python_src.evaluation.evaluation import Evaluation
from python_src.hgtm.finder_leader import FinderLeader
from .gbma_tasks_migration import GBMATasksMigration


class GBMA:
    """Greedy-Based Migration Algorithm"""

    def __init__(self, tasks, arc_graph, robots, a=0.1, b=0.9):
        """
        Initialize GBMA algorithm

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

    def gbma_run(self):
        """
        Execute GBMA algorithm

        Returns:
            ExperimentResult object containing performance metrics
        """
        print("GBMARun")

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

        # Leader selection
        self.leader_selection(self.id_to_groups, self.id_to_robots, self.arc_graph)

        # Execute task migration
        migration_records = GBMATasksMigration(
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

    def leader_selection(self, id_to_groups, id_to_robots, arc_graph):
        """
        Select leader for each group

        Args:
            id_to_groups: Dictionary mapping group ID to Group objects
            id_to_robots: Dictionary mapping robot ID to Agent objects
            arc_graph: NetworkX graph
        """
        finder = FinderLeader()

        # Find leaders for each group
        for group in id_to_groups.values():
            if group.get_leader() is None:
                leader = finder.find_leader(
                    group, id_to_robots, id_to_groups, arc_graph,
                    self.a, self.b
                )
                group.set_leader(leader)

        # Add edges between leader nodes
        group_ids = list(id_to_groups.keys())
        for group_id in group_ids:
            leader_id = id_to_groups[group_id].get_leader().get_robot_id()

            for to_group_id in group_ids:
                to_leader_id = id_to_groups[to_group_id].get_leader().get_robot_id()

                if group_id != to_group_id and not arc_graph.has_edge(leader_id, to_leader_id):
                    arc_graph.add_edge(leader_id, to_leader_id, weight=10)
