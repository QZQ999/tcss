"""PotentialField class definition"""

class PotentialField:
    def __init__(self):
        self.pegra = 0.0
        self.perep = 0.0

    def get_pegra(self):
        return self.pegra

    def set_pegra(self, pegra):
        self.pegra = pegra

    def get_perep(self):
        return self.perep

    def set_perep(self, perep):
        self.perep = perep
