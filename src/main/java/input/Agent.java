package input;

import lombok.Data;

import java.util.List;

@Data
public class Agent {
    private int robotId;
    private double capacity;
    private double  load;
    private List<Task> tasksList;
    private int groupId;
    private double faultA;
    //faultA为功能故障
    private double faultO;
    //faultA为过载故障
}
