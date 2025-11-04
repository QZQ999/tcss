package HGTM;

import input.Group;
import input.Agent;
import main.Function;
import org.jgrapht.alg.interfaces.ShortestPathAlgorithm;
import org.jgrapht.graph.DefaultUndirectedWeightedGraph;
import org.jgrapht.graph.DefaultWeightedEdge;

import java.util.*;

/**
 * @author Liu tianyi
 */
public class Groupform {
    private DefaultUndirectedWeightedGraph<Integer, DefaultWeightedEdge> arcGraph;
    private HashMap<Integer, Group> idToGroups;
    private HashMap<Integer, Agent> idToAgents;
    private ShortestPathAlgorithm<Integer, DefaultWeightedEdge> shortestPath ;
    Double a;
    Double b;
    List<List<Agent>> bags = new ArrayList<>();
    Map<List<Agent>,Agent> bagsToAgent = new HashMap<>();

    public Groupform(DefaultUndirectedWeightedGraph<Integer, DefaultWeightedEdge> arcGraph, HashMap<Integer, Group> idToGroups,
                     HashMap<Integer, Agent> idToAgents, ShortestPathAlgorithm<Integer, DefaultWeightedEdge> shortestPath, Double a, Double b) {
        this.arcGraph = arcGraph;
        this.idToGroups = idToGroups;
        this.idToAgents = idToAgents;
        this.shortestPath = shortestPath;
        this.a = a;
        this.b = b;
        for (Integer id : idToAgents.keySet()) {
            List<Agent> bag =new ArrayList<>();
            Agent e = idToAgents.get(id);
            if (e.getFaultA()==1) {
                bag.add(e);
                bags.add(bag);
            }
        }
    }
    public Map<List<Agent>,Agent> run() {
        IntraBagform();
        //InterBagform();
        Map<List<Agent>,Agent> bagsToAgentReturn = new HashMap<>();
        for (List<Agent> bag : bags) {
            bagsToAgentReturn.put(bag,bagsToAgent.get(bag));
        }
        return bagsToAgentReturn;
    }

    Comparator<List<Agent>> CompareBag= new Comparator<List<Agent>>() {
        @Override
        public int compare(List<Agent> o1, List<Agent> o2) {
            int size1 = 0;
            int size2 = 0;
            for (Agent agent : o1) {
                size1+=agent.getTasksList().size();
            }
            for (Agent agent : o2) {
                size2+=agent.getTasksList().size();
            }

            return size2-size1;
        }
    };


    private void IntraBagform(){
        //进行网络层内的组件打包
        PriorityQueue<List<Agent>> pq = new PriorityQueue<>(CompareBag);
        pq.addAll(bags);
        List<List<Agent>> temp = new ArrayList<>();
        //用来容纳 无法再无法再通过合并的方式扩大的任务组
        while (!pq.isEmpty()) {
            List<Agent> bagM = pq.poll();
            int flag = 0;
            PriorityQueue<List<Agent>> pqTemp = new PriorityQueue<>(pq);
            int size = pqTemp.size();
            //flag 和size用于判断 是否该包已经无法再通过合并的方式
            while (!pqTemp.isEmpty()) {
                List<Agent> bagN = pqTemp.poll();
                if (bagN==null) {
                    continue;
                }
                List<Agent> bagTemp = new ArrayList<>(bagN);
                bagTemp.addAll(bagM);
                if (BenIntra(bagTemp)>(BenIntra(bagN)+ BenIntra(bagM))) {
                    pq.offer(bagTemp);
                    bagsToAgent.remove(bagM);
                    bagsToAgent.remove(bagN);
                } else {
                    flag++;
                }
            }
            if (flag==size) {
                temp.add(bagM);
            }
        }
        bags = new ArrayList<>(temp);
    }

    private void InterBagform() {
        //进行网络层间的组件打包
        PriorityQueue<List<Agent>> pq = new PriorityQueue<>(CompareBag);
        pq.addAll(bags);
        List<List<Agent>> temp = new ArrayList<>();
        //用来容纳 无法再无法再通过合并的方式扩大的任务组
        while (!pq.isEmpty()) {
            List<Agent> bagM = pq.poll();
            int flag = 0;
            PriorityQueue<List<Agent>> pqTemp = new PriorityQueue<>(pq);
            int size = pqTemp.size();
            //flag 和size用于判断 是否该包已经无法再通过合并的方式
            while (!pqTemp.isEmpty()) {
                List<Agent> bagN = pqTemp.poll();
                if (bagN==null) {
                    continue;
                }
                List<Agent> bagTemp = new ArrayList<>(bagN);
                bagTemp.addAll(bagM);
                if (BenInter(bagTemp)>(BenInter(bagN)+ BenInter(bagM))) {
                    pq.offer(bagTemp);
                    bagsToAgent.remove(bagM);
                    bagsToAgent.remove(bagN);
                }else {
                    flag++;
                }
                if (flag==size) {
                    temp.add(bagM);
                }
            }
        }
        bags = new ArrayList<>(temp);
    }

    private Double BenIntra(List<Agent> bagTemp) {
        Double benIntraValue = Double.MIN_VALUE;
        List<Agent> neighbors = new ArrayList<>();
        for (Agent agent : bagTemp) {
            Set<DefaultWeightedEdge> defaultWeightedEdges = arcGraph.edgesOf(agent.getRobotId());
            for (DefaultWeightedEdge defaultWeightedEdge : defaultWeightedEdges) {
                Agent e = idToAgents.get(arcGraph.getEdgeTarget(defaultWeightedEdge));
                if (e.getGroupId()!=agent.getGroupId()||e.getFaultA()==1) {
                    continue;
                }
                neighbors.add(e);
            }
        }
        Agent target = null;
        for (Agent neighbor : neighbors) {
            double benIntraTemp = benIntra(bagTemp, neighbor);
            if (benIntraTemp >benIntraValue) {
                benIntraValue  = benIntraTemp;
                target = neighbor;
            }
        }
        bagsToAgent.put(bagTemp,target);
        return benIntraValue;
    }
    /*
       计算将任务包bagTemp同层迁移给临近节点neighbor的收益函数
     */
    private Double benIntra(List<Agent> bagTemp, Agent neighbor) {
        Group group = idToGroups.get(neighbor.getGroupId());
        double interactionLevel = group.getInteractionLevel();
        double meanC = 0.0;
        //任务完成成本增加比例的分子部分
        Double CostDenominator = 0.0;
        //任务完成成本增加比例的分母部分
        int count = 0;
        Set<DefaultWeightedEdge> defaultWeightedEdges = arcGraph.edgesOf(neighbor.getRobotId());
        for (DefaultWeightedEdge defaultWeightedEdge : defaultWeightedEdges) {
            Agent e = idToAgents.get(arcGraph.getEdgeTarget(defaultWeightedEdge));
            if (e.getGroupId()!=neighbor.getGroupId()) {
                continue;
            }
            CostDenominator+=arcGraph.getEdgeWeight(defaultWeightedEdge)*e.getTasksList().size();
            count++;
            //count用来表示目标agent neighbor有多少个临近节点
            meanC+=e.getLoad()/e.getCapacity();
        }
        CostDenominator/=count;
        Double loadInBag = 0.0;
        for (Agent agent : bagTemp) {
            CostDenominator+=agent.getLoad();
            loadInBag+=agent.getLoad();
        }

        for (Agent agent : bagTemp) {
            DefaultWeightedEdge weightedEdge = arcGraph.getEdge(agent.getRobotId(), neighbor.getRobotId());
            if (weightedEdge==null) {
                continue;
            }
            CostDenominator+=arcGraph.getEdgeWeight(weightedEdge);
        }
        Double CostIncreaseP = CostDenominator/meanC;
        Function function = new Function(idToAgents,idToGroups);


        Double CompleteP = 1-Math.max(function.sig(loadInBag) * interactionLevel, 0.5);
        return b*CompleteP-a*CostIncreaseP;

    }



    private Double BenInter(List<Agent> bagTemp) {
        Double benInterValue = Double.MIN_VALUE;
        List<Agent> neighbors = new ArrayList<>();
        for (Agent agent : bagTemp) {
            Set<DefaultWeightedEdge> defaultWeightedEdges = arcGraph.edgesOf(agent.getRobotId());
            for (DefaultWeightedEdge defaultWeightedEdge : defaultWeightedEdges) {
                Agent e = idToAgents.get(arcGraph.getEdgeTarget(defaultWeightedEdge));
                if (e.getGroupId()!=agent.getGroupId()) {
                    continue;
                }
                neighbors.add(e);
            }
        }
        Agent target = new Agent();
        for (Agent neighbor : neighbors) {
            double benIntraTemp = benInter(bagTemp, neighbor);
            if (benIntraTemp >benInterValue) {
                benInterValue  = benIntraTemp;
            }
        }
        bagsToAgent.put(bagTemp,target);
        return benInterValue;
    }
/*
   计算将任务包bagTemp跨层迁移给临近节点neighbor的收益函数
 */
    private Double benInter(List<Agent> bagTemp, Agent neighbor) {
        Double meanC = 0.0;
        //任务完成成本增加比例的分子部分
        Double CostDenominator = 0.0;
        //任务完成成本增加比例的分母部分
        int count = 0;
        Set<DefaultWeightedEdge> defaultWeightedEdges = arcGraph.edgesOf(neighbor.getRobotId());
        for (DefaultWeightedEdge defaultWeightedEdge : defaultWeightedEdges) {
            Agent e = idToAgents.get(arcGraph.getEdgeTarget(defaultWeightedEdge));
            CostDenominator+=arcGraph.getEdgeWeight(defaultWeightedEdge)*e.getTasksList().size();
            count++;
            //count用来表示目标agent neighbor有多少个临近节点
            meanC+=e.getLoad()/e.getCapacity();
        }
        CostDenominator/=count;
        Double loadInBag = 0.0;
        for (Agent agent : bagTemp) {
            CostDenominator+=agent.getLoad();
            loadInBag+=agent.getLoad();
        }

        for (Agent agent : bagTemp) {
            DefaultWeightedEdge weightedEdge = arcGraph.getEdge(agent.getRobotId(), neighbor.getRobotId());
            if (weightedEdge==null) {
                continue;
            }
            CostDenominator+=arcGraph.getEdgeWeight(weightedEdge);
        }
        Double CostIncreaseP = CostDenominator/meanC;
        Function function = new Function(idToAgents,idToGroups);


        Double CompleteP = 1-Math.max(function.sig(loadInBag), 0.5);
        return b*CompleteP-a*CostIncreaseP;
    }
}