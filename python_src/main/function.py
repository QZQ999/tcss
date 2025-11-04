"""Function class for calculating loads and survival rates"""
import math


class Function:
    def __init__(self, id_to_agents, id_to_groups):
        self.id_to_agents = id_to_agents
        self.id_to_groups = id_to_groups

    def calculate_over_load_is(self, robot):
        """Calculate Individual Survivability"""
        load = robot.get_load()
        # Get group survival score
        gs = self.calculate_gs(self.id_to_groups[robot.get_group_id()])
        # Survival rate function
        return max(gs * (1 - self.sig(load / 60)), 0.3)

    def calculate_gs(self, group):
        """Calculate Group Survivability"""
        group_load = group.get_group_load()
        # Use sigmoid-like function variant as monotonic decreasing function in 0-1
        size = len(group.get_robot_id_in_group())
        return max(1 - self.sig(group_load / (size * 200)), 0.6)

    def sig(self, x):
        """Sigmoid-like function"""
        return (math.exp(math.log(x + 1)) - math.exp(-math.log(x + 1))) / \
               (math.exp(math.log(x + 1)) + math.exp(-math.log(x + 1)))

    def calculate_contextual_load(self, leader, robot, arc_graph, shortest_path, a, b):
        """Calculate contextual load"""
        f = a * robot.get_load() / robot.get_capacity() - b * self.calculate_over_load_is(robot)

        # Get domain F from connected edges
        edges = arc_graph.edges(robot.get_robot_id())
        domain_f = 0.0
        cost_sum = 0.0

        for edge in edges:
            # Get the other endpoint of the edge
            if edge[0] == robot.get_robot_id():
                target_id = edge[1]
            else:
                target_id = edge[0]

            target_robot = self.id_to_agents[target_id]

            if target_robot.get_group_id() != robot.get_group_id() or \
               target_robot.get_robot_id() == robot.get_robot_id():
                continue

            # Sum of communication costs of connected edges
            cost_sum += arc_graph[edge[0]][edge[1]]['weight']
            domain_f += a * target_robot.get_load() / target_robot.get_capacity() - \
                       b * self.calculate_over_load_is(target_robot)

        size = len(list(edges)) + 1
        domain_num = size + 1

        # Add cost for inter-layer task migration
        try:
            path_weight = shortest_path(arc_graph, leader.get_robot_id(),
                                       robot.get_robot_id(), weight='weight')
        except:
            path_weight = 0

        cost_sum += path_weight

        return f + 0.1 * (domain_f / domain_num + cost_sum / size)
