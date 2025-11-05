"""
Supply Chain Network Analysis Module

This module provides theoretical analyses of the semiconductor supply chain:
1. Country/Region Dependency Analysis
2. Critical Node and Bottleneck Identification
3. Market Concentration Analysis (HHI Index)
4. Supply Chain Resilience Metrics
5. Stage-wise Analysis (Design, Fabrication, ATP)
6. Disruption Impact Simulation
"""

import sys
sys.path.append('python_src')

import pandas as pd
import numpy as np
import networkx as nx
from typing import Dict, List, Tuple, Set
from collections import defaultdict
import json


class SupplyChainAnalyzer:
    """Comprehensive supply chain network analyzer"""

    def __init__(self, network: nx.Graph, providers_df: pd.DataFrame,
                 inputs_df: pd.DataFrame, provision_df: pd.DataFrame,
                 stages_df: pd.DataFrame):
        self.network = network
        self.providers_df = providers_df
        self.inputs_df = inputs_df
        self.provision_df = provision_df
        self.stages_df = stages_df

        # Create provider ID mapping
        self.provider_info = {}
        for _, row in providers_df.iterrows():
            self.provider_info[row['provider_id']] = {
                'name': row['provider_name'],
                'type': row['provider_type'],
                'country': row['country']
            }

    def analyze_country_dependencies(self) -> Dict:
        """
        Analyze dependencies between countries in the supply chain.

        Returns dict with:
        - dependency_matrix: Country-to-country dependency strength
        - import_dependence: How much each country depends on imports
        - export_concentration: How concentrated each country's exports are
        - critical_relationships: Most critical country pairs
        """
        print("\n" + "="*70)
        print("Country Dependency Analysis")
        print("="*70)

        # Build country-to-country relationship matrix
        country_relationships = defaultdict(lambda: defaultdict(float))
        country_inputs = defaultdict(set)
        country_outputs = defaultdict(set)

        for _, prov in self.provision_df.iterrows():
            provider_id = prov['provider_id']
            input_id = prov['provided_id']
            share = prov.get('share_provided', 1.0) if pd.notna(prov.get('share_provided')) else 1.0

            if provider_id in self.provider_info:
                country = self.provider_info[provider_id]['country']
                country_inputs[country].add(input_id)

        # Find which countries provide which inputs
        input_to_countries = defaultdict(set)
        for _, prov in self.provision_df.iterrows():
            provider_id = prov['provider_id']
            input_id = prov['provided_id']

            if provider_id in self.provider_info and pd.notna(input_id):
                country = self.provider_info[provider_id]['country']
                input_to_countries[input_id].add(country)

        # Calculate dependencies based on sequence (what goes into what)
        if hasattr(self, 'sequence_df'):
            for _, seq in self.sequence_df.iterrows():
                input_from = seq.get('input_id')
                input_to = seq.get('goes_into_id')

                if pd.notna(input_from) and pd.notna(input_to):
                    countries_from = input_to_countries.get(input_from, set())
                    countries_to = input_to_countries.get(input_to, set())

                    # Countries providing input_from supply to countries needing input_to
                    for c_from in countries_from:
                        for c_to in countries_to:
                            if c_from != c_to:
                                country_relationships[c_to][c_from] += 1.0

        # Convert to matrix format
        all_countries = sorted(set(
            [info['country'] for info in self.provider_info.values() if pd.notna(info['country'])]
        ))

        dependency_matrix = pd.DataFrame(
            0.0, index=all_countries, columns=all_countries
        )

        for country_to, dependencies in country_relationships.items():
            for country_from, strength in dependencies.items():
                if country_to in all_countries and country_from in all_countries:
                    dependency_matrix.loc[country_to, country_from] = strength

        # Normalize by row (import perspective)
        row_sums = dependency_matrix.sum(axis=1)
        dependency_matrix_norm = dependency_matrix.div(row_sums, axis=0).fillna(0)

        # Calculate import dependence (how diversified are imports)
        import_dependence = {}
        for country in all_countries:
            deps = dependency_matrix_norm.loc[country]
            # Herfindahl index: sum of squared market shares
            hhi = (deps ** 2).sum()
            import_dependence[country] = hhi

        # Calculate export concentration
        export_concentration = {}
        for country in all_countries:
            exports = dependency_matrix_norm[country]
            hhi = (exports ** 2).sum()
            export_concentration[country] = hhi

        # Find critical relationships (top dependencies)
        critical_relationships = []
        for i, country_to in enumerate(all_countries):
            for j, country_from in enumerate(all_countries):
                if i != j:
                    strength = dependency_matrix_norm.loc[country_to, country_from]
                    if strength > 0:
                        critical_relationships.append({
                            'from': country_from,
                            'to': country_to,
                            'strength': strength
                        })

        critical_relationships.sort(key=lambda x: x['strength'], reverse=True)

        print(f"  ✓ Analyzed dependencies for {len(all_countries)} countries")
        print(f"  ✓ Found {len(critical_relationships)} supply relationships")

        return {
            'dependency_matrix': dependency_matrix_norm,
            'import_dependence': import_dependence,
            'export_concentration': export_concentration,
            'critical_relationships': critical_relationships[:20],  # Top 20
            'all_countries': all_countries
        }

    def identify_critical_nodes(self) -> Dict:
        """
        Identify critical nodes and bottlenecks in the supply chain.

        Returns dict with:
        - centrality_rankings: Nodes ranked by various centrality metrics
        - bottleneck_nodes: Nodes that would cause most disruption if removed
        - key_providers: Most important providers by role
        """
        print("\n" + "="*70)
        print("Critical Node Identification")
        print("="*70)

        # Calculate various centrality metrics
        degree_centrality = nx.degree_centrality(self.network)
        betweenness_centrality = nx.betweenness_centrality(self.network, weight='weight')

        try:
            closeness_centrality = nx.closeness_centrality(self.network, distance='weight')
        except:
            closeness_centrality = {}

        try:
            eigenvector_centrality = nx.eigenvector_centrality(self.network, weight='weight', max_iter=1000)
        except:
            eigenvector_centrality = {}

        # Combine centrality scores
        combined_rankings = []
        for node in self.network.nodes():
            if node in self.provider_info:
                score = (
                    degree_centrality.get(node, 0) * 0.25 +
                    betweenness_centrality.get(node, 0) * 0.35 +
                    closeness_centrality.get(node, 0) * 0.20 +
                    eigenvector_centrality.get(node, 0) * 0.20
                )

                combined_rankings.append({
                    'provider_id': node,
                    'provider_name': self.provider_info[node]['name'],
                    'country': self.provider_info[node]['country'],
                    'type': self.provider_info[node]['type'],
                    'combined_score': score,
                    'degree': degree_centrality.get(node, 0),
                    'betweenness': betweenness_centrality.get(node, 0),
                    'closeness': closeness_centrality.get(node, 0),
                    'eigenvector': eigenvector_centrality.get(node, 0)
                })

        combined_rankings.sort(key=lambda x: x['combined_score'], reverse=True)

        # Identify bottleneck nodes (high betweenness)
        bottleneck_nodes = sorted(
            combined_rankings,
            key=lambda x: x['betweenness'],
            reverse=True
        )[:15]

        # Identify key providers by country
        key_providers_by_country = defaultdict(list)
        for ranking in combined_rankings[:50]:
            country = ranking['country']
            key_providers_by_country[country].append(ranking)

        print(f"  ✓ Ranked {len(combined_rankings)} providers")
        print(f"  ✓ Identified {len(bottleneck_nodes)} critical bottleneck nodes")
        print(f"\nTop 5 Critical Nodes:")
        for i, node in enumerate(combined_rankings[:5], 1):
            print(f"    {i}. {node['provider_name']} ({node['country']}) - Score: {node['combined_score']:.4f}")

        return {
            'centrality_rankings': combined_rankings,
            'bottleneck_nodes': bottleneck_nodes,
            'key_providers_by_country': dict(key_providers_by_country)
        }

    def analyze_market_concentration(self) -> Dict:
        """
        Analyze market concentration using HHI (Herfindahl-Hirschman Index).

        Returns dict with:
        - input_concentration: HHI for each input (product/equipment)
        - stage_concentration: HHI for each supply chain stage
        - country_concentration: HHI for each country's market share
        - concentration_risk: Overall concentration risk assessment
        """
        print("\n" + "="*70)
        print("Market Concentration Analysis (HHI)")
        print("="*70)

        # Calculate HHI for each input
        input_concentration = {}
        for input_id in self.inputs_df['input_id'].unique():
            if pd.notna(input_id):
                # Get all providers for this input
                providers = self.provision_df[
                    self.provision_df['provided_id'] == input_id
                ]

                if len(providers) > 0:
                    # Calculate market shares
                    shares = providers['share_provided'].fillna(0).values
                    total = shares.sum()

                    if total > 0:
                        normalized_shares = shares / total
                        hhi = (normalized_shares ** 2).sum() * 10000  # HHI scaled to 0-10000
                    else:
                        hhi = 10000  # Maximum concentration (monopoly)

                    # Get input name
                    input_name = self.inputs_df[
                        self.inputs_df['input_id'] == input_id
                    ]['input_name'].values

                    input_concentration[input_name[0] if len(input_name) > 0 else str(input_id)] = hhi

        # Calculate HHI by stage
        stage_concentration = {}
        for stage_id in self.inputs_df['stage_id'].unique():
            if pd.notna(stage_id):
                # Get inputs in this stage
                stage_inputs = self.inputs_df[
                    self.inputs_df['stage_id'] == stage_id
                ]['input_id'].values

                # Get all provisions for these inputs
                stage_provisions = self.provision_df[
                    self.provision_df['provided_id'].isin(stage_inputs)
                ]

                # Calculate country-level concentration for this stage
                country_shares = defaultdict(float)
                for _, prov in stage_provisions.iterrows():
                    provider_id = prov['provider_id']
                    share = prov.get('share_provided', 1.0)

                    if provider_id in self.provider_info:
                        country = self.provider_info[provider_id]['country']
                        country_shares[country] += share if pd.notna(share) else 1.0

                # Calculate HHI
                total = sum(country_shares.values())
                if total > 0:
                    normalized_shares = np.array(list(country_shares.values())) / total
                    hhi = (normalized_shares ** 2).sum() * 10000
                else:
                    hhi = 0

                # Get stage name
                stage_name = self.inputs_df[
                    self.inputs_df['stage_id'] == stage_id
                ]['stage_name'].values
                stage_concentration[stage_name[0] if len(stage_name) > 0 else str(stage_id)] = hhi

        # Calculate country concentration across all inputs
        country_concentration = {}
        country_total_shares = defaultdict(float)

        for _, prov in self.provision_df.iterrows():
            provider_id = prov['provider_id']
            share = prov.get('share_provided', 1.0)

            if provider_id in self.provider_info:
                country = self.provider_info[provider_id]['country']
                country_total_shares[country] += share if pd.notna(share) else 1.0

        total = sum(country_total_shares.values())
        for country, share in country_total_shares.items():
            country_concentration[country] = (share / total * 100) if total > 0 else 0

        # Assess concentration risk
        high_concentration_inputs = {
            k: v for k, v in input_concentration.items() if v > 2500  # HHI > 2500 is highly concentrated
        }

        risk_assessment = {
            'overall_risk': 'High' if len(high_concentration_inputs) > len(input_concentration) * 0.3 else 'Moderate',
            'high_concentration_count': len(high_concentration_inputs),
            'total_inputs': len(input_concentration),
            'average_hhi': np.mean(list(input_concentration.values())) if input_concentration else 0
        }

        print(f"  ✓ Analyzed concentration for {len(input_concentration)} inputs")
        print(f"  ✓ Average HHI: {risk_assessment['average_hhi']:.0f}")
        print(f"  ✓ High concentration inputs: {len(high_concentration_inputs)}")
        print(f"  ✓ Overall risk: {risk_assessment['overall_risk']}")

        return {
            'input_concentration': input_concentration,
            'stage_concentration': stage_concentration,
            'country_concentration': country_concentration,
            'high_concentration_inputs': high_concentration_inputs,
            'risk_assessment': risk_assessment
        }

    def analyze_supply_chain_resilience(self) -> Dict:
        """
        Analyze supply chain resilience and vulnerability.

        Returns dict with:
        - network_robustness: Robustness to node removal
        - alternative_paths: Availability of alternative supply paths
        - single_point_failures: Critical single points of failure
        - resilience_score: Overall resilience metric
        """
        print("\n" + "="*70)
        print("Supply Chain Resilience Analysis")
        print("="*70)

        # Network robustness: connectivity after removing nodes
        original_components = nx.number_connected_components(self.network)
        original_diameter = nx.diameter(self.network) if nx.is_connected(self.network) else float('inf')

        # Test removing top nodes
        node_removal_impact = []
        top_nodes = sorted(
            self.network.degree(),
            key=lambda x: x[1],
            reverse=True
        )[:20]

        for node, degree in top_nodes:
            # Create network without this node
            G_temp = self.network.copy()
            G_temp.remove_node(node)

            new_components = nx.number_connected_components(G_temp)
            connectivity_impact = new_components - original_components

            if node in self.provider_info:
                node_removal_impact.append({
                    'provider_id': node,
                    'provider_name': self.provider_info[node]['name'],
                    'country': self.provider_info[node]['country'],
                    'degree': degree,
                    'connectivity_impact': connectivity_impact,
                    'is_critical': connectivity_impact > 0
                })

        # Find single points of failure (articulation points)
        articulation_points = list(nx.articulation_points(self.network))
        spof_details = []

        for node in articulation_points:
            if node in self.provider_info:
                spof_details.append({
                    'provider_id': node,
                    'provider_name': self.provider_info[node]['name'],
                    'country': self.provider_info[node]['country'],
                    'type': 'Articulation Point'
                })

        # Calculate path redundancy
        # Sample random pairs and check number of paths
        nodes = list(self.network.nodes())
        path_redundancy = []

        if len(nodes) > 10:
            for _ in range(min(50, len(nodes))):
                source = np.random.choice(nodes)
                target = np.random.choice(nodes)

                if source != target:
                    try:
                        # Count number of simple paths (limited to avoid explosion)
                        paths = list(nx.all_simple_paths(
                            self.network, source, target, cutoff=5
                        ))
                        path_redundancy.append(len(paths))
                    except:
                        path_redundancy.append(0)

        avg_path_redundancy = np.mean(path_redundancy) if path_redundancy else 0

        # Calculate resilience score
        resilience_score = (
            (1 - len(articulation_points) / len(self.network.nodes())) * 0.4 +
            min(avg_path_redundancy / 5, 1.0) * 0.3 +
            (1 - len([x for x in node_removal_impact if x['is_critical']]) / len(node_removal_impact)) * 0.3
        ) if len(self.network.nodes()) > 0 else 0

        print(f"  ✓ Network components: {original_components}")
        print(f"  ✓ Single points of failure: {len(articulation_points)}")
        print(f"  ✓ Average path redundancy: {avg_path_redundancy:.2f}")
        print(f"  ✓ Resilience score: {resilience_score:.3f}")

        return {
            'network_robustness': {
                'original_components': original_components,
                'original_diameter': original_diameter if original_diameter != float('inf') else None
            },
            'node_removal_impact': node_removal_impact,
            'single_point_failures': spof_details,
            'alternative_paths': {
                'average_redundancy': avg_path_redundancy,
                'samples_tested': len(path_redundancy)
            },
            'resilience_score': resilience_score
        }

    def analyze_by_stage(self) -> Dict:
        """
        Analyze supply chain by stage (Design, Fabrication, ATP).

        Returns dict with:
        - stage_statistics: Statistics for each stage
        - stage_dependencies: Dependencies between stages
        - stage_vulnerabilities: Vulnerabilities in each stage
        """
        print("\n" + "="*70)
        print("Supply Chain Stage Analysis")
        print("="*70)

        stage_statistics = {}

        for _, stage in self.stages_df.iterrows():
            stage_id = stage['stage_id']
            stage_name = stage['stage_name']

            # Get inputs in this stage
            stage_inputs = self.inputs_df[
                self.inputs_df['stage_id'] == stage_id
            ]

            # Get providers for this stage
            stage_input_ids = stage_inputs['input_id'].values
            stage_provisions = self.provision_df[
                self.provision_df['provided_id'].isin(stage_input_ids)
            ]

            # Count unique providers
            unique_providers = stage_provisions['provider_id'].nunique()

            # Count unique countries
            provider_ids = stage_provisions['provider_id'].unique()
            countries = set()
            for pid in provider_ids:
                if pid in self.provider_info:
                    countries.add(self.provider_info[pid]['country'])

            stage_statistics[stage_name] = {
                'stage_id': stage_id,
                'num_inputs': len(stage_inputs),
                'num_providers': unique_providers,
                'num_countries': len(countries),
                'countries': sorted(list(countries))
            }

        print(f"  ✓ Analyzed {len(stage_statistics)} stages")
        for stage_name, stats in stage_statistics.items():
            print(f"    - {stage_name}: {stats['num_inputs']} inputs, "
                  f"{stats['num_providers']} providers, {stats['num_countries']} countries")

        return {
            'stage_statistics': stage_statistics
        }

    def run_full_analysis(self) -> Dict:
        """Run all analyses and return comprehensive results"""
        print("\n" + "="*80)
        print(" "*20 + "SUPPLY CHAIN NETWORK ANALYSIS")
        print(" "*25 + "Theoretical Framework")
        print("="*80)

        results = {
            'country_dependencies': self.analyze_country_dependencies(),
            'critical_nodes': self.identify_critical_nodes(),
            'market_concentration': self.analyze_market_concentration(),
            'resilience': self.analyze_supply_chain_resilience(),
            'stage_analysis': self.analyze_by_stage()
        }

        print("\n" + "="*80)
        print("✓ Full Supply Chain Analysis Complete")
        print("="*80)

        return results

    def export_results(self, results: Dict, output_file: str = "supply_chain_analysis.json"):
        """Export analysis results to JSON"""
        # Convert non-serializable objects
        serializable_results = self._make_serializable(results)

        with open(output_file, 'w') as f:
            json.dump(serializable_results, f, indent=2)

        print(f"\n✓ Analysis results exported to: {output_file}")

    def _make_serializable(self, obj):
        """Convert objects to JSON-serializable format"""
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict()
        elif isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif pd.isna(obj):
            return None
        else:
            return obj
