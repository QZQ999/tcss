package evaluation;

import input.Agent;
import input.Task;

import java.util.List;

public class EvaluationEtraTarget {
    public Double calculateRobotCapacityStd(List<Agent> robots) {
        double capacitySum  = 0.0;
        for (Agent robot : robots) {
            capacitySum +=robot.getCapacity();
        }
        double mean = capacitySum /robots.size();
        double sumSqr = 0.0;
        for (Agent robot : robots) {
            double capacity = robot.getCapacity();
            sumSqr+=(capacity-mean)*(capacity-mean);
        }
        return Math.sqrt(sumSqr/robots.size());
    }

    public Double calculateTaskSizeStd(List<Task> tasks) {
        double sizeSum = 0.0;
        for (Task task : tasks) {
            sizeSum+=task.getSize();
        }
        double mean = sizeSum/tasks.size();
        double sumSqr = 0.0;
        for (Task task : tasks) {
            double size = task.getSize();
            sumSqr+=(size-mean)*(size-mean);
        }
        return Math.sqrt(sumSqr/tasks.size());
    }

    public Double calculateMeanRobotCapacity(List<Agent> robots) {
        double capacitySum = 0.0;
        for (Agent robot : robots) {
            capacitySum+=robot.getCapacity();
        }
        return capacitySum/robots.size();
    }

    public Double calculateMeanTaskSize (List<Task> tasks){
        double sizeSum = 0.0;
        for (Task task : tasks) {
            sizeSum+=task.getSize();
        }
        return sizeSum/tasks.size();
    }

}
