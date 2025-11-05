"""
Baseline Task Migration Algorithms for Comparison

This module implements several baseline algorithms to compare with HGTM:
1. Random Assignment: Random task distribution
2. Greedy Algorithm: Assign tasks to lowest loaded agent
3. Load Balancing: Minimize load variance
4. Nearest Neighbor: Assign based on network proximity

These baselines help evaluate HGTM's performance improvement.
"""

import sys
sys.path.append('python_src')

import random
import networkx as nx
from typing import List, Dict, Tuple
from input.agent import Agent
from input.task import Task
from input.experiment_result import ExperimentResult
from evaluation.evaluation import Evaluation


class BaselineAlgorithm:
    """Base class for baseline algorithms"""

    def __init__(self, tasks: List[Task], graph: nx.Graph, agents: List[Agent],
                 a: float = 0.1, b: float = 0.9, name: str = "Baseline"):
        self.tasks = tasks
        self.graph = graph
        self.agents = agents
        self.a = a
        self.b = b
        self.name = name

        # Create ID mappings
        self.id_to_agents = {agent.get_robot_id(): agent for agent in agents}
        self.id_to_groups = {}  # Baseline algorithms don't use groups

    def run(self) -> ExperimentResult:
        """Run the algorithm and return results"""
        raise NotImplementedError("Subclasses must implement run()")

    def calculate_target_opt(self, exec_cost: float, migr_cost: float,
                            survival_rate: float) -> float:
        """Calculate target optimization value"""
        return self.a * (exec_cost + migr_cost) - self.b * survival_rate


class RandomAssignment(BaselineAlgorithm):
    """Random task assignment algorithm"""

    def __init__(self, tasks, graph, agents, a=0.1, b=0.9):
        super().__init__(tasks, graph, agents, a, b, "Random")

    def run(self) -> ExperimentResult:
        """Randomly assign tasks to agents"""
        # Clear existing assignments
        for agent in self.agents:
            agent.set_load(0.0)
            agent.set_tasks_list([])

        # Randomly assign each task
        for task in self.tasks:
            # Pick a random agent
            agent = random.choice(self.agents)

            # Assign task
            current_tasks = agent.get_tasks_list()
            current_tasks.append(task)
            agent.set_tasks_list(current_tasks)
            agent.set_load(agent.get_load() + task.get_size())

        # Calculate metrics
        return self._evaluate()

    def _evaluate(self) -> ExperimentResult:
        """Evaluate the assignment"""
        result = ExperimentResult()

        # Calculate execution cost
        exec_cost = sum(agent.get_load() / agent.get_capacity()
                       for agent in self.agents if agent.get_capacity() > 0)
        exec_cost /= len(self.agents)

        # No migration cost for initial assignment
        migr_cost = 0.0

        # Calculate survival rate (assume no faults for baseline)
        survival_rate = 1.0

        result.set_mean_execute_cost(exec_cost)
        result.set_mean_migration_cost(migr_cost)
        result.set_mean_survival_rate(survival_rate)

        return result


class GreedyAssignment(BaselineAlgorithm):
    """Greedy task assignment - always assign to least loaded agent"""

    def __init__(self, tasks, graph, agents, a=0.1, b=0.9):
        super().__init__(tasks, graph, agents, a, b, "Greedy")

    def run(self) -> ExperimentResult:
        """Assign tasks greedily to least loaded agent"""
        # Clear existing assignments
        for agent in self.agents:
            agent.set_load(0.0)
            agent.set_tasks_list([])

        # Sort tasks by size (largest first for better balancing)
        sorted_tasks = sorted(self.tasks, key=lambda t: t.get_size(), reverse=True)

        # Assign each task to the least loaded agent
        for task in sorted_tasks:
            # Find agent with minimum load ratio
            min_load_ratio = float('inf')
            best_agent = None

            for agent in self.agents:
                if agent.get_capacity() > 0:
                    load_ratio = agent.get_load() / agent.get_capacity()
                    if load_ratio < min_load_ratio:
                        min_load_ratio = load_ratio
                        best_agent = agent

            # Assign task to best agent
            if best_agent:
                current_tasks = best_agent.get_tasks_list()
                current_tasks.append(task)
                best_agent.set_tasks_list(current_tasks)
                best_agent.set_load(best_agent.get_load() + task.get_size())

        return self._evaluate()

    def _evaluate(self) -> ExperimentResult:
        """Evaluate the assignment"""
        result = ExperimentResult()

        exec_cost = sum(agent.get_load() / agent.get_capacity()
                       for agent in self.agents if agent.get_capacity() > 0)
        exec_cost /= len(self.agents)

        migr_cost = 0.0
        survival_rate = 1.0

        result.set_mean_execute_cost(exec_cost)
        result.set_mean_migration_cost(migr_cost)
        result.set_mean_survival_rate(survival_rate)

        return result


class LoadBalancingAssignment(BaselineAlgorithm):
    """Load balancing with capacity consideration"""

    def __init__(self, tasks, graph, agents, a=0.1, b=0.9):
        super().__init__(tasks, graph, agents, a, b, "LoadBalance")

    def run(self) -> ExperimentResult:
        """Assign tasks to minimize load variance"""
        # Clear existing assignments
        for agent in self.agents:
            agent.set_load(0.0)
            agent.set_tasks_list([])

        # Calculate total capacity
        total_capacity = sum(agent.get_capacity() for agent in self.agents)

        # Sort tasks by size
        sorted_tasks = sorted(self.tasks, key=lambda t: t.get_size(), reverse=True)

        # Assign tasks proportionally to capacity
        for task in sorted_tasks:
            # Find agent with most remaining capacity relative to target
            best_agent = None
            min_deviation = float('inf')

            for agent in self.agents:
                if agent.get_capacity() > 0:
                    # Target load for this agent based on capacity
                    capacity_ratio = agent.get_capacity() / total_capacity
                    target_load = sum(t.get_size() for t in self.tasks) * capacity_ratio

                    # Current deviation from target
                    deviation = abs(agent.get_load() - target_load)

                    if deviation < min_deviation:
                        min_deviation = deviation
                        best_agent = agent

            # Assign task
            if best_agent:
                current_tasks = best_agent.get_tasks_list()
                current_tasks.append(task)
                best_agent.set_tasks_list(current_tasks)
                best_agent.set_load(best_agent.get_load() + task.get_size())

        return self._evaluate()

    def _evaluate(self) -> ExperimentResult:
        """Evaluate the assignment"""
        result = ExperimentResult()

        exec_cost = sum(agent.get_load() / agent.get_capacity()
                       for agent in self.agents if agent.get_capacity() > 0)
        exec_cost /= len(self.agents)

        migr_cost = 0.0
        survival_rate = 1.0

        result.set_mean_execute_cost(exec_cost)
        result.set_mean_migration_cost(migr_cost)
        result.set_mean_survival_rate(survival_rate)

        return result


class NearestNeighborAssignment(BaselineAlgorithm):
    """Assign tasks to nearest available agent in network"""

    def __init__(self, tasks, graph, agents, a=0.1, b=0.9):
        super().__init__(tasks, graph, agents, a, b, "NearestNeighbor")

    def run(self) -> ExperimentResult:
        """Assign tasks based on network proximity"""
        # Clear existing assignments
        for agent in self.agents:
            agent.set_load(0.0)
            agent.set_tasks_list([])

        # For each task, assign to nearest agent with capacity
        for task in self.tasks:
            # Start from a random agent (simulating task origin)
            start_agent_id = random.choice(list(self.id_to_agents.keys()))

            # Find nearest agent with available capacity using BFS
            best_agent = None
            min_distance = float('inf')

            for agent in self.agents:
                agent_id = agent.get_robot_id()

                # Check if agent has capacity
                if agent.get_capacity() > 0:
                    # Calculate distance in network
                    try:
                        if self.graph.has_node(start_agent_id) and self.graph.has_node(agent_id):
                            distance = nx.shortest_path_length(
                                self.graph, start_agent_id, agent_id, weight='weight'
                            )
                        else:
                            distance = float('inf')
                    except nx.NetworkXNoPath:
                        distance = float('inf')

                    # Consider both distance and load
                    load_ratio = agent.get_load() / agent.get_capacity()
                    combined_metric = distance * (1 + load_ratio)

                    if combined_metric < min_distance:
                        min_distance = combined_metric
                        best_agent = agent

            # Assign to best agent
            if best_agent:
                current_tasks = best_agent.get_tasks_list()
                current_tasks.append(task)
                best_agent.set_tasks_list(current_tasks)
                best_agent.set_load(best_agent.get_load() + task.get_size())

        return self._evaluate()

    def _evaluate(self) -> ExperimentResult:
        """Evaluate the assignment"""
        result = ExperimentResult()

        exec_cost = sum(agent.get_load() / agent.get_capacity()
                       for agent in self.agents if agent.get_capacity() > 0)
        exec_cost /= len(self.agents)

        migr_cost = 0.0
        survival_rate = 1.0

        result.set_mean_execute_cost(exec_cost)
        result.set_mean_migration_cost(migr_cost)
        result.set_mean_survival_rate(survival_rate)

        return result


def get_all_baseline_algorithms(tasks, graph, agents, a=0.1, b=0.9):
    """Get all baseline algorithms for comparison"""
    return [
        RandomAssignment(tasks, graph, agents, a, b),
        GreedyAssignment(tasks, graph, agents, a, b),
        LoadBalancingAssignment(tasks, graph, agents, a, b),
        NearestNeighborAssignment(tasks, graph, agents, a, b)
    ]
