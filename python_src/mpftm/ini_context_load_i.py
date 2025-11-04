"""IniContextLoadI class for initializing contextual load"""
import sys
sys.path.append('..')
from main.function import Function


class IniContextLoadI:
    def __init__(self, id_to_groups, id_to_robots, arc_graph, id_to_i, a, b):
        self.id_to_groups = id_to_groups
        self.id_to_robots = id_to_robots
        self.arc_graph = arc_graph
        self.a = a
        self.b = b
        self.id_to_i = id_to_i

    def run(self):
        """Run initialization of contextual load"""
        import networkx as nx

        function = Function(self.id_to_robots, self.id_to_groups)

        for robot_id in self.id_to_robots.keys():
            robot = self.id_to_robots[robot_id]
            group = self.id_to_groups[robot.get_group_id()]

            # Calculate contextual load
            i_value = function.calculate_contextual_load(
                group.get_leader(), robot, self.arc_graph,
                nx.shortest_path_length, self.a, self.b
            )

            if i_value > 1000 or i_value < -1000:
                i_value = 1.0

            self.id_to_i[robot_id] = i_value
