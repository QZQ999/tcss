package input;

import lombok.Data;

import java.util.List;
import java.util.Set;

@Data
public class Group {
    private int groupId;
    private double groupLoad;
    private Agent leader;
    private Set<Integer> robotIdInGroup;
    private List<Task> assignedTasks;
    private double groupCapacity;
    private List<Agent> adLeaders;
    private double interactionLevel ;
}
