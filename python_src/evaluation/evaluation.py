"""Evaluation class for calculating costs and survival rates"""
import networkx as nx


class Evaluation:
    def __init__(self, id_to_robots, id_to_groups):
        self.id_to_robots = id_to_robots
        self.id_to_groups = id_to_groups

    def calculate_migration_cost(self, arc_graph, migration_records):
        """Calculate total migration cost"""
        total = 0.0
        for record in migration_records:
            try:
                path_length = nx.shortest_path_length(arc_graph,
                                                      record.get_from(),
                                                      record.get_to(),
                                                      weight='weight')
                total += path_length
            except:
                total += 0

        return total

    def calculate_execute_tasks_cost(self, robots):
        """Calculate task execution cost"""
        total = 0.0
        for robot in robots:
            tasks_list = robot.get_tasks_list()
            if tasks_list:
                for task in tasks_list:
                    total += task.get_size() / robot.get_capacity()

        return total

    def calculate_mean_survival_rate(self, robots):
        """Calculate mean survival rate"""
        total = 0.0
        count = 0
        for robot in robots:
            if robot.get_fault_a() != 1:
                count += 1
            survival_rate = (1 - robot.get_fault_a()) * (1 - robot.get_fault_o())
            total += survival_rate

        return total / count if count > 0 else 0.0
