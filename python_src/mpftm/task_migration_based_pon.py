"""TaskMigrationBasedPon class for task migration based on potential fields"""
import sys
sys.path.append('..')
from python_src.input.migration_record import MigrationRecord
from .ini_context_load_i import IniContextLoadI
from .calculate_pon_field import CalculatePonField


class TaskMigrationBasedPon:
    def __init__(self, id_to_groups, id_to_robots, arc_graph, group_id_to_pfield,
                 robot_id_to_pfield, id_to_i, a, b):
        self.id_to_groups = id_to_groups
        self.id_to_robots = id_to_robots
        self.group_id_to_pfield = group_id_to_pfield
        self.robot_id_to_pfield = robot_id_to_pfield
        self.arc_graph = arc_graph
        self.a = a
        self.b = b
        self.id_to_i = id_to_i
        self.records = []

    def run(self):
        """Run task migration"""
        self.inter_task_migration()
        return self.records

    def inter_task_migration(self):
        """Inter-layer task migration"""
        f_groups = set()
        for robot_id in self.id_to_robots.keys():
            robot = self.id_to_robots[robot_id]
            if robot.get_fault_a() == 1:
                f_groups.add(robot.get_group_id())

        average_pe_n = self.get_average_pe_n()

        for fgroup_id in f_groups:
            s_group = self.id_to_groups[fgroup_id]
            robot_id_in_group = s_group.get_robot_id_in_group()

            for robot_id in robot_id_in_group:
                robot = self.id_to_robots[robot_id]
                if robot.get_fault_a() == 1:
                    tnf = list(robot.get_tasks_list())
                    pf = self.group_id_to_pfield[fgroup_id]
                    p_fg = pf.get_pegra() + pf.get_perep()

                    if p_fg > average_pe_n:
                        # Need inter-layer task migration
                        t_group_id = self.find_min_pn()
                        for task in tnf:
                            pt = self.group_id_to_pfield[t_group_id]
                            p_tg = pt.get_pegra() + pt.get_perep()
                            if p_tg < average_pe_n:
                                self.execute_migration(robot,
                                                     self.id_to_groups[t_group_id].get_leader(),
                                                     task)

            # Execute intra-layer task migration
            self.intra_task_migration(fgroup_id)

    def intra_task_migration(self, group_id):
        """Intra-layer task migration"""
        f_robots = []
        group = self.id_to_groups[group_id]

        for robot_id in group.get_robot_id_in_group():
            robot = self.id_to_robots[robot_id]
            if robot.get_fault_a() == 1:
                f_robots.append(robot)

        leader = group.get_leader()

        for f_robot in f_robots:
            tasks_list = f_robot.get_tasks_list()
            while len(tasks_list) > 0:
                migrated_task = tasks_list[0]
                migrated_robot = self.find_migrated_robot(f_robot)
                self.execute_migration(f_robot, migrated_robot, migrated_task)
                tasks_list = f_robot.get_tasks_list()

                self.migration_for_robot(migrated_robot, set())

        self.migration_for_robot(leader, set())

    def migration_for_robot(self, agent, visited_set):
        """Recursive migration for robot"""
        visited_set.add(agent.get_robot_id())
        robot_id = agent.get_robot_id()

        edges = list(self.arc_graph.edges(robot_id))
        domain_id = []

        for edge in edges:
            if edge[0] != robot_id:
                domain_id.append(edge[0])
            else:
                domain_id.append(edge[1])

        if not domain_id:
            return

        # Sort by comparator
        domain_id.sort(key=lambda x: self.get_compare_value(agent, x), reverse=True)

        migrated_id = domain_id[0]

        po_r = self.robot_id_to_pfield[robot_id]
        por_value = po_r.get_pegra() + po_r.get_perep()

        po_m = self.robot_id_to_pfield[migrated_id]
        pom_value = po_m.get_pegra() + po_m.get_perep()

        tasks_list = agent.get_tasks_list()
        migrated_task = self.find_max_task(tasks_list)

        if migrated_task is None:
            return

        edge_data = self.arc_graph.get_edge_data(robot_id, migrated_id)
        if edge_data is None:
            return

        c = edge_data['weight']

        while ((por_value - pom_value) / c) > 0.02:
            robot_migrated = self.id_to_robots[migrated_id]
            self.execute_migration(agent, robot_migrated, migrated_task)

            if migrated_id not in visited_set:
                self.migration_for_robot(robot_migrated, visited_set)
            else:
                break

            # Update values
            domain_id.sort(key=lambda x: self.get_compare_value(agent, x), reverse=True)
            migrated_id = domain_id[0]

            po_r = self.robot_id_to_pfield[robot_id]
            por_value = po_r.get_pegra() + po_r.get_perep()

            po_m = self.robot_id_to_pfield[migrated_id]
            pom_value = po_m.get_pegra() + po_m.get_perep()

            tasks_list = agent.get_tasks_list()
            migrated_task = self.find_max_task(tasks_list)

            if migrated_task is None:
                break

    def get_compare_value(self, robot, target_id):
        """Get comparison value for sorting"""
        po = self.robot_id_to_pfield[target_id]
        po_value = po.get_pegra() + po.get_perep()

        robot_id = robot.get_robot_id()
        po_m = self.robot_id_to_pfield[robot_id]
        po_m_value = po_m.get_pegra() + po_m.get_perep()

        edge_data = self.arc_graph.get_edge_data(robot_id, target_id)
        if edge_data is None:
            return -float('inf')

        cij = edge_data['weight']
        return (po_value - po_m_value) / cij

    def find_max_task(self, tasks_list):
        """Find maximum task"""
        if not tasks_list or len(tasks_list) < 1:
            return None

        return_task = tasks_list[0]
        for task in tasks_list:
            if task.get_size() > return_task.get_size():
                return_task = task

        return return_task

    def find_migrated_robot(self, f_robot):
        """Find migration target robot"""
        from python_src.input.agent import Agent
        migrated_robot = Agent()

        edges = self.arc_graph.edges(f_robot.get_robot_id())
        min_value = float('inf')

        for edge in edges:
            if edge[0] == f_robot.get_robot_id():
                target_id = edge[1]
            else:
                target_id = edge[0]

            target_robot = self.id_to_robots[target_id]

            target_p = self.robot_id_to_pfield[target_robot.get_robot_id()]
            v = (target_p.get_pegra() + target_p.get_perep()) * \
                self.arc_graph[edge[0]][edge[1]]['weight']

            if v < min_value:
                migrated_robot = target_robot
                min_value = v

        return migrated_robot

    def find_min_pn(self):
        """Find minimum potential network layer"""
        min_value = float('inf')
        return_id = -1

        for group_id in self.group_id_to_pfield.keys():
            p = self.group_id_to_pfield[group_id]
            p_value = p.get_perep() + p.get_pegra()

            if min_value > p_value:
                min_value = p_value
                return_id = group_id

        return return_id

    def get_average_pe_n(self):
        """Get average potential energy"""
        pe_n_sum = 0.0

        for group_id in self.group_id_to_pfield.keys():
            pe_n = self.group_id_to_pfield[group_id]
            pe_n_sum += pe_n.get_pegra()
            pe_n_sum += pe_n.get_perep()

        return pe_n_sum / len(self.group_id_to_pfield)

    def execute_migration(self, robot, robot_migrated, migration_task):
        """Execute migration"""
        if robot is None or robot_migrated is None or migration_task is None:
            return

        # Update inter-layer load and task list
        if robot.get_group_id() != robot_migrated.get_group_id():
            self.update_inter(robot, robot_migrated, migration_task)

        # Update intra-layer load and task list
        self.update_intra(robot, robot_migrated, migration_task)

        record = MigrationRecord()
        record.set_from(robot.get_robot_id())
        record.set_to(robot_migrated.get_robot_id())
        self.records.append(record)

        # Initialize contextual load
        IniContextLoadI(self.id_to_groups, self.id_to_robots,
                       self.arc_graph, self.id_to_i, self.a, self.b).run()

        # Update potential field
        calculate_pon_field = CalculatePonField(self.id_to_groups, self.id_to_robots,
                                               self.arc_graph, self.id_to_i, self.a, self.b)

        if robot.get_group_id() != robot_migrated.get_group_id():
            self.group_id_to_pfield = calculate_pon_field.calculate_inter_p()

        self.robot_id_to_pfield = calculate_pon_field.calculate_intra_p()

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
