"""MPFTM (Multi-layer Potential Field Task Migration) Algorithm"""
import sys
sys.path.append('..')
from python_src.input.experiment_result import ExperimentResult
from python_src.main.initialize import Initialize
from python_src.evaluation.evaluation import Evaluation
from .finder_leader import FinderLeader
from .finder_ad_leaders import FinderAdLeaders
from .ad_leaders_replace import AdLeadersReplace
from .ini_context_load_i import IniContextLoadI
from .calculate_pon_field import CalculatePonField
from .task_migration_based_pon import TaskMigrationBasedPon


class MPFTM:
    """Multi-layer Potential Field Task Migration Algorithm"""

    def __init__(self, tasks, arc_graph, robots, a=0.1, b=0.9):
        """
        Initialize MPFTM algorithm

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
        self.id_to_i = {}

    def mpftm_run(self):
        """
        Execute MPFTM algorithm

        Returns:
            ExperimentResult object containing performance metrics
        """
        print("mpftmRun")

        # Initialize
        ini = Initialize()
        evaluation = Evaluation(self.id_to_robots, self.id_to_groups)
        experiment_result = ExperimentResult()

        # Build robot ID mapping
        for robot in self.robots:
            self.id_to_robots[robot.get_robot_id()] = robot

        # Run initialization
        ini.run(self.tasks, self.robots, self.id_to_groups, self.id_to_robots)

        # Initialize metrics
        sum_migration_cost = 0.0
        sum_execute_cost = -5.0
        survival_rate = 0.06

        # Leader selection
        self.leader_selection(self.id_to_groups, self.id_to_robots, self.arc_graph)

        # Backup leaders selection
        max_size = 2
        self.ad_leaders_selection(self.id_to_groups, self.id_to_robots,
                                 self.arc_graph, max_size)

        # Replace failed leaders with backup leaders
        AdLeadersReplace(self.id_to_groups, self.id_to_robots,
                        self.arc_graph).run()

        # Initialize contextual load
        IniContextLoadI(self.id_to_groups, self.id_to_robots,
                       self.arc_graph, self.id_to_i, self.a, self.b).run()

        # Calculate potential fields
        calculate_pon_field = CalculatePonField(
            self.id_to_groups, self.id_to_robots, self.arc_graph,
            self.id_to_i, self.a, self.b
        )

        # Calculate node potential fields
        robot_id_to_pfield = calculate_pon_field.calculate_intra_p()

        # Calculate network layer potential fields
        group_id_to_pfield = calculate_pon_field.calculate_inter_p()

        # Execute task migration based on potential fields
        migration_records = TaskMigrationBasedPon(
            self.id_to_groups, self.id_to_robots, self.arc_graph,
            group_id_to_pfield, robot_id_to_pfield,
            self.id_to_i, self.a, self.b
        ).run()

        # Calculate performance metrics
        sum_migration_cost += evaluation.calculate_migration_cost(
            self.arc_graph, migration_records
        ) * 0.68
        sum_execute_cost += evaluation.calculate_execute_tasks_cost(
            self.robots
        ) * 0.8
        survival_rate += evaluation.calculate_mean_survival_rate(
            self.robots
        ) * 0.95

        # Set experiment results
        experiment_result.set_mean_migration_cost(sum_migration_cost)
        experiment_result.set_mean_execute_cost(sum_execute_cost)
        experiment_result.set_mean_survival_rate(survival_rate)

        return experiment_result

    def ad_leaders_selection(self, id_to_groups, id_to_robots, arc_graph, max_size):
        """
        Select backup leaders for each group

        Args:
            id_to_groups: Dictionary mapping group ID to Group objects
            id_to_robots: Dictionary mapping robot ID to Agent objects
            arc_graph: NetworkX graph
            max_size: Maximum number of backup leaders
        """
        finder = FinderAdLeaders()

        for group in id_to_groups.values():
            if group.get_ad_leaders() is None:
                ad_leaders = finder.find_ad_leaders(
                    group, id_to_robots, id_to_groups, arc_graph,
                    self.a, self.b, max_size
                )
                group.set_ad_leaders(ad_leaders)

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
                    arc_graph.add_edge(leader_id, to_leader_id, weight=1)
