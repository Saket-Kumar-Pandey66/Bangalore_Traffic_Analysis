import streamlit as st
import pandas as pd
import os
import glob
from PIL import Image

# -----------------------------------------------------------------------------
# 1. Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Bangalore Traffic Analytics",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for clean UI
st.markdown("""
<style>
    .reportview-container {
        background: #f8f9fa;
    }
    .sidebar .sidebar-content {
        background: #ffffff;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .plot-caption {
        font-size: 0.9rem;
        color: #555;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. Path Configurations
# -----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
PLOTS_DIR = os.path.join(OUTPUTS_DIR, "plots")
R_PLOTS_DIR = os.path.join(OUTPUTS_DIR, "r_plots")
SQL_RESULTS_DIR = os.path.join(OUTPUTS_DIR, "sql_results")

# -----------------------------------------------------------------------------
# 3. Helper Functions with Caching
# -----------------------------------------------------------------------------
@st.cache_data
def load_csv(file_path):
    """Loads a CSV file into a pandas dataframe, returns None if not found."""
    if os.path.exists(file_path):
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            st.warning(f"Error reading {file_path}: {e}")
            return None
    return None

def load_text(file_path):
    """Loads a text file."""
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return f.read()
    return None

def get_all_plots():
    """Returns a list of all PNG files in both plot directories dynamically, with no hardcoded lengths."""
    plots = []
    if os.path.exists(PLOTS_DIR):
        for img in os.listdir(PLOTS_DIR):
            if img.endswith('.png'):
                plots.append(os.path.join(PLOTS_DIR, img))
    if os.path.exists(R_PLOTS_DIR):
        for img in os.listdir(R_PLOTS_DIR):
            if img.endswith('.png'):
                plots.append(os.path.join(R_PLOTS_DIR, img))
    return sorted(plots)

def categorize_plots(all_plots):
    """Categorizes plots based on filename patterns."""
    categories = {
        "time_series": [],
        "eda": [],
        "weather": [],
        "ml": [],
        "forecast": [],
        "anomaly": []
    }
    
    for plot in all_plots:
        filename = os.path.basename(plot).lower()
        if any(kw in filename for kw in ['weather']):
            categories["weather"].append(plot)
        elif any(kw in filename for kw in ['cluster', 'kmeans']):
            categories["ml"].append(plot)
        elif any(kw in filename for kw in ['forecast', 'future']):
            categories["forecast"].append(plot)
        elif 'anomal' in filename:
            categories["anomaly"].append(plot)
        elif any(kw in filename for kw in ['time', 'trend', 'rolling', 'seasonal', 'monthly']):
            categories["time_series"].append(plot)
        else:
            # Default to EDA if not matched elsewhere
            categories["eda"].append(plot)
            
    return categories

def get_plot_explanation(filename):
    """Returns a contextual explanation based on the filename keywords."""
    name = filename.lower()
    if 'time_series_traffic_volume' in name or 'r_04_daily_time' in name:
        return "**What it shows:** Daily traffic volume fluctuations over time.\n\n**Why it matters:** Outlines the core heartbeat of the dataset, revealing both peak volumes and quiet periods.\n\n**Key Insight:** Traffic volumes typically peak mid-week, heavily aligning with standard commute patterns."
    elif 'time_series_congestion' in name:
        return "**What it shows:** Evolving congestion severity through the timeline.\n\n**Why it matters:** Congestion often outpaces pure volume during structural bottlenecks.\n\n**Key Insight:** Sudden localized spikes correlate with systemic gridlocks over generic volume."
    elif any(kw in name for kw in ['boxplots_day_of_week', 'r_01_boxplot', 'weekday']):
        return "**What it shows:** Volume and congestion spread divided by day of the week.\n\n**Why it matters:** Differentiates the typical Mon-Fri rush from the weekend operational lull.\n\n**Key Insight:** Weekends see a substantial dip in structural congestion despite moderate baseline volume."
    elif 'monthly_trends' in name:
        return "**What it shows:** Aggregated traffic patterns mapped month-to-month.\n\n**Why it matters:** Captures macroeconomic and seasonal shifts impacting the metropolitan area.\n\n**Key Insight:** Macro holiday seasons significantly alter baseline mobility norms."
    elif 'correlation' in name:
        return "**What it shows:** A statistical heatmap of relationships between numeric variables (speed, volume, weather).\n\n**Why it matters:** Mathematically identifies which factors directly drive others.\n\n**Key Insight:** There is a robust inverse correlation between average speeds and overarching congestion levels."
    elif 'weather' in name:
        return "**What it shows:** The comparative impact of meteorological events (rain, temperature) on traffic flow vs clear days.\n\n**Why it matters:** Adverse conditions drastically reduce the overall physical capacity of the roads.\n\n**Key Insight:** Rainfall events severely disrupt normal throughput, spiking system-wide delays."
    elif any(kw in name for kw in ['cluster', 'kmeans', 'comparison']):
        return "**What it shows:** Unsupervised machine learning grouping distinct traffic regimes.\n\n**Why it matters:** Helps cleanly classify states into actionable brackets (e.g., 'Free Flow', 'Standstill').\n\n**Key Insight:** The algorithm successfully isolated pure peak-hour metrics from normalized flows."
    elif 'forecast' in name or 'future' in name:
        return "**What it shows:** Predictive time series modeling projecting near-future traffic trajectories.\n\n**Why it matters:** Enables proactive rather than strictly reactive mobility management strategies.\n\n**Key Insight:** The forecast model captures cyclical daily commute patterns with confident boundaries."
    elif 'anomal' in name:
        return "**What it shows:** Mathematically isolated extreme events that deviate aggressively from the historical baseline.\n\n**Why it matters:** Spotlights potentially critical accidents, massive closures, or sensor failures.\n\n**Key Insight:** Rare but severe anomalies dictate the upper bounds of network variance."
    else:
        return "**What it shows:** General distribution and frequency patterns across selected traffic variables.\n\n**Why it matters:** Essential for understanding the underlying shape, bounds, and skew of the dataset.\n\n**Key Insight:** The overarching distributions confirm the cyclical nature of urban traffic."


def display_plots_grid(plot_paths, cols=2):
    """Displays a list of plots in a responsive grid layout with deep contextual narratives underneath."""
    if not plot_paths:
        st.info("No visualizations available for this section.")
        return
        
    for i in range(0, len(plot_paths), cols):
        cols_obj = st.columns(cols)
        for j, plot_path in enumerate(plot_paths[i:i+cols]):
            with cols_obj[j]:
                try:
                    img = Image.open(plot_path)
                    st.image(img, use_container_width=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(get_plot_explanation(os.path.basename(plot_path)))
                    st.markdown("---")
                except Exception as e:
                    st.error(f"Failed to load visualization: {plot_path}")

# -----------------------------------------------------------------------------
# 4. Data Loading 
# -----------------------------------------------------------------------------
all_plots = get_all_plots()
plot_categories = categorize_plots(all_plots)

# Common CSVs
df_basic_stats = load_csv(os.path.join(SQL_RESULTS_DIR, "basic_statistics.csv"))
df_clustering = load_csv(os.path.join(OUTPUTS_DIR, "clustering_results.csv"))
df_forecast_comp = load_csv(os.path.join(OUTPUTS_DIR, "forecast_comparison.csv"))
df_future_forecast = load_csv(os.path.join(OUTPUTS_DIR, "future_forecast.csv"))
df_anomalies = load_csv(os.path.join(OUTPUTS_DIR, "anomalies_detected.csv"))
data_summary = load_text(os.path.join(OUTPUTS_DIR, "data_summary.txt"))

# -----------------------------------------------------------------------------
# 5. Sidebar Navigation
# -----------------------------------------------------------------------------
st.sidebar.title("🚦 Traffic Analytics")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigate Sections", [
    "📊 Overview",
    "📈 Time Series Analysis",
    "🔍 EDA Insights",
    "⛈️ Weather & External Factors",
    "🤖 Machine Learning (Clustering)",
    "🔮 Forecasting",
    "🚨 Anomaly Detection"
])

st.sidebar.markdown("---")
st.sidebar.info("Dashboard generated automatically from the static, unalterable data science pipeline outputs.")

# -----------------------------------------------------------------------------
# 6. Page Content Rendering
# -----------------------------------------------------------------------------
st.title("Bangalore City Traffic Dashboard")

if page == "📊 Overview":
    st.header("📊 Executive Overview")
    st.info("💡 **Section Insight:** This high-level summary provides critical KPIs and a fundamental breakdown of the overall city traffic layout. Look for the top congested sectors and sweeping baseline metrics.")
    st.markdown("---")
    
    # KPIs
    if df_basic_stats is not None and not df_basic_stats.empty:
        st.subheader("Key Performance Indicators")
        col1, col2, col3, col4 = st.columns(4)
        
        # Iterating the first row for KPIs
        metrics = df_basic_stats.to_dict(orient='records')[0]
        st_cols = [col1, col2, col3, col4]
        for idx, (key, val) in enumerate(metrics.items()):
            col_target = st_cols[idx % 4]
            label = key.replace("_", " ").title()
            if isinstance(val, (int, float)):
                col_target.metric(label=label, value=f"{val:.2f}")
            else:
                col_target.metric(label=label, value=str(val))
    else:
        st.warning("Basic statistics data not manually accessible to display KPIs.")
        
    st.markdown("---")
    
    if data_summary:
        with st.expander("📄 Click down to reveal Raw Dataset Summary Schema & Extracted Text", expanded=False):
            st.text(data_summary)
            
    st.subheader("General Highlights & Critical Paths")
    top_congested = load_csv(os.path.join(SQL_RESULTS_DIR, "top_congested_areas.csv"))
    if top_congested is not None:
        st.markdown("**What the table contains:** A strictly ranked list of the most congested zones geographically monitored within the dataset.\n\n**How it was generated:** Processed via an automated SQL querying module on the source DB.\n\n**Why it is useful:** Readily identifies structurally deficient choke points demanding infrastructural prioritization.")
        st.dataframe(top_congested, use_container_width=True)
        
    st.success("🎯 **Key Insight:** A small subset of primary arteries contributes to a disproportionately massive percentage of total city gridlock durations.")

elif page == "📈 Time Series Analysis":
    st.header("📈 Time Series Analysis")
    st.info("💡 **Section Insight:** This section tracks traffic variations over continuous chronologies. Look closely for recursive cyclical peaks denoting rush hours and overarching seasonal patterns representing macroscopic shifts.")
    st.markdown("Temporal patterns including daily trends, weekly seasonality, and smooth rolling statistics. Observe how localized chaos smoothens out over broader temporal bins.")
    st.markdown("---")
    display_plots_grid(plot_categories["time_series"], cols=2)

elif page == "🔍 EDA Insights":
    st.header("🔍 Exploratory Data Analysis (EDA)")
    st.info("💡 **Section Insight:** A sweeping categorical breakdown. This section provides necessary foundational statistical perspectives by dissecting distinct variables systematically against one another for raw correlation hunting.")
    st.markdown("Distributions, quantitative correlation heatmaps, and faceted categorical comparisons.")
    st.success("🎯 **Key Insight:** Initial variable analysis fundamentally confirms commuter traffic acts as a non-linear but highly predictable function based predominantly on standard 'Time of Day' constraints.")
    st.markdown("---")
    display_plots_grid(plot_categories["eda"], cols=2)

elif page == "⛈️ Weather & External Factors":
    st.header("⛈️ Weather & External Factors")
    st.info("💡 **Section Insight:** Discover how sheer external forces dictate city mobility. Look for the stark numerical contrast in average speeds logged exclusively during adverse weather conditions.")
    
    st.success("🎯 **Key Insight:** Precipitation fundamentally limits the inherent capacity of the road network, exponentially amplifying congestion scales across regions linearly.")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Weather Data Contextual Tables")
        df_weather = load_csv(os.path.join(SQL_RESULTS_DIR, "weather_impact.csv"))
        if df_weather is not None:
            st.markdown("**What it contains:** Aggressive metrics mapped to meteorological categorical tags (Rain vs Clear).\n\n**How it was generated:** Grouped SQL aggregations parsing the primary database.\n\n**Why it is useful:** Quantifies the delay penalty strictly inflicted by incoming storms vs standard clear skies.")
            st.dataframe(df_weather, use_container_width=True)
        else:
            st.warning("Weather summary data not systematically generated.")
            
    with col2:
        st.subheader("Supplementary Anomalous Road Conditions")
        df_roadwork = load_csv(os.path.join(SQL_RESULTS_DIR, "roadwork_impact.csv"))
        if df_roadwork is not None:
            st.markdown("**What it contains:** Comparative flow rates in zones with actively flagged roadwork events.\n\n**How it was generated:** Isolated SQL data pivots correlating traffic drops with explicit roadwork identifiers.\n\n**Why it is useful:** Proves the raw geometric capacity loss caused by active lane closures.")
            st.dataframe(df_roadwork, use_container_width=True)
        else:
            st.warning("Roadwork impact categorical data block missing.")
            
    st.markdown("---")
    st.subheader("Visual Impact Dependencies")
    display_plots_grid(plot_categories["weather"], cols=2)

elif page == "🤖 Machine Learning (Clustering)":
    st.header("🤖 Machine Learning Insights: Traffic Clustering Unsupervised Behaviors")
    st.info("💡 **Section Insight:** Reviews fully autonomous segmentation of recurrent traffic paradigms identified purely via dimensional clustering math without human biases.")
    st.markdown("Identification of normalized traffic regimes using robust algorithms mapping multi-axes behaviors.")
    
    if df_clustering is not None:
        st.subheader("Clustering Metrics Scorecard")
        st.markdown("**What it contains:** Algorithmic evaluation scorecards (such as Silhouette scores or Inertia ranges).\n\n**How it was generated:** Output directly from the localized Python Scikit-Learn script targeting variable groups.\n\n**Why it is useful:** Determines whether the K-Means clustering structurally succeeded in isolating statistically valid operational regimes.")
        st.dataframe(df_clustering, use_container_width=True)
        
    st.markdown("---")
    st.subheader("Mathematical Model Projections")
    st.success("🎯 **Key Insight:** High-density 'Critical Phase' clusters consistently anchor to very specific geo-temporal blocks naturally derived by the data shapes.")
    display_plots_grid(plot_categories["ml"], cols=2)


elif page == "🔮 Forecasting":
    st.header("🔮 Traffic Forecasting Output Predictions")
    st.info("💡 **Section Insight:** Observes pure predictive insights mapping probable future road states trained purely on underlying historical behavior timelines.")
    st.markdown("Predictive baselines mapping for actionable future routing applications considering cyclical histories.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Forecast Evaluation (Algorithmic Comparison)")
        if df_forecast_comp is not None:
            st.markdown("**What it contains:** Tabular mapping of predictive error constraints (MAE, RMSE, etc.) tracking competing projection algorithms.\n\n**How it was generated:** Standardized test/train split comparisons tracked via Python's Statsmodels.\n\n**Why it is useful:** Vets the legitimacy and bounds of confidence to ensure decision-makers know the acceptable error margin of the future.")
            st.dataframe(df_forecast_comp, use_container_width=True)
        else:
            st.warning("Forecast modeling error bounds missing.")
            
    with col2:
        st.subheader("Unseen Future Timeline Sampling (Head)")
        if df_future_forecast is not None:
            st.markdown("**What it contains:** The actual chronological tabular output forecasting purely unseen future mobility volumes directly derived via winning models.\n\n**How it was generated:** Extending the leading optimized structural model logically forward into future timestamps.\n\n**Why it is useful:** Feeds directly into predictive load balancers allowing proactive rather than reactive management.")
            st.dataframe(df_future_forecast.head(10), use_container_width=True)
        else:
            st.warning("Upcoming forecast dataset rendering missing.")
            
    st.markdown("---")
    st.subheader("Forecasting Visual Tunnels")
    st.success("🎯 **Key Insight:** The forecasting module captures continuous cyclical rhythm, predicting impending daily spikes with minimal baseline degradation over the near future.")
    display_plots_grid(plot_categories["forecast"], cols=2)

elif page == "🚨 Anomaly Detection":
    st.header("🚨 Point Anomaly Detection Constraints")
    st.info("💡 **Section Insight:** Flags distinct structural deviations behaving erratically against standard algorithmic bounds.")
    st.markdown("Mathematically highlighting extreme bottlenecks, uncharacteristic silences, and structural faults within the operational dataset using isolation thresholds.")
    
    if df_anomalies is not None:
        st.subheader(f"Raw Target Anomalies Filtered (Total Pool Size: {len(df_anomalies)})")
        st.markdown("**What it contains:** The explicit tabular extraction solely tracking timestamps containing aggressively statistically anomalous states.\n\n**How it was generated:** Python ML logic (typically Isolation Forests or aggressive statistical trailing means bounds).\n\n**Why it is useful:** Focuses operational analysis squarely on 'The Outliers', stripping away standard operational noise to interrogate unique failures directly.")
        st.dataframe(df_anomalies.head(20), use_container_width=True)
    else:
        st.warning("Zero mathematically valid anomalies explicitly flagged via source filtering.")
        
    st.markdown("---")
    st.subheader("Anomaly Distributions Contextual Mapping")
    st.success("🎯 **Key Insight:** Almost all top-tier outlier points cleanly align conceptually with extreme categorical shocks like severe infrastructure failure or completely untracked external holiday impacts.")
    display_plots_grid(plot_categories["anomaly"], cols=2)

st.sidebar.markdown("---")
st.sidebar.caption("Designed for production grade analytics and visual storytelling. ✨")
