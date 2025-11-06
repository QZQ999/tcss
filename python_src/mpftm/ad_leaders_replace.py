"""AdLeadersReplace class for MPFTM - replacing failed leaders with backup leaders"""
import networkx as nx
import sys
sys.path.append('..')


class AdLeadersReplace:
    def __init__(self, id_to_groups, id_to_robots, arc_graph):
        """
        Initialize AdLeadersReplace

        Args:
            id_to_groups: Dictionary mapping group ID to Group objects
            id_to_robots: Dictionary mapping robot ID to Agent objects
            arc_graph: NetworkX graph
        """
        self.id_to_groups = id_to_groups
        self.id_to_robots = id_to_robots
        self.arc_graph = arc_graph

    def run(self):
        """Replace failed leaders with backup leaders"""
        for group_id in self.id_to_groups.keys():
            group = self.id_to_groups[group_id]
            if group.get_leader().get_fault_a() == 1:
                self.replace(group)

    def replace(self, group):
        """
        Replace failed leader with best backup leader

        Args:
            group: Group object with failed leader
        """
        ad_leaders = group.get_ad_leaders()
        if not ad_leaders:
            return

        # Build subgraph
        sub_graph = nx.Graph()
        robot_id_set = group.get_robot_id_in_group()

        for robot_id in robot_id_set:
            sub_graph.add_node(robot_id)
            edges = self.arc_graph.edges(robot_id)

            for edge in edges:
                if edge[0] == robot_id:
                    target = edge[1]
                else:
                    target = edge[0]

                if target == robot_id:
                    continue

                if group.get_group_id() != self.id_to_robots[target].get_group_id():
                    continue

                sub_graph.add_node(target)

                if not sub_graph.has_edge(robot_id, target):
                    weight = self.arc_graph[edge[0]][edge[1]]['weight']
                    sub_graph.add_edge(robot_id, target, weight=weight)

        # Calculate betweenness centrality
        betweenness = nx.betweenness_centrality(sub_graph, weight='weight')

        # Find best replacement leader
        replace_leader = ad_leaders[0]
        max_iscore = -1.0

        for ad_leader in ad_leaders:
            # Calculate I score (betweenness centrality based importance)
            iscore = (betweenness.get(ad_leader.get_robot_id(), 0) + 1) / \
                    (1 - (1 - ad_leader.get_fault_a()) * (1 - ad_leader.get_fault_o()))

            if iscore > max_iscore:
                replace_leader = ad_leader
                max_iscore = iscore

        # Replace leader
        group.set_leader(replace_leader)

        # Remove new leader from backup leaders list
        ad_leaders.remove(replace_leader)
        group.set_ad_leaders(ad_leaders)
