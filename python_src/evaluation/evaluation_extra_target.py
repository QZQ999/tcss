"""EvaluationExtraTarget class for calculating statistics"""
import math


class EvaluationExtraTarget:
    def calculate_robot_capacity_std(self, robots):
        """Calculate standard deviation of robot capacity"""
        capacity_sum = sum(robot.get_capacity() for robot in robots)
        mean = capacity_sum / len(robots)

        sum_sqr = sum((robot.get_capacity() - mean) ** 2 for robot in robots)
        return math.sqrt(sum_sqr / len(robots))

    def calculate_task_size_std(self, tasks):
        """Calculate standard deviation of task size"""
        size_sum = sum(task.get_size() for task in tasks)
        mean = size_sum / len(tasks)

        sum_sqr = sum((task.get_size() - mean) ** 2 for task in tasks)
        return math.sqrt(sum_sqr / len(tasks))

    def calculate_mean_robot_capacity(self, robots):
        """Calculate mean robot capacity"""
        capacity_sum = sum(robot.get_capacity() for robot in robots)
        return capacity_sum / len(robots)

    def calculate_mean_task_size(self, tasks):
        """Calculate mean task size"""
        size_sum = sum(task.get_size() for task in tasks)
        return size_sum / len(tasks)
