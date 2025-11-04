"""CalculatePonField class for calculating potential fields"""
import sys
sys.path.append('..')
from input.potential_field import PotentialField
from main.function import Function


class CalculatePonField:
    def __init__(self, id_to_groups, id_to_robots, arc_graph, id_to_i, a, b):
        self.arc_graph = arc_graph
        self.id_to_groups = id_to_groups
        self.id_to_robots = id_to_robots
        self.a = a
        self.b = b
        self.id_to_i = id_to_i
        self.y = 0.005
        self.yn = 0.3
        self.xn = 0.1
        self.x = 0.01

    def calculate_intra_p(self):
        """Calculate node potential field"""
        intra_potential = {}
        i_sum = sum(self.id_to_i.values())
        i_mean = i_sum / len(self.id_to_robots)

        for robot_id in self.id_to_robots.keys():
            robot = self.id_to_robots[robot_id]
            p = PotentialField()

            # Set attractive potential field
            i_value = self.id_to_i[robot_id]
            p.set_pegra(-self.a * self.gain(i_value - i_mean))

            # Set repulsive potential field
            ro = 0.0
            # Get edges of the node
            edges = self.arc_graph.edges(robot_id)

            for edge in edges:
                # Get target robot
                if edge[0] == robot_id:
                    target_id = edge[1]
                else:
                    target_id = edge[0]

                target_robot = self.id_to_robots[target_id]

                if target_robot.get_group_id() != robot.get_group_id():
                    continue

                if target_robot.get_fault_a() == 1:
                    # Distance to fault node is inversely proportional
                    weight = self.arc_graph[edge[0]][edge[1]]['weight']
                    ro += 1 / weight

            if robot.get_fault_a() == 1:
                p.set_perep(float('inf') / 2)
            elif ro != 0:
                p.set_perep(self.b * (self.y * 1 / ro) * (1 / ro))
            else:
                p.set_perep(0.0)

            intra_potential[robot_id] = p

            # Update overload fault status
            function = Function(self.id_to_robots, self.id_to_groups)
            fault_o = 1 - function.calculate_over_load_is(self.id_to_robots[robot_id])
            robot.set_fault_o(fault_o)

        return intra_potential

    def calculate_inter_p(self):
        """Calculate network layer potential field"""
        inter_potential = {}

        for group_id in self.id_to_groups.keys():
            group = self.id_to_groups[group_id]
            p = PotentialField()

            # Calculate network layer attractive potential field
            p.set_pegra(self.a * self.xn * group.get_group_load())

            # Calculate network layer repulsive field
            fk = 0
            robot_id_in_group = group.get_robot_id_in_group()

            for robot_id in robot_id_in_group:
                robot = self.id_to_robots[robot_id]
                if robot.get_fault_a() == 1:
                    fk += 1

            nk = len(robot_id_in_group)
            if fk == nk:
                p.set_perep(float('inf') / 2)
            else:
                p.set_perep(self.b * (self.yn * fk / (nk - fk)))

            inter_potential[group_id] = p

        return inter_potential

    def gain(self, x):
        """Gain function"""
        return x
