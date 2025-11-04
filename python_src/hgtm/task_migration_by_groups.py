"""TaskMigrationByGroups class for group-based task migration"""
import sys
sys.path.append('..')
from input.migration_record import MigrationRecord
from mpftm.task_migration_based_pon import TaskMigrationBasedPon


class TaskMigrationByGroups:
    def __init__(self, arc_graph, id_to_groups, id_to_agents,
                 group_id_to_pfield, robot_id_to_pfield,
                 records, a, b, id_to_i):
        self.arc_graph = arc_graph
        self.id_to_groups = id_to_groups
        self.id_to_agents = id_to_agents
        self.group_id_to_pfield = group_id_to_pfield
        self.robot_id_to_pfield = robot_id_to_pfield
        self.records = records
        self.a = a
        self.b = b
        self.id_to_i = id_to_i

    def run(self, bags_to_agent):
        """Run task migration by groups"""
        rece_agents = []

        for bag, agent in bags_to_agent.items():
            if agent is None:
                continue

            q_size = len(agent.get_tasks_list()) if agent.get_tasks_list() else 0

            g_size = sum(len(e.get_tasks_list()) for e in bag)

            group_id = agent.get_group_id()
            rl = self.id_to_groups[group_id].get_interaction_level()

            if g_size * (1 - rl) * 2 > q_size:
                rece_agents.append(agent)

        migration_agents = []

        for agent_id in self.id_to_agents.keys():
            agent = self.id_to_agents[agent_id]
            if agent.get_fault_a() == 1:
                migration_agents.append(agent)
                agent.set_fault_a(0)
                agent.set_fault_o(1)

        for rece_agent in rece_agents:
            rece_agent.set_fault_a(1)

        # Pre-execute MPFTM algorithm
        migration_records = TaskMigrationBasedPon(
            self.id_to_groups, self.id_to_agents, self.arc_graph,
            self.group_id_to_pfield, self.robot_id_to_pfield,
            self.id_to_i, self.a, self.b
        ).run()

        self.records.extend(migration_records)

        for rece_agent in rece_agents:
            rece_agent.set_fault_a(0)

        for bag, agent_migrated in bags_to_agent.items():
            for agent in bag:
                for task in list(agent.get_tasks_list()):
                    self.execute_migration(agent, agent_migrated, task)

        return self.records

    def execute_migration(self, agent, agent_migrated, migration_task):
        """Execute migration"""
        if agent is None or agent_migrated is None or migration_task is None:
            return

        # Update inter-layer load and task list
        if agent.get_group_id() != agent_migrated.get_group_id():
            self.update_inter(agent, agent_migrated, migration_task)

        # Update intra-layer load and task list
        self.update_intra(agent, agent_migrated, migration_task)

        record = MigrationRecord()
        record.set_from(agent.get_robot_id())
        record.set_to(agent_migrated.get_robot_id())
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
