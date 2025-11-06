"""FinderLeader class for MPFTM - finding leader nodes"""
import networkx as nx
import sys
sys.path.append('..')
from python_src.main.function import Function


class FinderLeader:
    def find_leader(self, group, id_to_robots, id_to_groups, arc_graph, a, b):
        """Find leader for group"""
        sub_graph = nx.Graph()
        robot_id_set = group.get_robot_id_in_group()

        for robot_id in robot_id_set:
            sub_graph.add_node(robot_id)
            edges = arc_graph.edges(robot_id)

            for edge in edges:
                if edge[0] == robot_id:
                    target = edge[1]
                else:
                    target = edge[0]

                if target == robot_id:
                    continue

                if group.get_group_id() != id_to_robots[target].get_group_id():
                    continue

                sub_graph.add_node(target)

                if not sub_graph.has_edge(robot_id, target):
                    weight = arc_graph[edge[0]][edge[1]]['weight']
                    sub_graph.add_edge(robot_id, target, weight=weight)

        # Calculate betweenness centrality of subgraph
        betweenness = nx.betweenness_centrality(sub_graph, weight='weight')

        leader_id = -1
        max_iscore = -1.0

        for vertex in robot_id_set:
            function = Function(id_to_robots, id_to_groups)
            bc_value = betweenness.get(vertex, 0)
            p = function.calculate_over_load_is(id_to_robots[vertex])
            # Note: MPFTM uses multiplication instead of addition for Iscore
            iscore = a * bc_value * b * p

            if iscore > max_iscore:
                max_iscore = iscore
                leader_id = vertex

        return id_to_robots[leader_id]
