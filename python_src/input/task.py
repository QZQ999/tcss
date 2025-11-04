"""Task class definition"""

class Task:
    def __init__(self):
        self.task_id = 0
        self.size = 0.0
        self.arrive_time = 0

    def get_task_id(self):
        return self.task_id

    def set_task_id(self, task_id):
        self.task_id = task_id

    def get_size(self):
        return self.size

    def set_size(self, size):
        self.size = size

    def get_arrive_time(self):
        return self.arrive_time

    def set_arrive_time(self, arrive_time):
        self.arrive_time = arrive_time
