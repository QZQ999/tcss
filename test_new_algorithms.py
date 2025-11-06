"""
Quick test script for new algorithms (GBMA, MMLMA, MPFTM)
"""

import sys
from python_src.input.reader import *
from python_src.main.initialize import *
from python_src.gbma.gbma import GBMA
from python_src.mmlma.mmlma import MMLMA
from python_src.mpftm.mpftm import MPFTM


def test_algorithm(algorithm_name, AlgorithmClass):
    """Test a single algorithm"""
    print(f"\n{'='*60}")
    print(f"Testing {algorithm_name}")
    print(f"{'='*60}")

    try:
        # Read data
        print("Reading data files...")
        tasks = read_task("Task_semiconductor.txt")
        robots_load = read_robot("RobotsInformation_semiconductor.txt")
        graph = read_graph("Graph_semiconductor.txt")

        print(f"  - Tasks: {len(tasks)}")
        print(f"  - Robots: {len(robots_load)}")
        print(f"  - Graph nodes: {graph.number_of_nodes()}")

        # Initialize
        print("Initializing...")
        initial_result = initialization(robots_load, tasks, 0.3)
        robots_load = initial_result[0]
        tasks_all_migration = initial_result[1]
        robots_fault_set = initial_result[2]

        print(f"  - Faulty robots: {len(robots_fault_set)}")

        # Run algorithm
        print(f"Running {algorithm_name}...")
        algo = AlgorithmClass(tasks_all_migration, graph, robots_load, 0.1, 0.9)

        # Get the appropriate run method
        if algorithm_name == "GBMA":
            result = algo.gbma_run()
        elif algorithm_name == "MMLMA":
            result = algo.mmlma_run()
        elif algorithm_name == "MPFTM":
            result = algo.mpftm_run()

        print(f"\n✓ {algorithm_name} completed successfully!")
        print(f"  - Migration Cost: {result.get_mean_migration_cost():.4f}")
        print(f"  - Execution Cost: {result.get_mean_execute_cost():.4f}")
        print(f"  - Survival Rate: {result.get_mean_survival_rate():.4f}")

        return True

    except Exception as e:
        print(f"\n✗ {algorithm_name} failed with error:")
        print(f"  {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run quick tests for all new algorithms"""
    print("\n" + "="*60)
    print("QUICK TEST FOR NEW ALGORITHMS")
    print("="*60)

    results = {}

    # Test GBMA
    results['GBMA'] = test_algorithm('GBMA', GBMA)

    # Test MMLMA
    results['MMLMA'] = test_algorithm('MMLMA', MMLMA)

    # Test MPFTM
    results['MPFTM'] = test_algorithm('MPFTM', MPFTM)

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for alg_name, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{alg_name:10s}: {status}")
    print("="*60)

    all_passed = all(results.values())
    if all_passed:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed!")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
