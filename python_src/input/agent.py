"""Agent class definition"""

class Agent:
    def __init__(self):
        self.robot_id = 0
        self.capacity = 0.0
        self.load = 0.0
        self.tasks_list = []
        self.group_id = 0
        self.fault_a = 0.0  # 功能故障
        self.fault_o = 0.0  # 过载故障

    def get_robot_id(self):
        return self.robot_id

    def set_robot_id(self, robot_id):
        self.robot_id = robot_id

    def get_capacity(self):
        return self.capacity

    def set_capacity(self, capacity):
        self.capacity = capacity

    def get_load(self):
        return self.load

    def set_load(self, load):
        self.load = load

    def get_tasks_list(self):
        return self.tasks_list

    def set_tasks_list(self, tasks_list):
        self.tasks_list = tasks_list

    def get_group_id(self):
        return self.group_id

    def set_group_id(self, group_id):
        self.group_id = group_id

    def get_fault_a(self):
        return self.fault_a

    def set_fault_a(self, fault_a):
        self.fault_a = fault_a

    def get_fault_o(self):
        return self.fault_o

    def set_fault_o(self, fault_o):
        self.fault_o = fault_o
