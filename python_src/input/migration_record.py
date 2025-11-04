"""MigrationRecord class definition"""

class MigrationRecord:
    def __init__(self):
        self.from_id = None
        self.to_id = None

    def get_from(self):
        return self.from_id

    def set_from(self, from_id):
        self.from_id = from_id

    def get_to(self):
        return self.to_id

    def set_to(self, to_id):
        self.to_id = to_id
