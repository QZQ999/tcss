"""
Quick test script to verify the semiconductor experiment setup
Runs a small-scale test (3 runs) to ensure everything works
"""

import sys
from run_semiconductor_experiment import SemiconductorExperiment

def main():
    print("="*70)
    print("Quick Test - Semiconductor Supply Chain Experiment")
    print("="*70)
    print("\nThis will run a quick test with 3 iterations...")
    print("Full experiment can be run with: python3 run_semiconductor_experiment.py")
    print("")

    try:
        # Create experiment instance
        experiment = SemiconductorExperiment(
            data_dir="data",
            output_dir="results"
        )

        # Run quick test (3 runs only)
        experiment.run_complete_experiment(num_runs=3)

        print("\n" + "="*70)
        print("✓ Quick test completed successfully!")
        print("="*70)
        print("\nYou can now run the full experiment:")
        print("  python3 run_semiconductor_experiment.py")
        print("\nOr use the one-click script:")
        print("  ./run_experiment.sh")

    except Exception as e:
        print(f"\n✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
