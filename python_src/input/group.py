"""Group class definition"""

class Group:
    def __init__(self):
        self.group_id = 0
        self.group_load = 0.0
        self.leader = None
        self.robot_id_in_group = set()
        self.assigned_tasks = []
        self.group_capacity = 0.0
        self.ad_leaders = []
        self.interaction_level = 0.0

    def get_group_id(self):
        return self.group_id

    def set_group_id(self, group_id):
        self.group_id = group_id

    def get_group_load(self):
        return self.group_load

    def set_group_load(self, group_load):
        self.group_load = group_load

    def get_leader(self):
        return self.leader

    def set_leader(self, leader):
        self.leader = leader

    def get_robot_id_in_group(self):
        return self.robot_id_in_group

    def set_robot_id_in_group(self, robot_id_in_group):
        self.robot_id_in_group = robot_id_in_group

    def get_assigned_tasks(self):
        return self.assigned_tasks

    def set_assigned_tasks(self, assigned_tasks):
        self.assigned_tasks = assigned_tasks

    def get_group_capacity(self):
        return self.group_capacity

    def set_group_capacity(self, group_capacity):
        self.group_capacity = group_capacity

    def get_ad_leaders(self):
        return self.ad_leaders

    def set_ad_leaders(self, ad_leaders):
        self.ad_leaders = ad_leaders

    def get_interaction_level(self):
        return self.interaction_level

    def set_interaction_level(self, interaction_level):
        self.interaction_level = interaction_level
