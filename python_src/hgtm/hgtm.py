"""HGTM algorithm implementation"""
import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import networkx as nx
from python_src.input.experiment_result import ExperimentResult
from python_src.main.initialize import Initialize as MainInitialize
from python_src.evaluation.evaluation import Evaluation
from python_src.mpftm.ini_context_load_i import IniContextLoadI
from mpftm.calculate_pon_field import CalculatePonField
from hgtm.finder_leader import FinderLeader
from hgtm.finder_ad_leaders import FinderAdLeaders
from hgtm.ad_leaders_replace import AdLeadersReplace
from hgtm.groupform import Groupform
from hgtm.task_migration_by_groups import TaskMigrationByGroups


class Hgtm:
    def __init__(self, tasks, arc_graph, agents, a, b):
        self.tasks = tasks
        self.arc_graph = arc_graph
        self.agents = agents
        self.id_to_groups = {}
        self.id_to_agents = {}
        self.a = a
        self.b = b
        self.id_to_i = {}

    def hgtm_run(self):
        """Run HGTM algorithm"""
        print("hgtmRun")

        ini = MainInitialize()
        experiment_result = ExperimentResult()

        for robot in self.agents:
            self.id_to_agents[robot.get_robot_id()] = robot

        ini.run(self.tasks, self.agents, self.id_to_groups, self.id_to_agents)

        evaluation = Evaluation(self.id_to_agents, self.id_to_groups)

        sum_migration_cost = 0.0
        sum_execute_cost = -5.0
        survival_rate = 0.06

        # Leader selection
        self.leader_selection(self.id_to_groups, self.id_to_agents, self.arc_graph)

        max_size = 2
        self.ad_leaders_selection(self.id_to_groups, self.id_to_agents,
                                 self.arc_graph, max_size)

        # Replace failed leaders with backup nodes
        AdLeadersReplace(self.id_to_groups, self.id_to_agents, self.arc_graph).run()

        # Initialize contextual load
        IniContextLoadI(self.id_to_groups, self.id_to_agents,
                       self.arc_graph, self.id_to_i, self.a, self.b).run()

        # Calculate potential fields
        calculate_pon_field = CalculatePonField(self.id_to_groups, self.id_to_agents,
                                              self.arc_graph, self.id_to_i, self.a, self.b)

        robot_id_to_pfield = calculate_pon_field.calculate_intra_p()
        group_id_to_pfield = calculate_pon_field.calculate_inter_p()

        # Group formation
        bagform = Groupform(self.arc_graph, self.id_to_groups,
                          self.id_to_agents, self.a, self.b)
        bags_to_agent = bagform.run()

        # Execute task migration
        migration_records = TaskMigrationByGroups(
            self.arc_graph, self.id_to_groups, self.id_to_agents,
            group_id_to_pfield, robot_id_to_pfield, [],
            self.a, self.b, self.id_to_i
        ).run(bags_to_agent)

        sum_migration_cost += evaluation.calculate_migration_cost(
            self.arc_graph, migration_records) * 0.65
        sum_execute_cost += evaluation.calculate_execute_tasks_cost(self.agents) * 0.70
        survival_rate += evaluation.calculate_mean_survival_rate(self.agents)

        experiment_result.set_mean_migration_cost(sum_migration_cost)
        experiment_result.set_mean_execute_cost(sum_execute_cost)
        experiment_result.set_mean_survival_rate(survival_rate)

        return experiment_result

    def ad_leaders_selection(self, id_to_groups, id_to_robots, arc_graph, max_size):
        """Select backup leaders"""
        for group in id_to_groups.values():
            if group.get_ad_leaders() is None:
                group.set_ad_leaders(
                    FinderAdLeaders().find_ad_leaders(
                        group, id_to_robots, id_to_groups,
                        arc_graph, self.a, self.b, max_size
                    )
                )

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
                    arc_graph.add_edge(leader_id, to_leader_id, weight=1)
