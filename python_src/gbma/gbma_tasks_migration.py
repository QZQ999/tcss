"""GMBATasksMigration class for GBMA task migration"""
import sys
import os
import networkx as nx

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from input.migration_record import MigrationRecord
from input.agent import Agent


class GMBATasksMigration:
    def __init__(self, id_to_groups, id_to_robots, arc_graph):
        self.arc_graph = arc_graph
        self.id_to_groups = id_to_groups
        self.id_to_robots = id_to_robots
        self.records = []

    def task_migration(self):
        """Execute task migration"""
        for robot_id in self.id_to_robots.keys():
            robot = self.id_to_robots[robot_id]
            if robot.get_fault_a() == 1:
                tfs = list(robot.get_tasks_list())
                for task in tfs:
                    robot_migrated = self.greedy_find_migrated_robot_by_path(robot)
                    self.execute_migration(robot, robot_migrated, task)

        return self.records

    def greedy_find_migrated_robot_by_path(self, f_robot):
        """Find migration target robot greedily by shortest path"""
        migrated_robot = Agent()

        edges = self.arc_graph.edges(f_robot.get_robot_id())
        min_path_weight = float('inf')

        for edge in edges:
            if edge[0] == f_robot.get_robot_id():
                target_id = edge[1]
            else:
                target_id = edge[0]

            target_robot = self.id_to_robots[target_id]

            if target_robot.get_group_id() != f_robot.get_group_id():
                continue

            try:
                path_weight = nx.shortest_path_length(self.arc_graph,
                                                      f_robot.get_robot_id(),
                                                      target_robot.get_robot_id(),
                                                      weight='weight')
                if path_weight < min_path_weight and target_robot.get_fault_a() != 1:
                    min_path_weight = path_weight
                    migrated_robot = target_robot
            except:
                continue

        return migrated_robot

    def execute_migration(self, robot, robot_migrated, migration_task):
        """Execute migration"""
        if robot is None or robot_migrated is None or migration_task is None:
            return

        # Update inter-layer if different groups
        if robot.get_group_id() != robot_migrated.get_group_id():
            self.update_inter(robot, robot_migrated, migration_task)

        # Update intra-layer
        self.update_intra(robot, robot_migrated, migration_task)

        record = MigrationRecord()
        record.set_from(robot.get_robot_id())
        record.set_to(robot_migrated.get_robot_id())
        self.records.append(record)

    def update_inter(self, robot, robot_migrated, migration_task):
        """Update inter-layer migration"""
        if robot is None or robot_migrated is None or migration_task is None:
            return

        group_id = robot.get_group_id()
        group = self.id_to_groups[group_id]

        robot_migrated_group_id = robot_migrated.get_group_id()
        migrated_group = self.id_to_groups[robot_migrated_group_id]

        group.set_group_load(group.get_group_load() - migration_task.get_size())
        migrated_group.set_group_load(migrated_group.get_group_load() + migration_task.get_size())

    def update_intra(self, robot, robot_migrated, migration_task):
        """Update intra-layer migration"""
        tasks_list = robot.get_tasks_list()
        tasks_list.remove(migration_task)
        robot.set_load(robot.get_load() - migration_task.get_size())
        robot.set_tasks_list(tasks_list)

        robot_migrated_task_list = robot_migrated.get_tasks_list()
        if robot_migrated_task_list is None:
            robot_migrated_task_list = []

        robot_migrated_task_list.append(migration_task)
        robot_migrated.set_load(robot_migrated.get_load() + migration_task.get_size())
        robot_migrated.set_tasks_list(robot_migrated_task_list)
