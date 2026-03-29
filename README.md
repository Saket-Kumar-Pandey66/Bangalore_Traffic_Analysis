# Bangalore City Traffic Analysis: A Multi-Tool Data Science Project

> **A comprehensive end-to-end data science project analyzing urban traffic congestion patterns in Bangalore using Python, SQL, R, and dashboard tools.**

---

## Table of Contents

1. [Abstract](#abstract)
2. [Introduction](#introduction)
3. [Problem Statement](#problem-statement)
4. [Dataset Description](#dataset-description)
5. [Project Structure](#project-structure)
6. [Methodology](#methodology)
7. [Tools and Technologies](#tools-and-technologies)
8. [Setup and Installation](#setup-and-installation)
9. [Execution Instructions](#execution-instructions)
10. [Results and Analysis](#results-and-analysis)
11. [Model Comparison](#model-comparison)
12. [Key Insights](#key-insights)
13. [Anomaly Detection](#anomaly-detection)
14. [Limitations](#limitations)
15. [Future Work](#future-work)
16. [Conclusion](#conclusion)
17. [References](#references)

---

## Abstract

This project presents a comprehensive analysis of traffic congestion patterns in Bangalore, India, using the Bangalore City Traffic Dataset. Leveraging a multi-tool approach combining **Python**, **SQL (SQLite)**, **R (ggplot2)**, and optional **dashboard tools (Tableau/Power BI)**, the study covers the full data science lifecycle: data preprocessing, exploratory data analysis, feature engineering, time-series decomposition, machine learning (clustering and forecasting), and anomaly detection. The analysis identifies key congestion hotspots, temporal traffic patterns, weather impacts, and forecasts future traffic volumes using ARIMA and SARIMA models. Clustering algorithms (KMeans, DBSCAN, Agglomerative) segment traffic patterns, while statistical methods detect anomalous traffic events. The project demonstrates the power of integrating multiple data science tools for holistic urban traffic analysis.

---

## Introduction

Bangalore (Bengaluru), the Silicon Valley of India, is home to over 12 million people and faces severe traffic congestion challenges. The city's rapid urbanization, coupled with an expanding IT sector and population growth, has led to chronic traffic problems affecting commuter productivity, environmental quality, and public safety.

Understanding traffic patterns through data-driven approaches is essential for:
- **Urban planning**: Informing infrastructure development decisions
- **Traffic management**: Optimizing signal timing and route planning
- **Environmental policy**: Reducing vehicular emissions
- **Public transport**: Improving transit coverage and scheduling
- **Safety**: Identifying accident-prone zones and conditions

This project applies the full spectrum of data science tools and techniques to extract actionable insights from real-world traffic data collected across multiple areas and road segments in Bangalore throughout 2022.

---

## Problem Statement

**How can we analyze, understand, and predict traffic congestion patterns in Bangalore using multiple data science tools to support evidence-based urban traffic management?**

Specific research questions:
1. What are the most congested areas and road segments in Bangalore?
2. How do traffic patterns vary by day of week, month, and season?
3. What is the impact of weather conditions and roadwork on congestion?
4. Can we accurately forecast future traffic volumes using time-series models?
5. How can traffic patterns be segmented using clustering algorithms?
6. Can we detect anomalous traffic events using statistical methods?

---

## Dataset Description

| Attribute | Details |
|-----------|---------|
| **Source** | [Kaggle - Bangalore City Traffic Dataset](https://www.kaggle.com/datasets/preethamgouda/banglore-city-traffic-dataset) |
| **Records** | 8,936 rows |
| **Features** | 16 columns |
| **Time Period** | January 2022 – December 2022 |
| **Format** | CSV |

### Feature Dictionary

| # | Feature | Type | Description |
|---|---------|------|-------------|
| 1 | Date | Date | Date of observation |
| 2 | Area Name | Categorical | Bangalore area (e.g., Indiranagar, Whitefield, Koramangala) |
| 3 | Road/Intersection Name | Categorical | Specific road or intersection |
| 4 | Traffic Volume | Numeric | Number of vehicles recorded |
| 5 | Average Speed | Numeric | Average vehicle speed (km/h) |
| 6 | Travel Time Index | Numeric | Ratio of actual vs free-flow travel time |
| 7 | Congestion Level | Numeric | Congestion percentage (0-100%) |
| 8 | Road Capacity Utilization | Numeric | Percentage of road capacity used |
| 9 | Incident Reports | Numeric | Number of traffic incidents |
| 10 | Environmental Impact | Numeric | Pollution/environmental score |
| 11 | Public Transport Usage | Numeric | Public transit usage percentage |
| 12 | Traffic Signal Compliance | Numeric | Signal compliance percentage |
| 13 | Parking Usage | Numeric | Parking utilization percentage |
| 14 | Pedestrian and Cyclist Count | Numeric | Pedestrian/cyclist count |
| 15 | Weather Conditions | Categorical | Weather (Clear, Rain, Fog, etc.) |
| 16 | Roadwork and Construction Activity | Categorical | Yes/No construction flag |

---

## Project Structure

```
FDS/
├── Banglore_traffic_Dataset.csv    # Raw dataset
├── python_analysis.py              # Python: preprocessing, EDA, ML, anomaly detection
├── sql_analysis.sql                # SQL: analytical queries (SQLite)
├── r_visualizations.R              # R: advanced ggplot2 visualizations
├── main_pipeline.sh                # Shell: orchestration script
├── requirements.txt                # Python dependencies
├── dashboard_instructions.md       # Tableau/Power BI guide
├── README.md                       # This file (academic report)
│
├── outputs/                        # Generated outputs
│   ├── plots/                      # Python-generated visualizations (18 PNG files)
│   │   ├── 01_time_series_traffic_volume.png
│   │   ├── 02_time_series_congestion.png
│   │   ├── 03_boxplots_day_of_week.png
│   │   ├── 04_bar_charts_by_area.png
│   │   ├── 05_correlation_heatmap.png
│   │   ├── 06_distributions.png
│   │   ├── 07_monthly_trends.png
│   │   ├── 08_weather_impact.png
│   │   ├── 09_weekday_vs_weekend.png
│   │   ├── 10_rolling_statistics.png
│   │   ├── 11_seasonal_decomposition.png
│   │   ├── 12_kmeans_evaluation.png
│   │   ├── 13_clustering_comparison.png
│   │   ├── 14_clustering_model_comparison.png
│   │   ├── 15_forecasting_comparison.png
│   │   ├── 16_future_forecast.png
│   │   ├── 17_forecast_model_comparison.png
│   │   └── 18_anomaly_detection.png
│   │
│   ├── r_plots/                    # R-generated visualizations (10 PNG files)
│   │   ├── r_01_boxplot_day_of_week.png
│   │   ├── r_02_boxplot_congestion_by_area.png
│   │   ├── r_03_monthly_trends.png
│   │   ├── r_04_daily_time_series.png
│   │   ├── r_05_correlation_heatmap.png
│   │   ├── r_06_distributions.png
│   │   ├── r_07_weekday_vs_weekend.png
│   │   ├── r_08_weather_impact.png
│   │   ├── r_09_speed_vs_congestion.png
│   │   └── r_10_violin_congestion.png
│   │
│   ├── sql_results/                # SQL query outputs as CSV
│   │   ├── basic_statistics.csv
│   │   ├── top_congested_areas.csv
│   │   ├── top_congested_roads.csv
│   │   ├── monthly_trends.csv
│   │   ├── day_of_week_analysis.csv
│   │   ├── weekday_vs_weekend.csv
│   │   ├── weather_impact.csv
│   │   └── roadwork_impact.csv
│   │
│   ├── data_summary.txt            # Dataset summary
│   ├── data_for_r.csv              # Processed data for R
│   ├── clustering_results.csv      # Clustering comparison
│   ├── forecast_comparison.csv     # ARIMA vs SARIMA metrics
│   ├── future_forecast.csv         # 14-day forecasted values
│   └── anomalies_detected.csv      # Detected anomaly dates
│
└── traffic_analysis.db             # SQLite database
```

---

## Methodology

### Phase 1: Data Loading & Preprocessing (Python)
- Load CSV dataset using pandas
- Rename columns for programmatic access
- Parse date column to datetime
- Handle missing values (median for numeric, mode for categorical)
- Generate descriptive statistics summary

### Phase 2: SQL Analysis (SQLite)
- Load the preprocessed data into an SQLite database
- Execute 8 categories of analytical queries:
  - Basic statistics (counts, min, max, mean)
  - Top congested areas and roads
  - Monthly traffic trends
  - Day-of-week patterns
  - Weekday vs weekend comparison
  - Weather impact analysis
  - Roadwork/construction impact
  - Environmental and safety analysis
- Export all query results to CSV files

### Phase 3: Feature Engineering (Python)
New features created:
- **Month**, **Month_Name**: Extracted from date
- **Day_of_Week**, **Day_Num**: Day identification
- **Is_Weekend**: Binary flag (Saturday/Sunday = 1)
- **Quarter**, **Week_of_Year**: Temporal groupings
- **Is_High_Congestion**: Binary flag (≥75% congestion)
- **Speed_Category**: Very Slow / Slow / Moderate / Fast
- **Volume_Category**: Low / Medium / High / Very High

### Phase 4: Exploratory Data Analysis (Python)
Generated 9 categories of visualizations:
1. Time series plot of traffic volume with 7-day rolling mean
2. Congestion level time series
3. Boxplots by day of week (volume and congestion)
4. Horizontal bar charts by area
5. Correlation heatmap (triangular with annotations)
6. Distribution histograms with KDE for 6 numeric variables
7. Monthly trends (dual-axis: volume bars + congestion line)
8. Weather impact analysis (congestion and incidents)
9. Weekday vs weekend comparison

### Phase 5: Time-Series Analysis (Python)
- **Rolling Statistics**: 7-day and 30-day moving averages and rolling standard deviation
- **Seasonal Decomposition**: Additive decomposition with weekly (period=7) frequency, extracting trend, seasonal, and residual components
- **Observed Patterns**: Weekly cyclical patterns, long-term trends, and residual noise

### Phase 6A: Clustering Analysis (Python - scikit-learn)
Three algorithms compared:
1. **KMeans**: Elbow method + silhouette analysis for optimal K
2. **DBSCAN**: Density-based with eps=1.5, min_samples=10
3. **Agglomerative Clustering**: Hierarchical with same K as KMeans

Features used: Traffic Volume, Average Speed, Congestion Level, Road Capacity Utilization, Environmental Impact, Public Transport Usage.

### Phase 6B: Time-Series Forecasting (Python - statsmodels)
- **ARIMA(2,1,2)**: AutoRegressive Integrated Moving Average
- **SARIMA(1,1,1)(1,1,1,7)**: Seasonal ARIMA with weekly seasonality
- Train/test split: last 30 days as test set
- Evaluation metrics: RMSE, MAE
- 14-day future traffic volume forecast generated

### Phase 7: Anomaly Detection (Python - scipy)
Three detection methods combined:
1. **Z-Score**: |z| > 2 threshold
2. **IQR Method**: Values outside Q1 − 1.5×IQR to Q3 + 1.5×IQR
3. **Rolling Mean Residual**: Residuals exceeding ±2σ from 7-day rolling mean

Final anomalies identified where **≥2 methods agree** (consensus approach).

### Phase 8: R Visualizations (ggplot2)
10 publication-quality visualizations:
1. Boxplot: Traffic volume by day of week
2. Boxplot: Congestion by area (ordered)
3. Monthly trend line plot (dual metric)
4. Daily time series with LOESS smoothing
5. Correlation heatmap (gradient fill)
6. Distribution grid (histogram + density for 4 variables)
7. Weekday vs weekend faceted comparison
8. Weather impact horizontal bar chart
9. Scatter: Speed vs Congestion (colored by volume)
10. Violin plot: Congestion by day type with quartile lines

---

## Tools and Technologies

| Tool | Version | Purpose |
|------|---------|---------|
| **Python** | 3.8+ | Core analysis, ML, preprocessing |
| **pandas** | ≥1.5 | Data manipulation |
| **numpy** | ≥1.23 | Numerical computing |
| **matplotlib** | ≥3.6 | Python visualizations |
| **seaborn** | ≥0.12 | Statistical visualizations |
| **scikit-learn** | ≥1.2 | Clustering, evaluation |
| **statsmodels** | ≥0.13 | Time-series, ARIMA, SARIMA |
| **scipy** | ≥1.9 | Statistical tests, z-scores |
| **SQLite** | Built-in | SQL database engine |
| **R** | 4.0+ | Statistical visualizations |
| **ggplot2** | ≥3.4 | R grammar of graphics |
| **dplyr/tidyr** | Latest | R data manipulation |
| **Bash** | Any | Pipeline orchestration |
| **Tableau/Power BI** | Optional | Interactive dashboards |

---

## Setup and Installation

### Prerequisites
- Python 3.8 or higher
- R 4.0 or higher (for R visualizations)
- Git (optional)

### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Install R Packages (automatic)
The R script auto-installs required packages. To install manually:
```r
install.packages(c("ggplot2", "dplyr", "tidyr", "scales",
                    "RColorBrewer", "viridis", "corrplot",
                    "gridExtra", "lubridate"))
```

---

## Execution Instructions

### Option A: Run Full Pipeline (Recommended)
```bash
bash main_pipeline.sh
```
This runs everything in sequence: Python analysis → R visualizations.

### Option B: Run Components Individually

```bash
# 1. Python analysis (includes SQL + EDA + ML + Anomaly Detection)
python python_analysis.py

# 2. R visualizations (run after Python generates data_for_r.csv)
Rscript r_visualizations.R

# 3. View SQL queries directly
cat sql_analysis.sql

# 4. Explore SQLite database (generated by Python)
sqlite3 traffic_analysis.db ".tables"
sqlite3 traffic_analysis.db "SELECT * FROM traffic LIMIT 5;"
```

---

## Results and Analysis

### SQL Analysis Results
- **8 query categories** executed against SQLite database
- All results exported as CSV files to `outputs/sql_results/`
- Key findings on top congested areas, monthly trends, day-of-week patterns, weather impact, and more

### EDA Findings
- **18 Python plots** generated covering time-series, distributions, correlations, and comparisons
- Traffic volume shows clear weekly cyclical patterns
- Strong positive correlation between Traffic Volume and Congestion Level
- Weather and roadwork significantly affect congestion

### Time-Series Analysis
- **Weekly seasonal pattern** clearly visible in decomposition
- 7-day rolling mean smooths daily fluctuations
- Residual component reveals unexpected traffic events

### Clustering Results
- **KMeans**: Optimal clusters identified via silhouette analysis
- **DBSCAN**: Density-based clusters with noise detection
- **Agglomerative**: Hierarchical clustering for comparison
- All three methods compared using silhouette scores

### Forecasting Results
- **ARIMA(2,1,2)** and **SARIMA(1,1,1)(1,1,1,7)** models compared
- SARIMA generally performs better due to weekly seasonality modeling
- 14-day future forecast generated with ±10% confidence band
- Metrics (RMSE, MAE) saved to `outputs/forecast_comparison.csv`

### Anomaly Detection
- Consensus-based approach using Z-Score, IQR, and Rolling Residual methods
- Anomalies flagged where ≥2 methods agree
- Detected dates saved to `outputs/anomalies_detected.csv`

---

## Model Comparison

### Clustering Models

| Model | Silhouette Score | Notes |
|-------|-----------------|-------|
| KMeans | Best K auto-selected | Optimal via elbow + silhouette |
| DBSCAN | Density-based | Identifies noise points |
| Agglomerative | Same K as KMeans | Hierarchical approach |

### Forecasting Models

| Model | RMSE | MAE | Notes |
|-------|------|-----|-------|
| ARIMA(2,1,2) | See output | See output | No seasonal component |
| SARIMA(1,1,1)(1,1,1,7) | See output | See output | Weekly seasonality |

*Exact values are computed at runtime and saved to `outputs/forecast_comparison.csv`.*

---

## Key Insights

1. **Area-Level Congestion**: Certain areas consistently show higher congestion regardless of day or weather, indicating structural infrastructure bottlenecks.

2. **Day-of-Week Patterns**: Weekdays generally have higher traffic volumes than weekends, with mid-week (Tuesday–Thursday) showing peak congestion.

3. **Monthly Trends**: Traffic patterns show seasonal variation throughout 2022, with potential peaks during festive or rainy seasons.

4. **Weather Impact**: Adverse weather conditions (rain, fog) correlate with higher congestion levels and more incident reports.

5. **Roadwork Effect**: Areas with active construction show measurably higher congestion and lower average speeds.

6. **Public Transport Correlation**: Higher public transport usage areas tend to show different congestion patterns, suggesting the importance of transit investment.

7. **Speed-Congestion Relationship**: Strong inverse relationship between average speed and congestion level, as expected.

8. **Environmental Concern**: Areas with high traffic volume and congestion show proportionally higher environmental impact scores.

9. **Weekly Seasonality**: Clear 7-day cyclical pattern in traffic data, well-captured by SARIMA model.

10. **Anomalous Events**: Several dates flagged as anomalous, potentially corresponding to strikes, holidays, or extreme weather events.

---

## Anomaly Detection

The project implements a **consensus-based anomaly detection** approach:

| Method | Technique | Threshold |
|--------|-----------|-----------|
| Z-Score | Standard deviation from mean | \|z\| > 2 |
| IQR | Interquartile range | Outside Q1 − 1.5×IQR to Q3 + 1.5×IQR |
| Rolling Residual | Deviation from 7-day moving average | \|residual\| > 2σ |

**Final anomalies**: Dates where **≥2 methods agree** on anomaly classification. This consensus approach reduces false positives compared to single-method detection.

---

## Limitations

1. **Daily granularity**: The dataset lacks hourly timestamps, limiting time-of-day analysis (e.g., rush hour detection based on actual hour data).

2. **Single year**: Only 2022 data is available, preventing multi-year trend analysis and year-over-year comparisons.

3. **No geospatial data**: Latitude/longitude coordinates are absent, preventing spatial clustering and map-based visualizations.

4. **Synthetic peak hours**: Without hourly data, peak hour flags are approximated from congestion levels rather than actual time-of-day data.

5. **Limited external context**: Events like festivals, political rallies, or strikes that could explain anomalies are not included in the dataset.

6. **Model simplicity**: ARIMA/SARIMA are univariate models; multivariate approaches (VAR, LSTM) could improve forecasts by incorporating weather and events.

---

## Future Work

1. **Hourly data integration**: Acquire hourly traffic data for granular time-of-day analysis and true peak-hour detection.

2. **Deep learning forecasting**: Implement LSTM, GRU, or Transformer-based models for potentially more accurate traffic prediction.

3. **Geospatial analysis**: Add GPS coordinates for spatial clustering, route optimization, and interactive map visualizations using Folium or Plotly.

4. **Real-time dashboard**: Build a live dashboard using Streamlit or Dash that updates with real-time traffic feeds.

5. **Multi-city comparison**: Extend the analysis to compare Bangalore with other Indian metro cities (Delhi, Mumbai, Chennai).

6. **Integration with Google Maps API**: Validate dataset patterns against live traffic data from mapping services.

7. **Causal analysis**: Apply Granger causality tests to understand directional relationships between variables.

8. **Policy simulation**: Model the impact of proposed interventions (new metro lines, congestion pricing) on traffic patterns.

---

## Conclusion

This project demonstrates a comprehensive, multi-tool data science approach to analyzing urban traffic congestion in Bangalore. By integrating **SQL** for structured querying, **Python** for advanced analytics and machine learning, **R** for publication-quality visualizations, and providing **dashboard** instructions for interactive exploration, the project covers the complete data science lifecycle.

Key contributions include:
- Identification of Bangalore's most congested areas and temporal traffic patterns
- Successful application of SARIMA models for traffic volume forecasting with weekly seasonality
- Multi-method anomaly detection using a consensus-based approach
- Comparative clustering analysis revealing distinct traffic pattern segments
- 28 total visualizations (18 Python + 10 R) providing comprehensive visual storytelling

The findings can inform urban planners, traffic authorities, and policymakers in developing targeted interventions to alleviate Bangalore's chronic traffic congestion.

---

## References

1. Preetham Gouda. (2023). *Bangalore City Traffic Dataset*. Kaggle. https://www.kaggle.com/datasets/preethamgouda/banglore-city-traffic-dataset
2. McKinney, W. (2017). *Python for Data Analysis*. O'Reilly Media.
3. Wickham, H. (2016). *ggplot2: Elegant Graphics for Data Analysis*. Springer.
4. Hyndman, R.J., & Athanasopoulos, G. (2021). *Forecasting: Principles and Practice*. OTexts.
5. Géron, A. (2019). *Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow*. O'Reilly.
6. SQLite Documentation. https://www.sqlite.org/docs.html
7. scikit-learn Documentation. https://scikit-learn.org/stable/
8. statsmodels Documentation. https://www.statsmodels.org/stable/

---

*Project developed as a comprehensive data science academic submission demonstrating multi-tool proficiency in Python, SQL, R, and dashboard technologies.*
