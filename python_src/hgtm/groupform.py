"""Groupform class for grouping agents into bags"""
import sys
sys.path.append('..')
from python_src.main.function import Function


class Groupform:
    def __init__(self, arc_graph, id_to_groups, id_to_agents, a, b):
        self.arc_graph = arc_graph
        self.id_to_groups = id_to_groups
        self.id_to_agents = id_to_agents
        self.a = a
        self.b = b
        self.bags = []
        self.bags_to_agent = {}

        # Initialize bags with faulty agents
        for agent_id in id_to_agents.keys():
            e = id_to_agents[agent_id]
            if e.get_fault_a() == 1:
                bag = [e]
                self.bags.append(bag)

    def run(self):
        """Run groupform algorithm"""
        self.intra_bagform()
        bags_to_agent_return = {}

        for bag in self.bags:
            bag_tuple = tuple(bag)
            if bag_tuple in self.bags_to_agent:
                bags_to_agent_return[bag_tuple] = self.bags_to_agent[bag_tuple]

        return bags_to_agent_return

    def compare_bag(self, bag):
        """Compare bags by total task count"""
        size = sum(len(agent.get_tasks_list()) for agent in bag)
        return -size  # Negative for descending order

    def intra_bagform(self):
        """Perform intra-layer bag formation"""
        import heapq

        pq = [(self.compare_bag(bag), id(bag), bag) for bag in self.bags]
        heapq.heapify(pq)

        temp = []

        while pq:
            _, _, bag_m = heapq.heappop(pq)
            merged = False

            # Extract all remaining bags from pq
            remaining_bags = []
            while pq:
                remaining_bags.append(heapq.heappop(pq))

            # Try to merge bag_m with each remaining bag
            for i, (priority, bag_id, bag_n) in enumerate(remaining_bags):
                if bag_n is None:
                    continue

                bag_temp = list(bag_n) + list(bag_m)

                ben_temp = self.ben_intra(bag_temp)
                ben_n = self.ben_intra(bag_n)
                ben_m = self.ben_intra(bag_m)

                if ben_temp > (ben_n + ben_m):
                    # Merge is beneficial
                    # Remove old entries from bags_to_agent
                    bag_m_tuple = tuple(bag_m)
                    bag_n_tuple = tuple(bag_n)
                    if bag_m_tuple in self.bags_to_agent:
                        del self.bags_to_agent[bag_m_tuple]
                    if bag_n_tuple in self.bags_to_agent:
                        del self.bags_to_agent[bag_n_tuple]

                    # Put merged bag back in pq
                    heapq.heappush(pq, (self.compare_bag(bag_temp), id(bag_temp), bag_temp))

                    # Put back all other bags except bag_n (which was merged)
                    for j, bag_item in enumerate(remaining_bags):
                        if j != i:
                            heapq.heappush(pq, bag_item)

                    merged = True
                    break

            if not merged:
                # No beneficial merge found, bag_m is final
                temp.append(bag_m)
                # Put back all remaining bags
                for bag_item in remaining_bags:
                    heapq.heappush(pq, bag_item)

        self.bags = temp

    def ben_intra(self, bag_temp):
        """Calculate benefit of intra-layer migration"""
        ben_intra_value = -float('inf')
        neighbors = []

        for agent in bag_temp:
            edges = self.arc_graph.edges(agent.get_robot_id())

            for edge in edges:
                if edge[0] == agent.get_robot_id():
                    target_id = edge[1]
                else:
                    target_id = edge[0]

                e = self.id_to_agents[target_id]

                if e.get_group_id() != agent.get_group_id() or e.get_fault_a() == 1:
                    continue

                neighbors.append(e)

        target = None

        for neighbor in neighbors:
            ben_intra_temp = self.ben_intra_calc(bag_temp, neighbor)

            if ben_intra_temp > ben_intra_value:
                ben_intra_value = ben_intra_temp
                target = neighbor

        if target is not None:
            self.bags_to_agent[tuple(bag_temp)] = target

        return ben_intra_value

    def ben_intra_calc(self, bag_temp, neighbor):
        """Calculate benefit for specific neighbor"""
        group = self.id_to_groups[neighbor.get_group_id()]
        interaction_level = group.get_interaction_level()
        mean_c = 0.0
        cost_denominator = 0.0
        count = 0

        edges = self.arc_graph.edges(neighbor.get_robot_id())

        for edge in edges:
            if edge[0] == neighbor.get_robot_id():
                target_id = edge[1]
            else:
                target_id = edge[0]

            e = self.id_to_agents[target_id]

            if e.get_group_id() != neighbor.get_group_id():
                continue

            weight = self.arc_graph[edge[0]][edge[1]]['weight']
            cost_denominator += weight * len(e.get_tasks_list())
            count += 1
            mean_c += e.get_load() / e.get_capacity()

        if count > 0:
            cost_denominator /= count

        load_in_bag = sum(agent.get_load() for agent in bag_temp)
        cost_denominator += load_in_bag

        for agent in bag_temp:
            edge_data = self.arc_graph.get_edge_data(agent.get_robot_id(),
                                                     neighbor.get_robot_id())
            if edge_data is not None:
                cost_denominator += edge_data['weight']

        cost_increase_p = cost_denominator / mean_c if mean_c > 0 else 0

        function = Function(self.id_to_agents, self.id_to_groups)
        complete_p = 1 - max(function.sig(load_in_bag) * interaction_level, 0.5)

        return self.b * complete_p - self.a * cost_increase_p
