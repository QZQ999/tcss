"""ExperimentResult class definition"""

class ExperimentResult:
    def __init__(self):
        self.mean_migration_cost = 0.0
        self.mean_execute_cost = 0.0
        self.mean_survival_rate = 0.0

    def get_mean_migration_cost(self):
        return self.mean_migration_cost

    def set_mean_migration_cost(self, mean_migration_cost):
        self.mean_migration_cost = mean_migration_cost

    def get_mean_execute_cost(self):
        return self.mean_execute_cost

    def set_mean_execute_cost(self, mean_execute_cost):
        self.mean_execute_cost = mean_execute_cost

    def get_mean_survival_rate(self):
        return self.mean_survival_rate

    def set_mean_survival_rate(self, mean_survival_rate):
        self.mean_survival_rate = mean_survival_rate
