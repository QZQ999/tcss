# HGTM Algorithm - Python Implementation

This is a Python implementation of the HGTM (Hierarchical Group Task Migration) algorithm, converted from the original Java codebase.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Algorithm

```bash
python main.py
```

## Project Structure

```
tcss/
├── main.py                          # Main entry point
├── requirements.txt                 # Python dependencies
├── python_src/                      # Python source code
│   ├── input/                       # Input data handling
│   │   ├── agent.py                # Agent/Robot class
│   │   ├── task.py                 # Task class
│   │   ├── group.py                # Group class
│   │   ├── reader.py               # File reader
│   │   └── ...
│   ├── main/                        # Main utilities
│   │   ├── function.py             # Utility functions
│   │   └── initialize.py           # Initialization logic
│   ├── hgtm/                        # HGTM algorithm implementation
│   │   ├── hgtm.py                 # Main HGTM algorithm
│   │   ├── finder_leader.py        # Leader selection
│   │   ├── groupform.py            # Group formation
│   │   └── ...
│   ├── mpftm/                       # MPFTM supporting algorithms
│   │   ├── calculate_pon_field.py  # Potential field calculation
│   │   └── ...
│   └── evaluation/                  # Evaluation metrics
│       ├── evaluation.py           # Main evaluation
│       └── ...
├── Task24.txt                       # Task input file
├── RobotsInformation4.txt          # Robot configuration file
└── Graph4.txt                       # Network graph file
```

## Input Files

The algorithm reads three types of input files:

1. **Task File** (e.g., `Task24.txt`): Contains task information
   - Format: `task_id size arrive_time`

2. **Robot File** (e.g., `RobotsInformation4.txt`): Contains robot/agent information
   - Format: `robot_id capacity group_id`

3. **Graph File** (e.g., `Graph4.txt`): Contains network topology
   - Format: `node1 node2 weight`

## Algorithm Overview

The HGTM algorithm performs hierarchical task migration in multi-robot systems:

1. **Initialization**: Assigns initial tasks to robots
2. **Leader Selection**: Selects leader nodes for each group
3. **Backup Leader Selection**: Selects backup leaders for fault tolerance
4. **Potential Field Calculation**: Calculates attractive and repulsive potential fields
5. **Group Formation**: Forms groups of faulty agents
6. **Task Migration**: Migrates tasks based on potential fields

## Output

The algorithm outputs:
- Mean execution cost
- Mean migration cost
- Mean survival rate
- Robot capacity statistics
- Task size statistics
- Target optimization value

## Key Differences from Java Version

1. Uses `networkx` instead of JGraphT for graph operations
2. Python class structure with getter/setter methods
3. Native Python data structures (dict, list, set)
4. Simplified imports and package structure

## Requirements

- Python 3.7+
- NetworkX 2.6.3+

## License

Same as the original Java implementation.
