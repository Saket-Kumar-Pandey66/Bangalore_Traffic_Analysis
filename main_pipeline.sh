#!/bin/bash
# ============================================================================
# Bangalore City Traffic Dataset - Main Pipeline Script
# ============================================================================
# This script runs the complete analysis pipeline:
#   1. Install Python dependencies
#   2. Run Python analysis (SQL + EDA + ML + Anomaly Detection)
#   3. Run R visualizations
# ============================================================================
# Usage: bash main_pipeline.sh
# ============================================================================

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  BANGALORE TRAFFIC ANALYSIS - MAIN PIPELINE              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# --- Step 1: Check Python ---
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  STEP 1: Checking Python environment..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "  ERROR: Python not found. Please install Python 3.8+"
    exit 1
fi
echo "  Python: $($PYTHON --version)"

# --- Step 2: Install Python dependencies ---
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  STEP 2: Installing Python dependencies..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
$PYTHON -m pip install -r requirements.txt --quiet 2>/dev/null || {
    echo "  Warning: pip install had issues. Trying with --user flag..."
    $PYTHON -m pip install -r requirements.txt --user --quiet 2>/dev/null || true
}
echo "  Dependencies installed."

# --- Step 3: Run Python Analysis ---
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  STEP 3: Running Python Analysis..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
$PYTHON python_analysis.py
echo ""
echo "  Python analysis completed successfully!"

# --- Step 4: Run R Visualizations (optional) ---
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  STEP 4: Running R Visualizations..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if command -v Rscript &> /dev/null; then
    echo "  R found: $(Rscript --version 2>&1 | head -1)"
    Rscript r_visualizations.R
    echo "  R visualizations completed!"
else
    echo "  WARNING: R/Rscript not found. Skipping R visualizations."
    echo "  Install R from: https://cran.r-project.org/"
    echo "  Then run: Rscript r_visualizations.R"
fi

# --- Step 5: Summary ---
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  PIPELINE COMPLETE!                                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "  Output files:"
echo "  ├── outputs/"
echo "  │   ├── plots/              (Python EDA & ML plots)"
echo "  │   ├── r_plots/            (R ggplot2 visualizations)"
echo "  │   ├── sql_results/        (SQL query outputs as CSV)"
echo "  │   ├── data_summary.txt    (Dataset summary)"
echo "  │   ├── clustering_results.csv"
echo "  │   ├── forecast_comparison.csv"
echo "  │   ├── future_forecast.csv"
echo "  │   ├── anomalies_detected.csv"
echo "  │   └── data_for_r.csv      (R input data)"
echo "  └── traffic_analysis.db     (SQLite database)"
echo ""
echo "  Total plots: $(find outputs/plots outputs/r_plots -name '*.png' 2>/dev/null | wc -l) PNG files"
echo ""

# --- Step 6: Launch Dashboard ---
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  STEP 6: Launching Streamlit Dashboard..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
$PYTHON -m pip install streamlit pandas pillow --quiet 2>/dev/null || true
echo "  Starting dashboard in your browser..."
$PYTHON -m streamlit run dashboard.py
