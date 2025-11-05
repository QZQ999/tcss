"""
Additional Algorithm Implementations for Comparison
Converted from Java to Python

This module includes:
1. GBMA (Group-Based Migration Algorithm) - Path-based greedy migration
2. MMLMA (Multi-level Load Migration Algorithm) - Capacity-ratio based migration
3. MPFTM (Multi-robot Potential Field Task Migration) - Potential field guided migration

These algorithms provide additional baselines for comparing HGTM performance.
"""

import sys
sys.path.append('python_src')

import networkx as nx
import copy
from typing import List, Dict, Tuple
from input.agent import Agent
from input.task import Task
from input.group import Group
from input.experiment_result import ExperimentResult
from input.migration_record import MigrationRecord
from hgtm.finder_leader import FinderLeader
from hgtm.finder_ad_leaders import FinderAdLeaders
from hgtm.ad_leaders_replace import AdLeadersReplace
from mpftm.ini_context_load_i import IniContextLoadI
from mpftm.calculate_pon_field import CalculatePonField
from main.initialize import Initialize


class GBMA:
    """
    Group-Based Migration Algorithm (GBMA)

    Strategy: For faulty agents, migrate tasks to the nearest non-faulty agent
    within the same group based on shortest path distance.

    Key Features:
    - Group-aware migration (tasks stay within group)
    - Shortest path based greedy selection
    - Simple and efficient

    Supply Chain Meaning:
    - Represents local supply chain adjustment within same region/organization
    - Minimizes logistics cost (shortest distance)
    - Preserves organizational boundaries
    """

    def __init__(self, tasks: List[Task], graph: nx.Graph, agents: List[Agent],
                 a: float = 0.1, b: float = 0.9, name: str = "GBMA"):
        self.tasks = tasks
        self.graph = graph
        self.agents = agents
        self.a = a
        self.b = b
        self.name = name

        # Create ID mappings
        self.id_to_agents = {agent.get_robot_id(): agent for agent in agents}
        self.id_to_groups = {}

    def run(self) -> ExperimentResult:
        """Run GBMA algorithm"""
        print(f"Running {self.name}...")

        # Initialize
        initialize = Initialize()
        initialize.run(self.tasks, self.agents, self.id_to_groups, self.id_to_agents)

        # Leader selection
        self._leader_selection()

        # Execute task migration
        migration_records = self._task_migration()

        # Evaluate
        result = self._evaluate(migration_records)

        return result

    def _leader_selection(self):
        """Select leaders for each group"""
        finder = FinderLeader()

        for group in self.id_to_groups.values():
            if group.get_leader() is None:
                leader = finder.find_leader(group, self.id_to_agents,
                                          self.id_to_groups, self.graph,
                                          self.a, self.b)
                group.set_leader(leader)

        # Add edges between leaders
        for group_id in self.id_to_groups.keys():
            leader_id = self.id_to_groups[group_id].get_leader().get_robot_id()

            for to_group_id in self.id_to_groups.keys():
                to_leader_id = self.id_to_groups[to_group_id].get_leader().get_robot_id()

                if group_id != to_group_id and not self.graph.has_edge(leader_id, to_leader_id):
                    self.graph.add_edge(leader_id, to_leader_id, weight=10.0)

    def _task_migration(self) -> List[MigrationRecord]:
        """Execute task migration for faulty agents"""
        records = []

        for robot_id, robot in self.id_to_agents.items():
            if robot.get_fault_a() == 1:  # Faulty agent
                tasks_to_migrate = list(robot.get_tasks_list())

                for task in tasks_to_migrate:
                    # Find nearest non-faulty agent in same group
                    target_robot = self._greedy_find_by_path(robot)

                    if target_robot is not None:
                        # Execute migration
                        self._execute_migration(robot, target_robot, task)

                        # Record migration
                        record = MigrationRecord()
                        record.set_from_robot_id(robot_id)
                        record.set_to_robot_id(target_robot.get_robot_id())
                        records.append(record)

        return records

    def _greedy_find_by_path(self, faulty_robot: Agent) -> Agent:
        """Find nearest non-faulty agent in same group by shortest path"""
        min_distance = float('inf')
        best_robot = None

        faulty_id = faulty_robot.get_robot_id()
        faulty_group = faulty_robot.get_group_id()

        # Check neighbors
        if not self.graph.has_node(faulty_id):
            return None

        for neighbor in self.graph.neighbors(faulty_id):
            if neighbor in self.id_to_agents:
                target_robot = self.id_to_agents[neighbor]

                # Same group and not faulty
                if (target_robot.get_group_id() == faulty_group and
                    target_robot.get_fault_a() != 1):

                    try:
                        distance = nx.shortest_path_length(
                            self.graph, faulty_id, neighbor, weight='weight'
                        )

                        if distance < min_distance:
                            min_distance = distance
                            best_robot = target_robot
                    except nx.NetworkXNoPath:
                        continue

        return best_robot

    def _execute_migration(self, from_robot: Agent, to_robot: Agent, task: Task):
        """Execute task migration between agents"""
        if from_robot is None or to_robot is None or task is None:
            return

        # Update from_robot
        tasks_list = from_robot.get_tasks_list()
        tasks_list.remove(task)
        from_robot.set_tasks_list(tasks_list)
        from_robot.set_load(from_robot.get_load() - task.get_size())

        # Update to_robot
        to_tasks = to_robot.get_tasks_list()
        if to_tasks is None:
            to_tasks = []
        to_tasks.append(task)
        to_robot.set_tasks_list(to_tasks)
        to_robot.set_load(to_robot.get_load() + task.get_size())

        # Update group loads if cross-group
        if from_robot.get_group_id() != to_robot.get_group_id():
            from_group = self.id_to_groups.get(from_robot.get_group_id())
            to_group = self.id_to_groups.get(to_robot.get_group_id())

            if from_group:
                from_group.set_group_load(from_group.get_group_load() - task.get_size())
            if to_group:
                to_group.set_group_load(to_group.get_group_load() + task.get_size())

    def _evaluate(self, migration_records: List) -> ExperimentResult:
        """Evaluate the assignment"""
        result = ExperimentResult()

        # Calculate execution cost
        exec_cost = 0.0
        for agent in self.agents:
            if agent.get_capacity() > 0:
                exec_cost += agent.get_load() / agent.get_capacity()
        exec_cost /= len(self.agents)

        # Calculate migration cost
        migr_cost = 0.0
        for record in migration_records:
            from_id = record.get_from_robot_id()
            to_id = record.get_to_robot_id()

            if (self.graph.has_node(from_id) and self.graph.has_node(to_id)):
                try:
                    path_length = nx.shortest_path_length(
                        self.graph, from_id, to_id, weight='weight'
                    )
                    migr_cost += path_length
                except:
                    migr_cost += 10.0  # Default cost if no path

        if len(migration_records) > 0:
            migr_cost /= len(migration_records)

        # Calculate survival rate
        survival_rate = 0.0
        for agent in self.agents:
            rate = (1 - agent.get_fault_a()) * (1 - agent.get_fault_o())
            survival_rate += rate
        survival_rate /= len(self.agents)

        result.set_mean_execute_cost(exec_cost)
        result.set_mean_migration_cost(migr_cost)
        result.set_mean_survival_rate(survival_rate)

        return result


class MMLMA:
    """
    Multi-level Load Migration Algorithm (MMLMA)

    Strategy: For faulty agents, migrate tasks to the agent with highest
    capacity/load ratio (most available capacity) within the same group.

    Key Features:
    - Group-aware migration
    - Capacity-ratio based greedy selection
    - Load balancing focused

    Supply Chain Meaning:
    - Represents resource utilization optimization
    - Prioritizes suppliers with most available capacity
    - Balances workload within organizational boundaries
    """

    def __init__(self, tasks: List[Task], graph: nx.Graph, agents: List[Agent],
                 a: float = 0.1, b: float = 0.9, name: str = "MMLMA"):
        self.tasks = tasks
        self.graph = graph
        self.agents = agents
        self.a = a
        self.b = b
        self.name = name

        self.id_to_agents = {agent.get_robot_id(): agent for agent in agents}
        self.id_to_groups = {}

    def run(self) -> ExperimentResult:
        """Run MMLMA algorithm"""
        print(f"Running {self.name}...")

        # Initialize
        initialize = Initialize()
        initialize.run(self.tasks, self.agents, self.id_to_groups, self.id_to_agents)

        # Execute task migration
        migration_records = self._task_migration()

        # Evaluate
        result = self._evaluate(migration_records)

        return result

    def _task_migration(self) -> List[MigrationRecord]:
        """Execute task migration for faulty agents"""
        records = []

        for robot_id, robot in self.id_to_agents.items():
            if robot.get_fault_a() == 1:  # Faulty agent
                tasks_to_migrate = list(robot.get_tasks_list())

                for task in tasks_to_migrate:
                    # Find agent with highest capacity ratio in same group
                    target_robot = self._greedy_find_by_capacity_ratio(robot)

                    if target_robot is not None:
                        # Execute migration
                        self._execute_migration(robot, target_robot, task)

                        # Record migration
                        record = MigrationRecord()
                        record.set_from_robot_id(robot_id)
                        record.set_to_robot_id(target_robot.get_robot_id())
                        records.append(record)

        return records

    def _greedy_find_by_capacity_ratio(self, faulty_robot: Agent) -> Agent:
        """Find agent with highest capacity/load ratio in same group"""
        max_ratio = float('-inf')
        best_robot = None

        faulty_id = faulty_robot.get_robot_id()
        faulty_group = faulty_robot.get_group_id()

        # Check neighbors
        if not self.graph.has_node(faulty_id):
            return None

        for neighbor in self.graph.neighbors(faulty_id):
            if neighbor in self.id_to_agents:
                target_robot = self.id_to_agents[neighbor]

                # Same group and not faulty
                if (target_robot.get_group_id() == faulty_group and
                    target_robot.get_fault_a() != 1):

                    # Calculate capacity ratio (capacity / load)
                    # Higher ratio means more available capacity
                    load = target_robot.get_load()
                    if load > 0:
                        ratio = target_robot.get_capacity() / load
                    else:
                        ratio = float('inf')  # Empty agent

                    if ratio > max_ratio:
                        max_ratio = ratio
                        best_robot = target_robot

        return best_robot

    def _execute_migration(self, from_robot: Agent, to_robot: Agent, task: Task):
        """Execute task migration between agents"""
        if from_robot is None or to_robot is None or task is None:
            return

        # Update from_robot
        tasks_list = from_robot.get_tasks_list()
        tasks_list.remove(task)
        from_robot.set_tasks_list(tasks_list)
        from_robot.set_load(from_robot.get_load() - task.get_size())

        # Update to_robot
        to_tasks = to_robot.get_tasks_list()
        if to_tasks is None:
            to_tasks = []
        to_tasks.append(task)
        to_robot.set_tasks_list(to_tasks)
        to_robot.set_load(to_robot.get_load() + task.get_size())

        # Update group loads if cross-group
        if from_robot.get_group_id() != to_robot.get_group_id():
            from_group = self.id_to_groups.get(from_robot.get_group_id())
            to_group = self.id_to_groups.get(to_robot.get_group_id())

            if from_group:
                from_group.set_group_load(from_group.get_group_load() - task.get_size())
            if to_group:
                to_group.set_group_load(to_group.get_group_load() + task.get_size())

    def _evaluate(self, migration_records: List) -> ExperimentResult:
        """Evaluate the assignment"""
        result = ExperimentResult()

        # Calculate execution cost
        exec_cost = 0.0
        for agent in self.agents:
            if agent.get_capacity() > 0:
                exec_cost += agent.get_load() / agent.get_capacity()
        exec_cost /= len(self.agents)

        # Calculate migration cost
        migr_cost = 0.0
        for record in migration_records:
            from_id = record.get_from_robot_id()
            to_id = record.get_to_robot_id()

            if (self.graph.has_node(from_id) and self.graph.has_node(to_id)):
                try:
                    path_length = nx.shortest_path_length(
                        self.graph, from_id, to_id, weight='weight'
                    )
                    migr_cost += path_length
                except:
                    migr_cost += 10.0

        if len(migration_records) > 0:
            migr_cost /= len(migration_records)

        # Calculate survival rate
        survival_rate = 0.0
        for agent in self.agents:
            rate = (1 - agent.get_fault_a()) * (1 - agent.get_fault_o())
            survival_rate += rate
        survival_rate /= len(self.agents)

        result.set_mean_execute_cost(exec_cost)
        result.set_mean_migration_cost(migr_cost)
        result.set_mean_survival_rate(survival_rate)

        return result


class MPFTM:
    """
    Multi-robot Potential Field Task Migration (MPFTM)

    Strategy: Use potential field theory to guide task migration.
    Agents create attractive/repulsive fields based on load and capacity.

    Key Features:
    - Potential field based decision making
    - Considers both intra-group and inter-group dynamics
    - Physics-inspired approach

    Supply Chain Meaning:
    - Represents market forces (supply/demand)
    - Overloaded suppliers "repel" new tasks
    - Underutilized suppliers "attract" tasks
    - Balances local and global optimization

    Note: This uses existing Python implementation from python_src/mpftm/
    """

    def __init__(self, tasks: List[Task], graph: nx.Graph, agents: List[Agent],
                 a: float = 0.1, b: float = 0.9, name: str = "MPFTM"):
        self.tasks = tasks
        self.graph = graph
        self.agents = agents
        self.a = a
        self.b = b
        self.name = name

        self.id_to_agents = {agent.get_robot_id(): agent for agent in agents}
        self.id_to_groups = {}
        self.id_to_i = {}

    def run(self) -> ExperimentResult:
        """Run MPFTM algorithm"""
        print(f"Running {self.name}...")

        # Initialize
        initialize = Initialize()
        initialize.run(self.tasks, self.agents, self.id_to_groups, self.id_to_agents)

        # Leader selection
        self._leader_selection()

        # Backup leader selection
        self._ad_leaders_selection()

        # Replace faulty leaders
        AdLeadersReplace(self.id_to_groups, self.id_to_agents, self.graph).run()

        # Initialize contextual load
        IniContextLoadI(self.id_to_groups, self.id_to_agents, self.graph,
                       self.id_to_i, self.a, self.b).run()

        # Calculate potential fields
        calculate_pon_field = CalculatePonField(
            self.id_to_groups, self.id_to_agents, self.graph,
            self.id_to_i, self.a, self.b
        )

        robot_id_to_pfield = calculate_pon_field.calculate_intra_p()
        group_id_to_pfield = calculate_pon_field.calculate_inter_p()

        # Execute task migration (using existing implementation)
        from mpftm.task_migration_based_pon import TaskMigrationBasedPon

        migration_records = TaskMigrationBasedPon(
            self.graph, self.id_to_groups, self.id_to_agents,
            group_id_to_pfield, robot_id_to_pfield, [],
            self.a, self.b, self.id_to_i
        ).run()

        # Evaluate
        result = self._evaluate(migration_records)

        return result

    def _leader_selection(self):
        """Select leaders for each group"""
        finder = FinderLeader()

        for group in self.id_to_groups.values():
            if group.get_leader() is None:
                leader = finder.find_leader(group, self.id_to_agents,
                                          self.id_to_groups, self.graph,
                                          self.a, self.b)
                group.set_leader(leader)

        # Add edges between leaders
        for group_id in self.id_to_groups.keys():
            leader_id = self.id_to_groups[group_id].get_leader().get_robot_id()

            for to_group_id in self.id_to_groups.keys():
                to_leader_id = self.id_to_groups[to_group_id].get_leader().get_robot_id()

                if group_id != to_group_id and not self.graph.has_edge(leader_id, to_leader_id):
                    self.graph.add_edge(leader_id, to_leader_id, weight=1.0)

    def _ad_leaders_selection(self):
        """Select backup leaders"""
        finder = FinderAdLeaders()
        max_size = 2

        for group in self.id_to_groups.values():
            if group.get_ad_leaders() is None:
                ad_leaders = finder.find_ad_leaders(
                    group, self.id_to_agents, self.id_to_groups,
                    self.graph, self.a, self.b, max_size
                )
                group.set_ad_leaders(ad_leaders)

    def _evaluate(self, migration_records: List) -> ExperimentResult:
        """Evaluate the assignment"""
        result = ExperimentResult()

        # Calculate execution cost
        exec_cost = 0.0
        for agent in self.agents:
            if agent.get_capacity() > 0:
                exec_cost += agent.get_load() / agent.get_capacity()
        exec_cost /= len(self.agents)

        # Calculate migration cost
        migr_cost = 0.0
        for record in migration_records:
            from_id = record.get_from_robot_id()
            to_id = record.get_to_robot_id()

            if (self.graph.has_node(from_id) and self.graph.has_node(to_id)):
                try:
                    path_length = nx.shortest_path_length(
                        self.graph, from_id, to_id, weight='weight'
                    )
                    migr_cost += path_length
                except:
                    migr_cost += 10.0

        if len(migration_records) > 0:
            migr_cost /= len(migration_records)

        # Calculate survival rate
        survival_rate = 0.0
        for agent in self.agents:
            rate = (1 - agent.get_fault_a()) * (1 - agent.get_fault_o())
            survival_rate += rate
        survival_rate /= len(self.agents)

        result.set_mean_execute_cost(exec_cost)
        result.set_mean_migration_cost(migr_cost)
        result.set_mean_survival_rate(survival_rate)

        return result


def get_additional_algorithms(tasks, graph, agents, a=0.1, b=0.9):
    """Get all additional algorithms for comparison"""
    return [
        GBMA(tasks, graph, agents, a, b),
        MMLMA(tasks, graph, agents, a, b),
        MPFTM(tasks, graph, agents, a, b)
    ]
