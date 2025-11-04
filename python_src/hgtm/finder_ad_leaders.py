"""FinderAdLeaders class for finding backup leader nodes"""
import networkx as nx
import heapq
import sys
sys.path.append('..')


class FinderAdLeaders:
    def find_ad_leaders(self, group, id_to_robots, id_to_groups, arc_graph, a, b, max_size):
        """Find backup leaders for group"""
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

        # Calculate betweenness centrality
        betweenness = nx.betweenness_centrality(sub_graph, weight='weight')

        # Select backup nodes
        id_to_refmap = {}

        for robot_id in robot_id_set:
            robot = id_to_robots[robot_id]

            if robot.get_fault_a() == 1:
                id_to_refmap[robot_id] = -float('inf')
            else:
                iscore = (betweenness.get(robot_id, 0) + 1) / \
                        (1 - (1 - robot.get_fault_a()) * (1 - robot.get_fault_o()))

                try:
                    d = nx.shortest_path_length(arc_graph,
                                               group.get_leader().get_robot_id(),
                                               robot.get_robot_id(),
                                               weight='weight')
                except:
                    d = 100000.0

                id_to_refmap[robot_id] = iscore * d

        # Priority queue (min heap) - negate values for max heap behavior
        ad_leaders_pq = []

        for robot_id in robot_id_set:
            if len(ad_leaders_pq) < max_size:
                heapq.heappush(ad_leaders_pq,
                             (id_to_refmap[robot_id], id_to_robots[robot_id]))
            else:
                min_ref = ad_leaders_pq[0][0]
                if id_to_refmap[robot_id] > min_ref:
                    heapq.heappop(ad_leaders_pq)
                    heapq.heappush(ad_leaders_pq,
                                 (id_to_refmap[robot_id], id_to_robots[robot_id]))

        return [agent for _, agent in ad_leaders_pq]
