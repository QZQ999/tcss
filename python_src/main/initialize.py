"""Initialize class for task assignment and fault initialization"""
import random
import heapq
from .function import Function


class Initialize:
    def __init__(self):
        self.fault_p = 0.3

    def run(self, tasks, robots, id_to_groups, id_to_robots):
        """Run initialization"""
        self.ini_task(tasks, robots, id_to_groups, id_to_robots)
        self.ini_fault(id_to_robots, id_to_groups)

    def ini_fault(self, id_to_robots, id_to_groups):
        """Initialize faults"""
        size = len(id_to_robots)
        fault_size = int(size * self.fault_p)
        if fault_size == 0:
            fault_size += 1
        step = size // fault_size

        # Get list of robot IDs (not assume sequential 0,1,2...)
        robot_ids = list(id_to_robots.keys())

        # fault_p represents the proportion of nodes with functional faults
        for i, robot_id in enumerate(robot_ids):
            robot = id_to_robots[robot_id]
            if i % step == 1:
                # Faults occur regionally
                robot.set_fault_a(1)
                group_id = robot.get_group_id()
                group = id_to_groups[group_id]
                group.set_group_capacity(group.get_group_capacity() - robot.get_capacity())

            function = Function(id_to_robots, id_to_groups)
            fault_o = 1 - function.calculate_over_load_is(robot)
            robot.set_fault_o(fault_o)
            # Set component overload fault probability

    def ini_task(self, tasks, robots, id_to_groups, id_to_robots):
        """Initialize task assignment"""
        # Assign tasks at time -1 to groups and robots (as initial state)
        tasks_pre = []
        for task in tasks[:]:
            if task.get_arrive_time() != -1:
                break
            else:
                tasks_pre.append(task)

        for task in tasks_pre:
            tasks.remove(task)
            # Remove already assigned tasks from the task queue

        # Sort tasks by size in descending order
        tasks_pre.sort(key=lambda t: -t.get_size())

        # Initial matching of robots and tasks
        pq_robots = []

        # Sort robots by capacity in descending order
        robots.sort(key=lambda r: -r.get_capacity())

        counter = 0
        for robot in robots:
            # Update robots (node numbers) in the group
            group_id = robot.get_group_id()
            group = id_to_groups.get(group_id)
            if group is None:
                from python_src.input.group import Group
                group = Group()
                group.set_group_id(group_id)

            robot_id_in_group = group.get_robot_id_in_group()
            if robot_id_in_group is None:
                robot_id_in_group = set()

            robot_id_in_group.add(robot.get_robot_id())
            group.set_robot_id_in_group(robot_id_in_group)
            id_to_groups[group_id] = group

            self.update(tasks_pre, robot, id_to_groups)
            heapq.heappush(pq_robots, (robot.get_load() / robot.get_capacity(), counter, robot))
            counter += 1

        while tasks_pre:
            # Match all initial tasks
            _, _, robot = heapq.heappop(pq_robots)
            self.update(tasks_pre, robot, id_to_groups)
            heapq.heappush(pq_robots, (robot.get_load() / robot.get_capacity(), counter, robot))
            counter += 1

        # Fill in group capacity information
        for group_id in id_to_groups.keys():
            group = id_to_groups[group_id]
            robot_id_in_group = group.get_robot_id_in_group()
            capacity_sum = 0.0
            for robot_id in robot_id_in_group:
                capacity_sum += id_to_robots[robot_id].get_capacity()

            group.set_group_capacity(capacity_sum)
            rand_val = random.randint(0, 1)
            interaction_level = rand_val * 0.1 + 0.1
            group.set_interaction_level(interaction_level)

    def update(self, tasks_pre, robot, id_to_groups):
        """Update robot task list and load"""
        robot_tasks_list = robot.get_tasks_list()
        if not tasks_pre:
            return

        robot_tasks_list.append(tasks_pre[0])
        # Update robot load, assign the largest task to the robot with the smallest load
        robot.set_load(robot.get_load() + tasks_pre[0].get_size())

        group_id = robot.get_group_id()
        # Update group load
        group = id_to_groups[group_id]
        group.set_group_load(group.get_group_load() + tasks_pre[0].get_size())
        group.set_group_id(group_id)

        tasks_pre.pop(0)
        robot.set_tasks_list(robot_tasks_list)


# Convenience function for simplified initialization
def initialization(robots, tasks, fault_rate=0.3):
    """
    Simplified initialization function

    Args:
        robots: List of robot/agent objects
        tasks: List of task objects
        fault_rate: Proportion of robots that should fail (default: 0.3)

    Returns:
        Tuple of (robots, tasks_all_migration, robots_fault_set)
    """
    from ..input.group import Group

    # IMPORTANT: Set all tasks' arrive_time to -1 for initial assignment
    # The ini_task method only processes tasks with arrive_time == -1
    for task in tasks:
        task.set_arrive_time(-1)

    # Create ID mappings
    id_to_groups = {}
    id_to_robots = {}

    for robot in robots:
        rid = robot.get_robot_id()
        gid = robot.get_group_id()
        id_to_robots[rid] = robot

        if gid not in id_to_groups:
            group = Group()
            group.set_group_id(gid)
            group.set_robot_id_in_group(set())
            group.set_group_capacity(0.0)
            group.set_group_load(0.0)
            id_to_groups[gid] = group

    # Run initialization
    initializer = Initialize()
    initializer.fault_p = fault_rate
    initializer.run(tasks, robots, id_to_groups, id_to_robots)

    # Collect faulty robots
    robots_fault_set = []
    for robot in robots:
        if robot.get_fault_a() == 1:
            robots_fault_set.append(robot)

    # All tasks are migration tasks (simplified)
    tasks_all_migration = tasks.copy()

    return (robots, tasks_all_migration, robots_fault_set)
