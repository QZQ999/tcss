"""
Semiconductor Supply Chain Network Builder

This module constructs a network-based experimental setup from semiconductor
supply chain data, including:
- Network topology based on provider-input relationships
- Task generation from semiconductor components
- Agent (robot) generation from providers
- Graph construction from provision relationships
"""

import pandas as pd
import networkx as nx
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, List
import json


class SemiconductorNetworkBuilder:
    """Build network experiment inputs from semiconductor supply chain data."""

    def __init__(self, data_dir: str = "data"):
        """
        Initialize the network builder.

        Args:
            data_dir: Directory containing semiconductor data CSV files
        """
        self.data_dir = Path(data_dir)
        self.providers_df = None
        self.inputs_df = None
        self.provision_df = None
        self.stages_df = None
        self.sequence_df = None
        self.network = None

    def load_data(self):
        """Load all semiconductor supply chain data."""
        print("Loading semiconductor supply chain data...")

        self.providers_df = pd.read_csv(self.data_dir / "providers.csv")
        self.inputs_df = pd.read_csv(self.data_dir / "inputs.csv")
        self.provision_df = pd.read_csv(self.data_dir / "provision.csv")
        self.stages_df = pd.read_csv(self.data_dir / "stages.csv")
        self.sequence_df = pd.read_csv(self.data_dir / "sequence.csv")

        print(f"  - Loaded {len(self.providers_df)} providers")
        print(f"  - Loaded {len(self.inputs_df)} inputs")
        print(f"  - Loaded {len(self.provision_df)} provision relationships")
        print(f"  - Loaded {len(self.stages_df)} stages")
        print(f"  - Loaded {len(self.sequence_df)} sequences")

    def build_network(self) -> nx.Graph:
        """
        Build network graph from semiconductor supply chain.

        Network structure:
        - Nodes represent providers (companies/countries)
        - Edges represent supply relationships (weighted by market share)
        - Edge weights inversely related to market share (stronger connections = lower weight)

        Returns:
            NetworkX graph object
        """
        print("\nBuilding network graph...")

        G = nx.Graph()

        # Add provider nodes with attributes
        for _, provider in self.providers_df.iterrows():
            G.add_node(
                provider['provider_id'],
                name=provider['provider_name'],
                type=provider['provider_type'],
                country=provider['country']
            )

        # Build edges based on provision relationships
        # Providers that supply the same input are connected
        input_to_providers = {}

        for _, prov in self.provision_df.iterrows():
            input_id = prov['provided_id']
            provider_id = prov['provider_id']
            share = prov.get('share_provided', 1.0)

            if pd.notna(input_id) and pd.notna(provider_id):
                if input_id not in input_to_providers:
                    input_to_providers[input_id] = []
                input_to_providers[input_id].append({
                    'provider_id': provider_id,
                    'share': share if pd.notna(share) else 1.0
                })

        # Connect providers that work on same inputs (supply chain partners)
        edge_weights = {}
        for input_id, providers in input_to_providers.items():
            for i, p1 in enumerate(providers):
                for p2 in providers[i+1:]:
                    id1, id2 = p1['provider_id'], p2['provider_id']
                    if id1 != id2 and id1 in G.nodes and id2 in G.nodes:
                        # Edge weight based on combined market share
                        # Higher market share = stronger connection = lower weight
                        combined_share = (p1['share'] + p2['share']) / 2
                        weight = max(1.0, 10.0 - combined_share * 9.0)

                        edge_key = tuple(sorted([id1, id2]))
                        if edge_key not in edge_weights:
                            edge_weights[edge_key] = []
                        edge_weights[edge_key].append(weight)

        # Add edges with averaged weights
        for (id1, id2), weights in edge_weights.items():
            avg_weight = np.mean(weights)
            G.add_edge(id1, id2, weight=avg_weight)

        # Ensure network connectivity - connect isolated components
        if not nx.is_connected(G):
            print("  - Network is disconnected, connecting components...")
            components = list(nx.connected_components(G))
            for i in range(len(components) - 1):
                # Connect largest node from each component
                node1 = max(components[i], key=lambda n: G.degree(n) if G.degree(n) > 0 else 0)
                node2 = max(components[i+1], key=lambda n: G.degree(n) if G.degree(n) > 0 else 0)
                G.add_edge(node1, node2, weight=5.0)

        self.network = G

        print(f"  - Network built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        print(f"  - Network is connected: {nx.is_connected(G)}")

        return G

    def generate_tasks(self, output_file: str = "Task_semiconductor.txt") -> List[Dict]:
        """
        Generate tasks from semiconductor inputs.

        Each task represents a semiconductor component/process that needs to be handled.
        Task properties:
        - task_id: unique identifier
        - size: based on market size and complexity
        - arrive_time: staggered arrival based on supply chain stage

        Args:
            output_file: Output file path for tasks

        Returns:
            List of task dictionaries
        """
        print("\nGenerating tasks from semiconductor inputs...")

        tasks = []
        task_id = 0

        # Sort inputs by stage for logical arrival times
        inputs_sorted = self.inputs_df.sort_values('stage_id')

        for idx, inp in inputs_sorted.iterrows():
            # Task size based on input type and market importance
            # Use a combination of factors to determine size
            base_size = 10.0

            # Adjust size based on stage (later stages are more complex)
            # Handle missing or NaN stage_id
            if pd.notna(inp['stage_id']) and isinstance(inp['stage_id'], str):
                stage_multiplier = float(inp['stage_id'].replace('S', ''))
            else:
                # Default to stage 2 if missing
                stage_multiplier = 2.0

            # Random variation for realism
            size = base_size * stage_multiplier * np.random.uniform(0.8, 1.5)
            size = round(size, 2)

            # Arrival time based on stage (earlier stages arrive first)
            arrive_time = (task_id % 10) + int((stage_multiplier - 1) * 5)
            arrive_time = int(arrive_time)

            # Get stage name, handle NaN
            stage_name = inp['stage_name'] if pd.notna(inp['stage_name']) else 'Unknown'

            tasks.append({
                'task_id': task_id,
                'size': size,
                'arrive_time': arrive_time,
                'input_name': inp['input_name'],
                'stage': stage_name
            })

            task_id += 1

        # Write tasks to file in required format: task_id size arrive_time
        output_path = Path(output_file)
        with open(output_path, 'w') as f:
            for task in tasks:
                f.write(f"{task['task_id']} {task['size']} {task['arrive_time']}\n")

        print(f"  - Generated {len(tasks)} tasks")
        print(f"  - Tasks written to {output_file}")

        return tasks

    def generate_agents(self, output_file: str = "RobotsInformation_semiconductor.txt",
                       num_groups: int = 10) -> List[Dict]:
        """
        Generate agents (robots) from providers.

        Each agent represents a provider's capacity to handle semiconductor tasks.
        Agent properties:
        - robot_id: unique identifier (maps to provider_id)
        - capacity: based on provider type and market presence
        - group_id: assigned based on geographic/organizational clustering

        Args:
            output_file: Output file path for agents
            num_groups: Number of groups to organize agents into

        Returns:
            List of agent dictionaries
        """
        print("\nGenerating agents from providers...")

        agents = []

        # Filter providers that are in the network
        if self.network is None:
            raise ValueError("Network must be built before generating agents")

        network_provider_ids = set(self.network.nodes())
        providers_in_network = self.providers_df[
            self.providers_df['provider_id'].isin(network_provider_ids)
        ]

        # Assign groups based on clustering (could use geographic or type-based)
        # For simplicity, use community detection on the network
        if len(self.network.nodes()) > 0:
            try:
                # Use community detection for group assignment
                communities = nx.community.greedy_modularity_communities(self.network)
                provider_to_group = {}
                for group_id, community in enumerate(communities[:num_groups]):
                    for provider_id in community:
                        provider_to_group[provider_id] = group_id
            except:
                # Fallback: assign groups randomly
                provider_ids = list(network_provider_ids)
                provider_to_group = {
                    pid: i % num_groups for i, pid in enumerate(provider_ids)
                }
        else:
            provider_to_group = {}

        for _, provider in providers_in_network.iterrows():
            provider_id = provider['provider_id']

            # Capacity based on provider type
            if provider['provider_type'] == 'Country':
                # Countries have higher capacity
                capacity = np.random.uniform(80, 150)
            else:
                # Companies have variable capacity
                capacity = np.random.uniform(30, 100)

            capacity = round(capacity, 2)

            # Assign group
            group_id = provider_to_group.get(provider_id, 0)

            agents.append({
                'robot_id': provider_id,
                'capacity': capacity,
                'group_id': group_id,
                'provider_name': provider['provider_name'],
                'country': provider['country']
            })

        # Write agents to file in required format: robot_id capacity group_id
        output_path = Path(output_file)
        with open(output_path, 'w') as f:
            for agent in agents:
                f.write(f"{agent['robot_id']} {agent['capacity']} {agent['group_id']}\n")

        print(f"  - Generated {len(agents)} agents")
        print(f"  - Organized into {num_groups} groups")
        print(f"  - Agents written to {output_file}")

        return agents

    def generate_graph(self, output_file: str = "Graph_semiconductor.txt"):
        """
        Generate graph topology file from network.

        Graph format: node1 node2 weight (one edge per line)

        Args:
            output_file: Output file path for graph
        """
        print("\nGenerating graph topology file...")

        if self.network is None:
            raise ValueError("Network must be built before generating graph")

        output_path = Path(output_file)
        with open(output_path, 'w') as f:
            for u, v, data in self.network.edges(data=True):
                weight = data.get('weight', 1.0)
                f.write(f"{u} {v} {weight}\n")

        print(f"  - Graph written to {output_file}")
        print(f"  - {self.network.number_of_edges()} edges exported")

    def generate_metadata(self, output_file: str = "semiconductor_metadata.json"):
        """
        Generate metadata file with information about the generated experiment.

        Args:
            output_file: Output file path for metadata
        """
        print("\nGenerating metadata...")

        if self.network is None:
            raise ValueError("Network must be built before generating metadata")

        metadata = {
            'description': 'Semiconductor supply chain network experiment',
            'data_source': 'CSET Semiconductor Supply Chain Dataset',
            'network': {
                'num_nodes': self.network.number_of_nodes(),
                'num_edges': self.network.number_of_edges(),
                'is_connected': nx.is_connected(self.network),
                'avg_degree': sum(dict(self.network.degree()).values()) / self.network.number_of_nodes()
            },
            'providers': {
                'total': len(self.providers_df),
                'countries': self.providers_df['country'].nunique(),
                'types': self.providers_df['provider_type'].value_counts().to_dict()
            },
            'inputs': {
                'total': len(self.inputs_df),
                'stages': self.inputs_df['stage_name'].value_counts().to_dict()
            },
            'provision_relationships': len(self.provision_df)
        }

        with open(output_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"  - Metadata written to {output_file}")

    def build_complete_experiment(self, output_prefix: str = "semiconductor"):
        """
        Build complete experiment setup with all required files.

        Args:
            output_prefix: Prefix for all output files
        """
        print("="*70)
        print("Building Complete Semiconductor Supply Chain Experiment")
        print("="*70)

        # Load data
        self.load_data()

        # Build network
        self.build_network()

        # Generate all required files
        tasks = self.generate_tasks(f"Task_{output_prefix}.txt")
        agents = self.generate_agents(f"RobotsInformation_{output_prefix}.txt")
        self.generate_graph(f"Graph_{output_prefix}.txt")
        self.generate_metadata(f"{output_prefix}_metadata.json")

        print("\n" + "="*70)
        print("Experiment Setup Complete!")
        print("="*70)
        print(f"\nGenerated files:")
        print(f"  1. Task_{output_prefix}.txt - {len(tasks)} tasks")
        print(f"  2. RobotsInformation_{output_prefix}.txt - {len(agents)} agents")
        print(f"  3. Graph_{output_prefix}.txt - {self.network.number_of_edges()} edges")
        print(f"  4. {output_prefix}_metadata.json - experiment metadata")

        return {
            'tasks': tasks,
            'agents': agents,
            'network': self.network
        }


def main():
    """Main function to build semiconductor network experiment."""
    builder = SemiconductorNetworkBuilder(data_dir="data")
    result = builder.build_complete_experiment(output_prefix="semiconductor")

    print("\n✓ Semiconductor supply chain experiment ready to run!")


if __name__ == "__main__":
    main()
