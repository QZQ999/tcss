"""Reader class for reading input files"""
import networkx as nx
from .task import Task
from .agent import Agent


# Global reader instance for convenience functions
_reader = None


def get_reader():
    """Get or create global reader instance"""
    global _reader
    if _reader is None:
        _reader = Reader()
    return _reader


class Reader:
    def read_file_to_graph(self, graph_file):
        """Read graph from file and create NetworkX graph"""
        arc_graph = nx.Graph()

        with open(graph_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 3:
                    a = int(parts[0])
                    b = int(parts[1])
                    c = float(parts[2])

                    # Add vertices (nodes)
                    arc_graph.add_node(a)
                    arc_graph.add_node(b)

                    # Add edge with weight
                    arc_graph.add_edge(a, b, weight=c)

        return arc_graph

    def read_file_to_tasks(self, tasks_file):
        """Read tasks from file"""
        tasks = []

        with open(tasks_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 3:
                    task = Task()
                    task.set_task_id(int(parts[0]))
                    task.set_size(float(parts[1]))
                    task.set_arrive_time(int(parts[2]))
                    tasks.append(task)

        return tasks

    def read_file_to_robots(self, robots_file):
        """Read robots/agents from file"""
        robots = []

        with open(robots_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 3:
                    robot = Agent()
                    robot.set_robot_id(int(parts[0]))
                    robot.set_capacity(float(parts[1]))
                    robot.set_load(0.0)
                    robot.set_tasks_list([])
                    robot.set_group_id(int(parts[2]))
                    robots.append(robot)

        return robots


# Convenience functions using global reader instance
def read_task(task_file):
    """Convenience function to read tasks from file"""
    return get_reader().read_file_to_tasks(task_file)


def read_robot(robot_file):
    """Convenience function to read robots from file"""
    return get_reader().read_file_to_robots(robot_file)


def read_graph(graph_file):
    """Convenience function to read graph from file"""
    return get_reader().read_file_to_graph(graph_file)
