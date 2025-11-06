"""GBMATasksMigration - Task migration for GBMA algorithm"""
import sys
import networkx as nx
sys.path.append('..')
from python_src.input.migration_record import MigrationRecord


class GBMATasksMigration:
    """Task migration based on greedy path selection"""

    def __init__(self, id_to_groups, id_to_robots, arc_graph):
        """
        Initialize GBMATasksMigration

        Args:
            id_to_groups: Dictionary mapping group ID to Group objects
            id_to_robots: Dictionary mapping robot ID to Agent objects
            arc_graph: NetworkX graph
        """
        self.arc_graph = arc_graph
        self.id_to_groups = id_to_groups
        self.id_to_robots = id_to_robots
        self.records = []

    def task_migration(self):
        """
        Execute task migration for all faulty robots

        Returns:
            List of MigrationRecord objects
        """
        # Iterate through all robots to find faulty ones
        for robot_id in self.id_to_robots.keys():
            robot = self.id_to_robots[robot_id]

            # Check if robot has functional fault
            if robot.get_fault_a() == 1:
                # Get copy of task list (to avoid modification during iteration)
                tfs = list(robot.get_tasks_list())

                # Migrate all tasks from this faulty robot
                for task in tfs:
                    robot_migrated = self.greedy_find_migrated_robot_by_path(robot)
                    self.execute_migration(robot, robot_migrated, task)

        return self.records

    def greedy_find_migrated_robot_by_path(self, f_robot):
        """
        Find best migration target robot using greedy path-based selection

        Args:
            f_robot: Faulty robot to migrate tasks from

        Returns:
            Best target robot for migration
        """
        from python_src.input.agent import Agent
        migrated_robot = Agent()

        # Get edges connected to faulty robot
        edges = list(self.arc_graph.edges(f_robot.get_robot_id()))
        min_path_weight = float('inf')

        for edge in edges:
            # Get target robot
            if edge[0] == f_robot.get_robot_id():
                target_id = edge[1]
            else:
                target_id = edge[0]

            target_robot = self.id_to_robots[target_id]

            # Only consider robots in the same group
            if target_robot.get_group_id() != f_robot.get_group_id():
                continue

            # Calculate shortest path weight
            try:
                path_weight = nx.shortest_path_length(
                    self.arc_graph,
                    f_robot.get_robot_id(),
                    target_robot.get_robot_id(),
                    weight='weight'
                )
            except:
                continue

            # Select robot with minimum path weight that is not faulty
            if path_weight < min_path_weight and target_robot.get_fault_a() != 1:
                min_path_weight = path_weight
                migrated_robot = target_robot

        return migrated_robot

    def execute_migration(self, robot, robot_migrated, migration_task):
        """
        Execute migration of a task from one robot to another

        Args:
            robot: Source robot
            robot_migrated: Target robot
            migration_task: Task to migrate
        """
        if robot is None or robot_migrated is None or migration_task is None:
            return

        # Update inter-layer load if robots are in different groups
        if robot.get_group_id() != robot_migrated.get_group_id():
            self.update_inter(robot, robot_migrated, migration_task)

        # Update intra-layer load and task lists
        self.update_intra(robot, robot_migrated, migration_task)

        # Record migration
        record = MigrationRecord()
        record.set_from(robot.get_robot_id())
        record.set_to(robot_migrated.get_robot_id())
        self.records.append(record)

    def update_inter(self, robot, robot_migrated, migration_task):
        """
        Update inter-layer group loads

        Args:
            robot: Source robot
            robot_migrated: Target robot
            migration_task: Task being migrated
        """
        if robot is None or robot_migrated is None or migration_task is None:
            return

        group_id = robot.get_group_id()
        group = self.id_to_groups[group_id]

        robot_migrated_group_id = robot_migrated.get_group_id()
        migrated_group = self.id_to_groups[robot_migrated_group_id]

        # Update group loads
        group.set_group_load(group.get_group_load() - migration_task.get_size())
        migrated_group.set_group_load(migrated_group.get_group_load() + migration_task.get_size())

    def update_intra(self, robot, robot_migrated, migration_task):
        """
        Update intra-layer robot loads and task lists

        Args:
            robot: Source robot
            robot_migrated: Target robot
            migration_task: Task being migrated
        """
        # Update source robot
        tasks_list = robot.get_tasks_list()
        tasks_list.remove(migration_task)
        robot.set_load(robot.get_load() - migration_task.get_size())
        robot.set_tasks_list(tasks_list)

        # Update target robot
        robot_migrated_task_list = robot_migrated.get_tasks_list()
        if robot_migrated_task_list is None:
            robot_migrated_task_list = []

        robot_migrated_task_list.append(migration_task)
        robot_migrated.set_load(robot_migrated.get_load() + migration_task.get_size())
        robot_migrated.set_tasks_list(robot_migrated_task_list)
