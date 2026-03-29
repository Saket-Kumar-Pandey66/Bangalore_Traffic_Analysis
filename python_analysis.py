"""
================================================================================
Bangalore City Traffic Dataset - Comprehensive Python Analysis
================================================================================
This script performs:
  1. Data Loading & Preprocessing
  2. SQL Analysis (SQLite)
  3. Feature Engineering
  4. Exploratory Data Analysis (EDA)
  5. Time-Series Analysis
  6. Machine Learning (Clustering + Forecasting)
  7. Anomaly Detection
  8. Exports results and plots
================================================================================
"""

import os
import sqlite3
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for saving plots
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.metrics import silhouette_score

from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_squared_error, mean_absolute_error

warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================
DATASET_PATH = 'Banglore_traffic_Dataset.csv'
DB_PATH = 'traffic_analysis.db'
OUTPUT_DIR = 'outputs'
PLOTS_DIR = os.path.join(OUTPUT_DIR, 'plots')
SQL_OUTPUT_DIR = os.path.join(OUTPUT_DIR, 'sql_results')

for d in [OUTPUT_DIR, PLOTS_DIR, SQL_OUTPUT_DIR]:
    os.makedirs(d, exist_ok=True)

# Plot style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette('viridis')
FIGSIZE = (12, 6)
DPI = 150


def save_plot(fig, name):
    """Save a matplotlib figure to the plots directory."""
    path = os.path.join(PLOTS_DIR, f'{name}.png')
    fig.savefig(path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  [SAVED] {path}")


# ============================================================================
# PHASE 1: DATA LOADING & PREPROCESSING
# ============================================================================
def load_and_preprocess():
    print("=" * 70)
    print("PHASE 1: DATA LOADING & PREPROCESSING")
    print("=" * 70)

    df = pd.read_csv(DATASET_PATH)
    print(f"\nDataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")

    # Rename columns for easier SQL/Python handling
    col_map = {
        'Area Name': 'Area_Name',
        'Road/Intersection Name': 'Road_Name',
        'Traffic Volume': 'Traffic_Volume',
        'Average Speed': 'Average_Speed',
        'Travel Time Index': 'Travel_Time_Index',
        'Congestion Level': 'Congestion_Level',
        'Road Capacity Utilization': 'Road_Capacity_Utilization',
        'Incident Reports': 'Incident_Reports',
        'Environmental Impact': 'Environmental_Impact',
        'Public Transport Usage': 'Public_Transport_Usage',
        'Traffic Signal Compliance': 'Traffic_Signal_Compliance',
        'Parking Usage': 'Parking_Usage',
        'Pedestrian and Cyclist Count': 'Pedestrian_Cyclist_Count',
        'Weather Conditions': 'Weather_Conditions',
        'Roadwork and Construction Activity': 'Roadwork_Activity',
    }
    df.rename(columns=col_map, inplace=True)

    # Parse date
    df['Date'] = pd.to_datetime(df['Date'])

    # Handle missing values
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print(f"\nMissing values:\n{missing[missing > 0]}")
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
        cat_cols = df.select_dtypes(include='object').columns
        for col in cat_cols:
            df[col].fillna(df[col].mode()[0], inplace=True)
    else:
        print("\nNo missing values found.")

    # Data types summary
    print(f"\nData types:\n{df.dtypes}")
    print(f"\nBasic statistics:\n{df.describe().round(2)}")

    # Save preprocessing summary
    with open(os.path.join(OUTPUT_DIR, 'data_summary.txt'), 'w') as f:
        f.write("BANGALORE TRAFFIC DATASET - DATA SUMMARY\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Shape: {df.shape}\n")
        f.write(f"Date range: {df['Date'].min()} to {df['Date'].max()}\n")
        f.write(f"Unique areas: {df['Area_Name'].nunique()}\n")
        f.write(f"Unique roads: {df['Road_Name'].nunique()}\n\n")
        f.write("Descriptive Statistics:\n")
        f.write(df.describe().round(2).to_string())
    print("  [SAVED] outputs/data_summary.txt")

    return df


# ============================================================================
# PHASE 2: SQL ANALYSIS (SQLite)
# ============================================================================
def run_sql_analysis(df):
    print("\n" + "=" * 70)
    print("PHASE 2: SQL ANALYSIS (SQLite)")
    print("=" * 70)

    # Load data into SQLite
    conn = sqlite3.connect(DB_PATH)
    df_sql = df.copy()
    df_sql['Date'] = df_sql['Date'].dt.strftime('%Y-%m-%d')
    df_sql.to_sql('traffic', conn, if_exists='replace', index=False)
    print(f"\n  Data loaded into SQLite database: {DB_PATH}")

    # Read and execute SQL file
    queries = {
        'basic_statistics': """
            SELECT
                'Traffic Volume' AS metric,
                ROUND(AVG(Traffic_Volume), 2) AS mean_value,
                MIN(Traffic_Volume) AS min_value,
                MAX(Traffic_Volume) AS max_value
            FROM traffic
            UNION ALL
            SELECT 'Average Speed', ROUND(AVG(Average_Speed), 2),
                   ROUND(MIN(Average_Speed), 2), ROUND(MAX(Average_Speed), 2)
            FROM traffic
            UNION ALL
            SELECT 'Congestion Level', ROUND(AVG(Congestion_Level), 2),
                   ROUND(MIN(Congestion_Level), 2), ROUND(MAX(Congestion_Level), 2)
            FROM traffic
        """,
        'top_congested_areas': """
            SELECT Area_Name,
                   ROUND(AVG(Congestion_Level), 2) AS avg_congestion,
                   ROUND(AVG(Traffic_Volume), 0) AS avg_traffic_volume,
                   ROUND(AVG(Average_Speed), 2) AS avg_speed,
                   COUNT(*) AS record_count
            FROM traffic
            GROUP BY Area_Name
            ORDER BY avg_congestion DESC
            LIMIT 10
        """,
        'top_congested_roads': """
            SELECT Road_Name, Area_Name,
                   ROUND(AVG(Congestion_Level), 2) AS avg_congestion,
                   ROUND(AVG(Traffic_Volume), 0) AS avg_traffic_volume
            FROM traffic
            GROUP BY Road_Name, Area_Name
            ORDER BY avg_congestion DESC
            LIMIT 10
        """,
        'monthly_trends': """
            SELECT strftime('%Y-%m', Date) AS month,
                   ROUND(AVG(Traffic_Volume), 0) AS avg_traffic_volume,
                   ROUND(AVG(Congestion_Level), 2) AS avg_congestion,
                   ROUND(AVG(Average_Speed), 2) AS avg_speed,
                   SUM(Incident_Reports) AS total_incidents
            FROM traffic
            GROUP BY strftime('%Y-%m', Date)
            ORDER BY month
        """,
        'day_of_week_analysis': """
            SELECT
                CASE strftime('%w', Date)
                    WHEN '0' THEN 'Sunday'
                    WHEN '1' THEN 'Monday'
                    WHEN '2' THEN 'Tuesday'
                    WHEN '3' THEN 'Wednesday'
                    WHEN '4' THEN 'Thursday'
                    WHEN '5' THEN 'Friday'
                    WHEN '6' THEN 'Saturday'
                END AS day_of_week,
                ROUND(AVG(Traffic_Volume), 0) AS avg_traffic_volume,
                ROUND(AVG(Congestion_Level), 2) AS avg_congestion,
                ROUND(AVG(Average_Speed), 2) AS avg_speed
            FROM traffic
            GROUP BY strftime('%w', Date)
            ORDER BY CAST(strftime('%w', Date) AS INTEGER)
        """,
        'weekday_vs_weekend': """
            SELECT
                CASE WHEN strftime('%w', Date) IN ('0', '6') THEN 'Weekend'
                     ELSE 'Weekday' END AS day_type,
                ROUND(AVG(Traffic_Volume), 0) AS avg_traffic_volume,
                ROUND(AVG(Congestion_Level), 2) AS avg_congestion,
                ROUND(AVG(Average_Speed), 2) AS avg_speed,
                COUNT(*) AS total_records
            FROM traffic
            GROUP BY day_type
        """,
        'weather_impact': """
            SELECT Weather_Conditions,
                   COUNT(*) AS record_count,
                   ROUND(AVG(Traffic_Volume), 0) AS avg_traffic_volume,
                   ROUND(AVG(Congestion_Level), 2) AS avg_congestion,
                   ROUND(AVG(Average_Speed), 2) AS avg_speed
            FROM traffic
            GROUP BY Weather_Conditions
            ORDER BY avg_congestion DESC
        """,
        'roadwork_impact': """
            SELECT Roadwork_Activity,
                   COUNT(*) AS record_count,
                   ROUND(AVG(Congestion_Level), 2) AS avg_congestion,
                   ROUND(AVG(Average_Speed), 2) AS avg_speed
            FROM traffic
            GROUP BY Roadwork_Activity
        """,
    }

    sql_results = {}
    for name, query in queries.items():
        result = pd.read_sql_query(query, conn)
        sql_results[name] = result
        csv_path = os.path.join(SQL_OUTPUT_DIR, f'{name}.csv')
        result.to_csv(csv_path, index=False)
        print(f"\n  [{name.upper()}]")
        print(result.to_string(index=False))
        print(f"  [SAVED] {csv_path}")

    conn.close()
    return sql_results


# ============================================================================
# PHASE 3: FEATURE ENGINEERING
# ============================================================================
def feature_engineering(df):
    print("\n" + "=" * 70)
    print("PHASE 3: FEATURE ENGINEERING")
    print("=" * 70)

    df['Month'] = df['Date'].dt.month
    df['Month_Name'] = df['Date'].dt.month_name()
    df['Day_of_Week'] = df['Date'].dt.day_name()
    df['Day_Num'] = df['Date'].dt.dayofweek  # 0=Monday, 6=Sunday
    df['Is_Weekend'] = df['Day_Num'].isin([5, 6]).astype(int)
    df['Quarter'] = df['Date'].dt.quarter
    df['Week_of_Year'] = df['Date'].dt.isocalendar().week.astype(int)

    # Since dataset is daily (no hour), we'll create synthetic features
    # based on congestion patterns for peak-hour simulation
    df['Is_High_Congestion'] = (df['Congestion_Level'] >= 75).astype(int)
    df['Speed_Category'] = pd.cut(
        df['Average_Speed'],
        bins=[0, 20, 40, 60, 100],
        labels=['Very Slow', 'Slow', 'Moderate', 'Fast']
    )
    df['Volume_Category'] = pd.cut(
        df['Traffic_Volume'],
        bins=[0, 20000, 40000, 60000, 100000],
        labels=['Low', 'Medium', 'High', 'Very High']
    )

    print(f"\n  New features: Month, Month_Name, Day_of_Week, Day_Num, "
          f"Is_Weekend, Quarter, Week_of_Year")
    print(f"  Derived features: Is_High_Congestion, Speed_Category, Volume_Category")
    print(f"  Updated shape: {df.shape}")

    return df


# ============================================================================
# PHASE 4: EXPLORATORY DATA ANALYSIS (EDA)
# ============================================================================
def exploratory_data_analysis(df):
    print("\n" + "=" * 70)
    print("PHASE 4: EXPLORATORY DATA ANALYSIS")
    print("=" * 70)

    numeric_cols = ['Traffic_Volume', 'Average_Speed', 'Travel_Time_Index',
                    'Congestion_Level', 'Road_Capacity_Utilization',
                    'Environmental_Impact', 'Public_Transport_Usage',
                    'Traffic_Signal_Compliance', 'Parking_Usage',
                    'Pedestrian_Cyclist_Count', 'Incident_Reports']

    # --- 4a. Time Series Plot: Traffic Volume Over Time ---
    print("\n  Creating time series plot...")
    daily_avg = df.groupby('Date')['Traffic_Volume'].mean()
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.plot(daily_avg.index, daily_avg.values, color='#2196F3', linewidth=0.8, alpha=0.7)
    rolling = daily_avg.rolling(window=7).mean()
    ax.plot(rolling.index, rolling.values, color='#FF5722', linewidth=2, label='7-day Rolling Mean')
    ax.set_title('Daily Average Traffic Volume Over Time', fontsize=14, fontweight='bold')
    ax.set_xlabel('Date')
    ax.set_ylabel('Average Traffic Volume')
    ax.legend()
    save_plot(fig, '01_time_series_traffic_volume')

    # --- 4b. Congestion Level Time Series ---
    print("  Creating congestion time series plot...")
    daily_cong = df.groupby('Date')['Congestion_Level'].mean()
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.plot(daily_cong.index, daily_cong.values, color='#E91E63', linewidth=0.8, alpha=0.7)
    rolling_cong = daily_cong.rolling(window=7).mean()
    ax.plot(rolling_cong.index, rolling_cong.values, color='#9C27B0', linewidth=2,
            label='7-day Rolling Mean')
    ax.set_title('Daily Average Congestion Level Over Time', fontsize=14, fontweight='bold')
    ax.set_xlabel('Date')
    ax.set_ylabel('Congestion Level (%)')
    ax.legend()
    save_plot(fig, '02_time_series_congestion')

    # --- 4c. Boxplots: Traffic Volume by Day of Week ---
    print("  Creating boxplots by day of week...")
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    sns.boxplot(data=df, x='Day_of_Week', y='Traffic_Volume',
                order=day_order, ax=axes[0], palette='Set2')
    axes[0].set_title('Traffic Volume by Day of Week', fontweight='bold')
    axes[0].tick_params(axis='x', rotation=45)

    sns.boxplot(data=df, x='Day_of_Week', y='Congestion_Level',
                order=day_order, ax=axes[1], palette='Set3')
    axes[1].set_title('Congestion Level by Day of Week', fontweight='bold')
    axes[1].tick_params(axis='x', rotation=45)
    fig.tight_layout()
    save_plot(fig, '03_boxplots_day_of_week')

    # --- 4d. Bar Charts: Average Metrics by Area ---
    print("  Creating bar charts by area...")
    area_stats = df.groupby('Area_Name').agg({
        'Traffic_Volume': 'mean',
        'Congestion_Level': 'mean',
        'Average_Speed': 'mean'
    }).round(1)
    area_stats = area_stats.sort_values('Congestion_Level', ascending=False)

    fig, axes = plt.subplots(1, 3, figsize=(20, 7))
    colors = ['#FF6F61', '#6B5B95', '#88B04B']
    for i, col in enumerate(['Congestion_Level', 'Traffic_Volume', 'Average_Speed']):
        area_stats[col].plot(kind='barh', ax=axes[i], color=colors[i], edgecolor='white')
        axes[i].set_title(f'Avg {col.replace("_", " ")} by Area', fontweight='bold')
        axes[i].set_xlabel(col.replace('_', ' '))
    fig.tight_layout()
    save_plot(fig, '04_bar_charts_by_area')

    # --- 4e. Correlation Heatmap ---
    print("  Creating correlation heatmap...")
    corr_cols = [c for c in numeric_cols if c in df.columns]
    corr_matrix = df[corr_cols].corr()
    fig, ax = plt.subplots(figsize=(12, 10))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdYlBu_r', mask=mask,
                center=0, square=True, linewidths=0.5, ax=ax,
                cbar_kws={"shrink": 0.8})
    ax.set_title('Correlation Heatmap of Traffic Variables', fontsize=14, fontweight='bold')
    save_plot(fig, '05_correlation_heatmap')

    # --- 4f. Distribution Plots ---
    print("  Creating distribution plots...")
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    dist_cols = ['Traffic_Volume', 'Average_Speed', 'Congestion_Level',
                 'Road_Capacity_Utilization', 'Environmental_Impact', 'Public_Transport_Usage']
    for i, col in enumerate(dist_cols):
        row, c = divmod(i, 3)
        sns.histplot(df[col], kde=True, ax=axes[row][c], color=sns.color_palette('viridis', 6)[i])
        axes[row][c].set_title(f'Distribution of {col.replace("_", " ")}', fontweight='bold')
    fig.tight_layout()
    save_plot(fig, '06_distributions')

    # --- 4g. Monthly Trends ---
    print("  Creating monthly trends plot...")
    monthly = df.groupby('Month').agg({
        'Traffic_Volume': 'mean',
        'Congestion_Level': 'mean',
        'Average_Speed': 'mean'
    }).round(2)

    fig, ax1 = plt.subplots(figsize=FIGSIZE)
    ax1.bar(monthly.index, monthly['Traffic_Volume'], color='#42A5F5', alpha=0.7,
            label='Avg Traffic Volume')
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Traffic Volume', color='#42A5F5')
    ax1.set_xticks(range(1, 13))
    ax2 = ax1.twinx()
    ax2.plot(monthly.index, monthly['Congestion_Level'], color='#EF5350',
             marker='o', linewidth=2, label='Avg Congestion')
    ax2.set_ylabel('Congestion Level (%)', color='#EF5350')
    fig.suptitle('Monthly Traffic Volume and Congestion Trends', fontsize=14, fontweight='bold')
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    save_plot(fig, '07_monthly_trends')

    # --- 4h. Weather Impact ---
    print("  Creating weather impact plot...")
    weather_stats = df.groupby('Weather_Conditions').agg({
        'Traffic_Volume': 'mean',
        'Congestion_Level': 'mean',
        'Incident_Reports': 'sum'
    }).round(1)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    weather_stats['Congestion_Level'].plot(kind='bar', ax=axes[0], color='#FF7043', edgecolor='white')
    axes[0].set_title('Avg Congestion by Weather', fontweight='bold')
    axes[0].set_ylabel('Congestion Level')
    axes[0].tick_params(axis='x', rotation=45)

    weather_stats['Incident_Reports'].plot(kind='bar', ax=axes[1], color='#AB47BC', edgecolor='white')
    axes[1].set_title('Total Incidents by Weather', fontweight='bold')
    axes[1].set_ylabel('Incident Count')
    axes[1].tick_params(axis='x', rotation=45)
    fig.tight_layout()
    save_plot(fig, '08_weather_impact')

    # --- 4i. Weekend vs Weekday ---
    print("  Creating weekend vs weekday comparison...")
    wk_stats = df.groupby('Is_Weekend').agg({
        'Traffic_Volume': 'mean',
        'Congestion_Level': 'mean',
        'Average_Speed': 'mean',
        'Incident_Reports': 'sum'
    }).round(2)
    wk_stats.index = ['Weekday', 'Weekend']

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    metrics = ['Traffic_Volume', 'Congestion_Level', 'Average_Speed']
    colors_wk = [['#42A5F5', '#66BB6A'], ['#EF5350', '#FFA726'], ['#AB47BC', '#26C6DA']]
    for i, m in enumerate(metrics):
        wk_stats[m].plot(kind='bar', ax=axes[i], color=colors_wk[i], edgecolor='white')
        axes[i].set_title(f'{m.replace("_", " ")}', fontweight='bold')
        axes[i].tick_params(axis='x', rotation=0)
    fig.suptitle('Weekday vs Weekend Traffic Comparison', fontsize=14, fontweight='bold', y=1.02)
    fig.tight_layout()
    save_plot(fig, '09_weekday_vs_weekend')

    return corr_matrix


# ============================================================================
# PHASE 5: TIME-SERIES ANALYSIS
# ============================================================================
def time_series_analysis(df):
    print("\n" + "=" * 70)
    print("PHASE 5: TIME-SERIES ANALYSIS")
    print("=" * 70)

    # Aggregate daily traffic volume
    daily = df.groupby('Date')['Traffic_Volume'].mean()
    daily = daily.asfreq('D')
    daily = daily.ffill()

    # --- 5a. Rolling Statistics ---
    print("\n  Computing rolling statistics...")
    rolling_7 = daily.rolling(window=7).mean()
    rolling_30 = daily.rolling(window=30).mean()
    rolling_std = daily.rolling(window=7).std()

    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    axes[0].plot(daily.index, daily.values, alpha=0.4, label='Daily', color='#90CAF9')
    axes[0].plot(rolling_7.index, rolling_7.values, label='7-day MA', color='#1565C0', linewidth=2)
    axes[0].plot(rolling_30.index, rolling_30.values, label='30-day MA', color='#FF5722', linewidth=2)
    axes[0].set_title('Traffic Volume - Rolling Means', fontsize=14, fontweight='bold')
    axes[0].set_ylabel('Average Traffic Volume')
    axes[0].legend()

    axes[1].plot(rolling_std.index, rolling_std.values, color='#4CAF50', linewidth=1.5)
    axes[1].set_title('Traffic Volume - Rolling Standard Deviation (7-day)', fontsize=14, fontweight='bold')
    axes[1].set_ylabel('Std Dev')
    axes[1].set_xlabel('Date')
    fig.tight_layout()
    save_plot(fig, '10_rolling_statistics')

    # --- 5b. Seasonal Decomposition ---
    print("  Performing seasonal decomposition...")
    try:
        decomposition = seasonal_decompose(daily, model='additive', period=7)

        fig, axes = plt.subplots(4, 1, figsize=(14, 12))
        decomposition.observed.plot(ax=axes[0], color='#1976D2')
        axes[0].set_title('Observed', fontweight='bold')
        axes[0].set_ylabel('Traffic Volume')

        decomposition.trend.plot(ax=axes[1], color='#E91E63')
        axes[1].set_title('Trend', fontweight='bold')
        axes[1].set_ylabel('Traffic Volume')

        decomposition.seasonal.plot(ax=axes[2], color='#4CAF50')
        axes[2].set_title('Seasonal (Weekly Pattern)', fontweight='bold')
        axes[2].set_ylabel('Traffic Volume')

        decomposition.resid.plot(ax=axes[3], color='#FF9800')
        axes[3].set_title('Residual', fontweight='bold')
        axes[3].set_ylabel('Traffic Volume')
        axes[3].set_xlabel('Date')

        fig.suptitle('Seasonal Decomposition of Traffic Volume (Weekly Period)',
                     fontsize=14, fontweight='bold', y=1.01)
        fig.tight_layout()
        save_plot(fig, '11_seasonal_decomposition')
        print("  Seasonal decomposition completed successfully.")
        return daily, decomposition
    except Exception as e:
        print(f"  Warning: Seasonal decomposition failed: {e}")
        return daily, None


# ============================================================================
# PHASE 6: MACHINE LEARNING
# ============================================================================

# --- 6A: CLUSTERING ---
def clustering_analysis(df):
    print("\n" + "=" * 70)
    print("PHASE 6A: CLUSTERING ANALYSIS")
    print("=" * 70)

    # Prepare features for clustering
    cluster_features = ['Traffic_Volume', 'Average_Speed', 'Congestion_Level',
                        'Road_Capacity_Utilization', 'Environmental_Impact',
                        'Public_Transport_Usage']
    X = df[cluster_features].dropna()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    results = {}

    # --- KMeans ---
    print("\n  Running KMeans clustering...")
    inertias = []
    sil_scores_km = []
    K_range = range(2, 9)
    for k in K_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X_scaled)
        inertias.append(km.inertia_)
        sil_scores_km.append(silhouette_score(X_scaled, labels))

    best_k = list(K_range)[np.argmax(sil_scores_km)]
    km_final = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    km_labels = km_final.fit_predict(X_scaled)
    km_sil = silhouette_score(X_scaled, km_labels)
    results['KMeans'] = {'k': best_k, 'silhouette': round(km_sil, 4)}
    print(f"    Best K={best_k}, Silhouette Score={km_sil:.4f}")

    # Elbow plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].plot(K_range, inertias, 'bo-', linewidth=2)
    axes[0].set_title('Elbow Method for KMeans', fontweight='bold')
    axes[0].set_xlabel('Number of Clusters (K)')
    axes[0].set_ylabel('Inertia')

    axes[1].plot(K_range, sil_scores_km, 'rs-', linewidth=2)
    axes[1].set_title('Silhouette Scores for KMeans', fontweight='bold')
    axes[1].set_xlabel('Number of Clusters (K)')
    axes[1].set_ylabel('Silhouette Score')
    fig.tight_layout()
    save_plot(fig, '12_kmeans_evaluation')

    # --- DBSCAN ---
    print("  Running DBSCAN clustering...")
    dbscan = DBSCAN(eps=1.5, min_samples=10)
    db_labels = dbscan.fit_predict(X_scaled)
    n_clusters_db = len(set(db_labels)) - (1 if -1 in db_labels else 0)
    n_noise = (db_labels == -1).sum()

    if n_clusters_db > 1:
        mask = db_labels != -1
        db_sil = silhouette_score(X_scaled[mask], db_labels[mask])
    else:
        db_sil = -1
    results['DBSCAN'] = {'clusters': n_clusters_db, 'noise': n_noise,
                         'silhouette': round(db_sil, 4)}
    print(f"    Clusters={n_clusters_db}, Noise points={n_noise}, Silhouette={db_sil:.4f}")

    # --- Agglomerative Clustering ---
    print("  Running Agglomerative clustering...")
    agg = AgglomerativeClustering(n_clusters=best_k)
    agg_labels = agg.fit_predict(X_scaled)
    agg_sil = silhouette_score(X_scaled, agg_labels)
    results['Agglomerative'] = {'k': best_k, 'silhouette': round(agg_sil, 4)}
    print(f"    K={best_k}, Silhouette Score={agg_sil:.4f}")

    # --- Cluster Comparison ---
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    all_labels = [km_labels, db_labels, agg_labels]
    titles = [f'KMeans (K={best_k})', f'DBSCAN ({n_clusters_db} clusters)',
              f'Agglomerative (K={best_k})']
    for i, (labels, title) in enumerate(zip(all_labels, titles)):
        scatter = axes[i].scatter(X_scaled[:, 0], X_scaled[:, 2],
                                  c=labels, cmap='viridis', alpha=0.5, s=10)
        axes[i].set_title(title, fontweight='bold')
        axes[i].set_xlabel('Traffic Volume (scaled)')
        axes[i].set_ylabel('Congestion Level (scaled)')
        plt.colorbar(scatter, ax=axes[i])
    fig.suptitle('Clustering Comparison', fontsize=14, fontweight='bold', y=1.02)
    fig.tight_layout()
    save_plot(fig, '13_clustering_comparison')

    # --- Model Comparison Bar Chart ---
    fig, ax = plt.subplots(figsize=(8, 5))
    model_names = list(results.keys())
    sil_values = [results[m]['silhouette'] for m in model_names]
    bars = ax.bar(model_names, sil_values, color=['#42A5F5', '#66BB6A', '#FF7043'],
                  edgecolor='white', linewidth=2)
    ax.set_title('Clustering Model Comparison - Silhouette Scores',
                 fontsize=14, fontweight='bold')
    ax.set_ylabel('Silhouette Score')
    for bar, val in zip(bars, sil_values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                f'{val:.4f}', ha='center', fontweight='bold')
    save_plot(fig, '14_clustering_model_comparison')

    # Save results
    results_df = pd.DataFrame(results).T
    results_df.to_csv(os.path.join(OUTPUT_DIR, 'clustering_results.csv'))
    print(f"\n  Clustering Results:")
    print(results_df)

    return results, km_labels


# --- 6B: FORECASTING (ARIMA / SARIMA) ---
def forecasting_analysis(daily_ts):
    print("\n" + "=" * 70)
    print("PHASE 6B: FORECASTING (ARIMA / SARIMA)")
    print("=" * 70)

    # Use last 30 days as test set
    train = daily_ts[:-30]
    test = daily_ts[-30:]

    forecast_results = {}

    # --- ARIMA ---
    print("\n  Fitting ARIMA model...")
    try:
        arima_model = ARIMA(train, order=(2, 1, 2))
        arima_fit = arima_model.fit()
        arima_pred = arima_fit.forecast(steps=30)

        arima_rmse = np.sqrt(mean_squared_error(test, arima_pred))
        arima_mae = mean_absolute_error(test, arima_pred)
        forecast_results['ARIMA(2,1,2)'] = {
            'RMSE': round(arima_rmse, 2),
            'MAE': round(arima_mae, 2)
        }
        print(f"    ARIMA(2,1,2) - RMSE: {arima_rmse:.2f}, MAE: {arima_mae:.2f}")
    except Exception as e:
        print(f"    ARIMA failed: {e}")
        arima_pred = None

    # --- SARIMA ---
    print("  Fitting SARIMA model...")
    try:
        sarima_model = SARIMAX(train, order=(1, 1, 1),
                               seasonal_order=(1, 1, 1, 7))
        sarima_fit = sarima_model.fit(disp=False, maxiter=200)
        sarima_pred = sarima_fit.forecast(steps=30)

        sarima_rmse = np.sqrt(mean_squared_error(test, sarima_pred))
        sarima_mae = mean_absolute_error(test, sarima_pred)
        forecast_results['SARIMA(1,1,1)(1,1,1,7)'] = {
            'RMSE': round(sarima_rmse, 2),
            'MAE': round(sarima_mae, 2)
        }
        print(f"    SARIMA - RMSE: {sarima_rmse:.2f}, MAE: {sarima_mae:.2f}")
    except Exception as e:
        print(f"    SARIMA failed: {e}")
        sarima_pred = None

    # --- Forecast Visualization ---
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(train.index[-60:], train.values[-60:], label='Training', color='#1976D2', linewidth=1.5)
    ax.plot(test.index, test.values, label='Actual', color='#212121', linewidth=2)
    if arima_pred is not None:
        ax.plot(test.index, arima_pred.values, label='ARIMA Forecast',
                color='#FF5722', linewidth=2, linestyle='--')
    if sarima_pred is not None:
        ax.plot(test.index, sarima_pred.values, label='SARIMA Forecast',
                color='#4CAF50', linewidth=2, linestyle='-.')
    ax.set_title('Traffic Volume Forecasting: ARIMA vs SARIMA', fontsize=14, fontweight='bold')
    ax.set_xlabel('Date')
    ax.set_ylabel('Average Traffic Volume')
    ax.legend(fontsize=11)
    ax.axvline(x=test.index[0], color='gray', linestyle=':', alpha=0.7)
    save_plot(fig, '15_forecasting_comparison')

    # --- Future Forecast (next 14 days) ---
    print("  Generating 14-day future forecast...")
    try:
        full_model = SARIMAX(daily_ts, order=(1, 1, 1),
                             seasonal_order=(1, 1, 1, 7))
        full_fit = full_model.fit(disp=False, maxiter=200)
        future_pred = full_fit.forecast(steps=14)

        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(daily_ts.index[-30:], daily_ts.values[-30:],
                label='Historical', color='#1976D2', linewidth=2)
        ax.plot(future_pred.index, future_pred.values,
                label='14-Day Forecast', color='#FF5722', linewidth=2, marker='o')
        ax.fill_between(future_pred.index,
                        future_pred.values * 0.9,
                        future_pred.values * 1.1,
                        alpha=0.2, color='#FF5722', label='±10% Band')
        ax.set_title('14-Day Traffic Volume Forecast', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Average Traffic Volume')
        ax.legend()
        save_plot(fig, '16_future_forecast')

        future_df = pd.DataFrame({
            'Date': future_pred.index,
            'Predicted_Traffic_Volume': future_pred.values.round(0)
        })
        future_df.to_csv(os.path.join(OUTPUT_DIR, 'future_forecast.csv'), index=False)
        print(f"  [SAVED] outputs/future_forecast.csv")
    except Exception as e:
        print(f"  Future forecast failed: {e}")

    # Save comparison
    if forecast_results:
        fr_df = pd.DataFrame(forecast_results).T
        fr_df.to_csv(os.path.join(OUTPUT_DIR, 'forecast_comparison.csv'))
        print(f"\n  Forecast Comparison:")
        print(fr_df)

        # Bar chart comparison
        fig, ax = plt.subplots(figsize=(8, 5))
        x = np.arange(len(forecast_results))
        width = 0.35
        rmse_vals = [v['RMSE'] for v in forecast_results.values()]
        mae_vals = [v['MAE'] for v in forecast_results.values()]
        ax.bar(x - width / 2, rmse_vals, width, label='RMSE', color='#EF5350')
        ax.bar(x + width / 2, mae_vals, width, label='MAE', color='#42A5F5')
        ax.set_xticks(x)
        ax.set_xticklabels(forecast_results.keys(), rotation=15)
        ax.set_title('Forecasting Model Comparison', fontsize=14, fontweight='bold')
        ax.set_ylabel('Error')
        ax.legend()
        for i, (r, m) in enumerate(zip(rmse_vals, mae_vals)):
            ax.text(i - width / 2, r + 50, str(r), ha='center', fontweight='bold', fontsize=9)
            ax.text(i + width / 2, m + 50, str(m), ha='center', fontweight='bold', fontsize=9)
        save_plot(fig, '17_forecast_model_comparison')

    return forecast_results


# ============================================================================
# PHASE 7: ANOMALY DETECTION
# ============================================================================
def anomaly_detection(df):
    print("\n" + "=" * 70)
    print("PHASE 7: ANOMALY DETECTION")
    print("=" * 70)

    daily = df.groupby('Date').agg({
        'Traffic_Volume': 'mean',
        'Congestion_Level': 'mean'
    })

    # --- Method 1: Z-Score Based ---
    print("\n  Method 1: Z-Score based anomaly detection...")
    daily['TV_zscore'] = np.abs(stats.zscore(daily['Traffic_Volume']))
    daily['CL_zscore'] = np.abs(stats.zscore(daily['Congestion_Level']))
    daily['Is_Anomaly_ZScore'] = ((daily['TV_zscore'] > 2) | (daily['CL_zscore'] > 2)).astype(int)
    n_anomalies_z = daily['Is_Anomaly_ZScore'].sum()
    print(f"    Z-Score anomalies detected: {n_anomalies_z}")

    # --- Method 2: IQR Based ---
    print("  Method 2: IQR based anomaly detection...")
    Q1 = daily['Traffic_Volume'].quantile(0.25)
    Q3 = daily['Traffic_Volume'].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    daily['Is_Anomaly_IQR'] = (
        (daily['Traffic_Volume'] < lower) | (daily['Traffic_Volume'] > upper)
    ).astype(int)
    n_anomalies_iqr = daily['Is_Anomaly_IQR'].sum()
    print(f"    IQR anomalies detected: {n_anomalies_iqr}")

    # --- Method 3: Rolling Mean Residual ---
    print("  Method 3: Rolling mean residual based...")
    rolling_mean = daily['Traffic_Volume'].rolling(window=7, center=True).mean()
    residuals = daily['Traffic_Volume'] - rolling_mean
    resid_std = residuals.std()
    daily['Is_Anomaly_Residual'] = (np.abs(residuals) > 2 * resid_std).astype(int)
    n_anomalies_res = daily['Is_Anomaly_Residual'].sum()
    print(f"    Residual anomalies detected: {n_anomalies_res}")

    # Combined anomaly flag
    daily['Anomaly_Score'] = (daily['Is_Anomaly_ZScore'] +
                              daily['Is_Anomaly_IQR'] +
                              daily['Is_Anomaly_Residual'])
    daily['Is_Anomaly'] = (daily['Anomaly_Score'] >= 2).astype(int)
    n_final = daily['Is_Anomaly'].sum()
    print(f"    Combined anomalies (≥2 methods agree): {n_final}")

    # --- Visualization ---
    fig, axes = plt.subplots(3, 1, figsize=(14, 14))

    # Plot 1: Traffic Volume with anomalies
    anomalies = daily[daily['Is_Anomaly'] == 1]
    axes[0].plot(daily.index, daily['Traffic_Volume'], color='#1976D2',
                 alpha=0.7, linewidth=1, label='Traffic Volume')
    axes[0].scatter(anomalies.index, anomalies['Traffic_Volume'],
                    color='#FF1744', s=60, zorder=5, label=f'Anomalies ({n_final})',
                    edgecolors='black', linewidth=0.5)
    axes[0].set_title('Traffic Volume Anomalies', fontsize=14, fontweight='bold')
    axes[0].set_ylabel('Avg Traffic Volume')
    axes[0].legend()

    # Plot 2: Z-Scores
    axes[1].plot(daily.index, daily['TV_zscore'], color='#FF9800', linewidth=1)
    axes[1].axhline(y=2, color='red', linestyle='--', label='Threshold (z=2)')
    axes[1].set_title('Z-Score of Traffic Volume', fontsize=14, fontweight='bold')
    axes[1].set_ylabel('|Z-Score|')
    axes[1].legend()

    # Plot 3: Residuals
    axes[2].plot(daily.index, residuals, color='#4CAF50', linewidth=1)
    axes[2].axhline(y=2 * resid_std, color='red', linestyle='--', label=f'±2σ ({2*resid_std:.0f})')
    axes[2].axhline(y=-2 * resid_std, color='red', linestyle='--')
    axes[2].fill_between(daily.index, -2 * resid_std, 2 * resid_std, alpha=0.1, color='red')
    axes[2].set_title('Rolling Mean Residuals', fontsize=14, fontweight='bold')
    axes[2].set_ylabel('Residual')
    axes[2].set_xlabel('Date')
    axes[2].legend()

    fig.suptitle('Anomaly Detection in Bangalore Traffic',
                 fontsize=16, fontweight='bold', y=1.01)
    fig.tight_layout()
    save_plot(fig, '18_anomaly_detection')

    # Save anomaly data
    anomaly_df = daily[daily['Is_Anomaly'] == 1][['Traffic_Volume', 'Congestion_Level',
                                                    'Anomaly_Score']].round(2)
    anomaly_df.to_csv(os.path.join(OUTPUT_DIR, 'anomalies_detected.csv'))
    print(f"  [SAVED] outputs/anomalies_detected.csv")

    return daily


# ============================================================================
# PHASE 8: EXPORT CSV FOR R
# ============================================================================
def export_for_r(df):
    print("\n" + "=" * 70)
    print("PHASE 8: EXPORTING DATA FOR R VISUALIZATION")
    print("=" * 70)

    r_data = df[['Date', 'Area_Name', 'Road_Name', 'Traffic_Volume',
                 'Average_Speed', 'Congestion_Level', 'Road_Capacity_Utilization',
                 'Environmental_Impact', 'Public_Transport_Usage',
                 'Weather_Conditions', 'Month', 'Day_of_Week', 'Is_Weekend',
                 'Incident_Reports', 'Pedestrian_Cyclist_Count']].copy()
    r_path = os.path.join(OUTPUT_DIR, 'data_for_r.csv')
    r_data.to_csv(r_path, index=False)
    print(f"  [SAVED] {r_path}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================
def main():
    print("╔" + "═" * 68 + "╗")
    print("║  BANGALORE CITY TRAFFIC DATASET - COMPREHENSIVE ANALYSIS          ║")
    print("║  Multi-Tool Data Science Project (Python + SQL + R)               ║")
    print("╚" + "═" * 68 + "╝")
    print()

    # Phase 1: Load & preprocess
    df = load_and_preprocess()

    # Phase 2: SQL analysis
    sql_results = run_sql_analysis(df)

    # Phase 3: Feature engineering
    df = feature_engineering(df)

    # Phase 4: EDA
    corr_matrix = exploratory_data_analysis(df)

    # Phase 5: Time series analysis
    daily_ts, decomposition = time_series_analysis(df)

    # Phase 6A: Clustering
    cluster_results, km_labels = clustering_analysis(df)

    # Phase 6B: Forecasting
    forecast_results = forecasting_analysis(daily_ts)

    # Phase 7: Anomaly detection
    anomaly_data = anomaly_detection(df)

    # Phase 8: Export for R
    export_for_r(df)

    # Final summary
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"\n  Output directory: {OUTPUT_DIR}/")
    print(f"  Plots saved to:  {PLOTS_DIR}/")
    print(f"  SQL results:     {SQL_OUTPUT_DIR}/")
    print(f"  SQLite database: {DB_PATH}")
    print(f"\n  Total plots generated: {len(os.listdir(PLOTS_DIR))}")
    print("\n  Next step: Run 'Rscript r_visualizations.R' for R-based plots.")
    print("=" * 70)


if __name__ == '__main__':
    main()
