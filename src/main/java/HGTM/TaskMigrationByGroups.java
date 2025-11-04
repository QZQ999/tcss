package HGTM;

import MPFTM.TaskMigrationBasedPon;
import input.*;
import org.jgrapht.alg.interfaces.ShortestPathAlgorithm;
import org.jgrapht.graph.DefaultUndirectedWeightedGraph;
import org.jgrapht.graph.DefaultWeightedEdge;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class TaskMigrationByGroups {
    private DefaultUndirectedWeightedGraph<Integer, DefaultWeightedEdge> arcGraph;
    private HashMap<Integer, Group> idToGroups;
    private HashMap<Integer, Agent> idToAgents;
    private ShortestPathAlgorithm<Integer, DefaultWeightedEdge> shortestPath ;
    private HashMap<Integer, PotentialField> groupIdToPfield;
    private HashMap<Integer,PotentialField> robotIdToPfield;
    private List<MigrationRecord> records;
    Double a;
    Double b;
    private HashMap<Integer,Double> idToI;

    public TaskMigrationByGroups(DefaultUndirectedWeightedGraph<Integer, DefaultWeightedEdge> arcGraph, HashMap<Integer, Group> idToGroups, HashMap<Integer, Agent> idToAgents,
                                 ShortestPathAlgorithm<Integer, DefaultWeightedEdge> shortestPath, HashMap<Integer, PotentialField> groupIdToPfield, HashMap<Integer, PotentialField> robotIdToPfield,
                                 List<MigrationRecord> records, Double a, Double b, HashMap<Integer, Double> idToI) {
        this.arcGraph = arcGraph;
        this.idToGroups = idToGroups;
        this.idToAgents = idToAgents;
        this.shortestPath = shortestPath;
        this.groupIdToPfield = groupIdToPfield;
        this.robotIdToPfield = robotIdToPfield;
        this.records = records;
        this.a = a;
        this.b = b;
        this.idToI = idToI;
    }
    public List<MigrationRecord> run(Map<List<Agent>,Agent> bagsToAgent) {
        List<Agent> receAgents = new ArrayList<>();
        for (List<Agent> bag : bagsToAgent.keySet()) {
            Agent agent = bagsToAgent.get(bag);
            if (agent==null) {
                continue;
            }
            int Qsize = 0;
            if (agent.getTasksList() != null) {
                Qsize = agent.getTasksList().size();
            }
            int Gsize = 0;
            for (Agent e : bag) {
                Gsize+=e.getTasksList().size();
            }
            int groupId = agent.getGroupId();
            double RL = idToGroups.get(groupId).getInteractionLevel();
            if (Gsize*(1-RL)*2>Qsize) {
                receAgents.add(agent);
            } else {
                //bagsToAgent.remove(bag);
            }
        }
        List<Agent> MigrationAgents = new ArrayList<>();
        for (Integer id : idToAgents.keySet()) {
            Agent agent = idToAgents.get(id);
            if (agent.getFaultA()==1) {
                MigrationAgents.add(agent);
                agent.setFaultA(0);
                agent.setFaultO(1);
                //为了方便将接收任务的组件上原有的任务扩散出去，也为了能够更好的利用原有的MPTFM算法
            }
        }
        for (Agent receAgent : receAgents) {
            receAgent.setFaultA(1);
            //为了方便将接收任务的组件上原有的任务扩散出去，只有FaultA=1的组件上的任务才会被扩散出去
        }
        //对接收任务的组件提前执行MPFTM算法--腾出负载空间
        List<MigrationRecord> migrationRecords = new TaskMigrationBasedPon(idToGroups, idToAgents,
                arcGraph, groupIdToPfield, robotIdToPfield, shortestPath, idToI, a, b).run();
        records.addAll(migrationRecords);
        for (Agent receAgent : receAgents) {
            //还原接收任务的组件状态
            receAgent.setFaultA(0);
        }
        for (List<Agent> bag : bagsToAgent.keySet()) {
            Agent agentMigrated = bagsToAgent.get(bag);
            for (Agent agent : bag) {
                for (Task task : agent.getTasksList()) {
                    excuteMigration(agent,agentMigrated,task);
                }
            }
        }

        return records;
    }

    private void excuteMigration(Agent agent, Agent agentMigrated, Task migrationTask) {
        if (agent == null) {
            return;
        }

        if (agentMigrated == null) {
            return;
        }
        if (migrationTask == null) {
            return;
        }

        //改变网络层间负载和任务列表
        if (agent.getGroupId()!=agentMigrated.getGroupId()) {
            //不在同一组才会更新网络层间的势场情况
            updateInter(agent, agentMigrated, migrationTask);
        }
        //改变网络层内负载和任务列表
        updateIntra(agent, agentMigrated, migrationTask);
        MigrationRecord record = new MigrationRecord();
        record.setFrom(agent.getRobotId());
        record.setTo(agentMigrated.getRobotId());
        records.add(record);
        //初始化（计算）上下文负载

    }
    private void updateInter(Agent robot, Agent robotMigrated, Task migrationTask) {
        if (robot == null) {
            return;
        }

        if (robotMigrated == null) {
            return;
        }
        if (migrationTask == null) {
            return;
        }

        int groupId = robot.getGroupId();
        Group group = idToGroups.get(groupId);
        int robotMigratedGroupId = robotMigrated.getGroupId();
        Group migratedGroup = idToGroups.get(robotMigratedGroupId);

        group.setGroupLoad(group.getGroupLoad()-migrationTask.getSize());
        migratedGroup.setGroupLoad(migratedGroup.getGroupLoad()+migrationTask.getSize());


    }

    private void updateIntra(Agent robot, Agent robotMigrated, Task migrationTask) {
        //更新迁移后的任务负载
        List<Task> tasksList = robot.getTasksList();
        tasksList.remove(migrationTask);
        robot.setLoad(robot.getLoad()-migrationTask.getSize());
        robot.setTasksList(tasksList);


        List<Task> robotMigratedTaskList = robotMigrated.getTasksList();
        if (robotMigratedTaskList==null) {
            robotMigratedTaskList = new ArrayList<>();
        }

        robotMigratedTaskList.add(migrationTask);
        robotMigrated.setLoad(robotMigrated.getLoad()+migrationTask.getSize());
        robotMigrated.setTasksList(robotMigratedTaskList);

    }
}
