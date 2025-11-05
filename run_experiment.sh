#!/bin/bash
# One-Click Semiconductor Supply Chain Experiment Runner
# This script sets up the environment and runs the complete experiment

echo "=========================================================================="
echo "          Semiconductor Supply Chain HGTM Experiment Runner"
echo "=========================================================================="
echo ""

# Check Python version
echo "Checking Python environment..."
python3 --version

# Install dependencies
echo ""
echo "Installing required dependencies..."
pip install -r requirements.txt -q

if [ $? -ne 0 ]; then
    echo "✗ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed successfully"
echo ""

# Run the experiment
echo "Starting semiconductor supply chain experiment..."
echo ""
python3 run_semiconductor_experiment.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================================================="
    echo "✓ Experiment completed successfully!"
    echo "=========================================================================="
    echo ""
    echo "Check the 'results/' directory for:"
    echo "  - Excel files with detailed results"
    echo "  - PNG figures with visualizations"
    echo "  - Markdown report with analysis"
    echo ""
else
    echo ""
    echo "✗ Experiment failed. Please check the error messages above."
    exit 1
fi
