-- ============================================================================
-- Bangalore City Traffic Dataset - SQL Analysis
-- ============================================================================
-- This script contains SQL queries for analyzing traffic patterns in Bangalore.
-- Designed to run on SQLite (loaded via python_analysis.py).
-- ============================================================================

-- ============================================================================
-- 1. BASIC STATISTICS
-- ============================================================================

-- 1a. Total number of records
SELECT COUNT(*) AS total_records FROM traffic;

-- 1b. Date range of the dataset
SELECT
    MIN(Date) AS earliest_date,
    MAX(Date) AS latest_date,
    COUNT(DISTINCT Date) AS unique_dates
FROM traffic;

-- 1c. Summary statistics for numeric columns
SELECT
    'Traffic Volume' AS metric,
    ROUND(AVG(Traffic_Volume), 2) AS mean_value,
    MIN(Traffic_Volume) AS min_value,
    MAX(Traffic_Volume) AS max_value
FROM traffic
UNION ALL
SELECT
    'Average Speed',
    ROUND(AVG(Average_Speed), 2),
    ROUND(MIN(Average_Speed), 2),
    ROUND(MAX(Average_Speed), 2)
FROM traffic
UNION ALL
SELECT
    'Congestion Level',
    ROUND(AVG(Congestion_Level), 2),
    ROUND(MIN(Congestion_Level), 2),
    ROUND(MAX(Congestion_Level), 2)
FROM traffic
UNION ALL
SELECT
    'Road Capacity Utilization',
    ROUND(AVG(Road_Capacity_Utilization), 2),
    ROUND(MIN(Road_Capacity_Utilization), 2),
    ROUND(MAX(Road_Capacity_Utilization), 2)
FROM traffic;

-- 1d. Count of unique areas and roads
SELECT
    COUNT(DISTINCT Area_Name) AS unique_areas,
    COUNT(DISTINCT Road_Name) AS unique_roads
FROM traffic;

-- ============================================================================
-- 2. TOP CONGESTED LOCATIONS
-- ============================================================================

-- 2a. Top 10 most congested areas (by average congestion level)
SELECT
    Area_Name,
    ROUND(AVG(Congestion_Level), 2) AS avg_congestion,
    ROUND(AVG(Traffic_Volume), 0) AS avg_traffic_volume,
    ROUND(AVG(Average_Speed), 2) AS avg_speed,
    COUNT(*) AS record_count
FROM traffic
GROUP BY Area_Name
ORDER BY avg_congestion DESC
LIMIT 10;

-- 2b. Top 10 most congested roads/intersections
SELECT
    Road_Name,
    Area_Name,
    ROUND(AVG(Congestion_Level), 2) AS avg_congestion,
    ROUND(AVG(Traffic_Volume), 0) AS avg_traffic_volume,
    ROUND(AVG(Road_Capacity_Utilization), 2) AS avg_road_utilization
FROM traffic
GROUP BY Road_Name, Area_Name
ORDER BY avg_congestion DESC
LIMIT 10;

-- 2c. Areas with highest incident reports
SELECT
    Area_Name,
    SUM(Incident_Reports) AS total_incidents,
    ROUND(AVG(Congestion_Level), 2) AS avg_congestion,
    COUNT(*) AS record_count
FROM traffic
GROUP BY Area_Name
ORDER BY total_incidents DESC
LIMIT 10;

-- ============================================================================
-- 3. TRAFFIC BY MONTH
-- ============================================================================

-- 3a. Monthly average traffic volume and congestion
SELECT
    strftime('%Y-%m', Date) AS month,
    ROUND(AVG(Traffic_Volume), 0) AS avg_traffic_volume,
    ROUND(AVG(Congestion_Level), 2) AS avg_congestion,
    ROUND(AVG(Average_Speed), 2) AS avg_speed,
    ROUND(AVG(Road_Capacity_Utilization), 2) AS avg_utilization,
    SUM(Incident_Reports) AS total_incidents
FROM traffic
GROUP BY strftime('%Y-%m', Date)
ORDER BY month;

-- 3b. Month with highest traffic
SELECT
    strftime('%m', Date) AS month_num,
    CASE strftime('%m', Date)
        WHEN '01' THEN 'January'
        WHEN '02' THEN 'February'
        WHEN '03' THEN 'March'
        WHEN '04' THEN 'April'
        WHEN '05' THEN 'May'
        WHEN '06' THEN 'June'
        WHEN '07' THEN 'July'
        WHEN '08' THEN 'August'
        WHEN '09' THEN 'September'
        WHEN '10' THEN 'October'
        WHEN '11' THEN 'November'
        WHEN '12' THEN 'December'
    END AS month_name,
    ROUND(AVG(Traffic_Volume), 0) AS avg_traffic_volume,
    ROUND(AVG(Congestion_Level), 2) AS avg_congestion
FROM traffic
GROUP BY month_num
ORDER BY avg_traffic_volume DESC;

-- ============================================================================
-- 4. TRAFFIC BY DAY OF WEEK
-- ============================================================================

-- 4a. Average traffic by day of week (0=Sunday, 6=Saturday)
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
    ROUND(AVG(Average_Speed), 2) AS avg_speed,
    SUM(Incident_Reports) AS total_incidents
FROM traffic
GROUP BY strftime('%w', Date)
ORDER BY CAST(strftime('%w', Date) AS INTEGER);

-- 4b. Weekday vs Weekend comparison
SELECT
    CASE
        WHEN strftime('%w', Date) IN ('0', '6') THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type,
    ROUND(AVG(Traffic_Volume), 0) AS avg_traffic_volume,
    ROUND(AVG(Congestion_Level), 2) AS avg_congestion,
    ROUND(AVG(Average_Speed), 2) AS avg_speed,
    ROUND(AVG(Road_Capacity_Utilization), 2) AS avg_utilization,
    COUNT(*) AS total_records
FROM traffic
GROUP BY day_type;

-- ============================================================================
-- 5. WEATHER IMPACT ANALYSIS
-- ============================================================================

-- 5a. Traffic patterns by weather condition
SELECT
    Weather_Conditions,
    COUNT(*) AS record_count,
    ROUND(AVG(Traffic_Volume), 0) AS avg_traffic_volume,
    ROUND(AVG(Congestion_Level), 2) AS avg_congestion,
    ROUND(AVG(Average_Speed), 2) AS avg_speed,
    SUM(Incident_Reports) AS total_incidents
FROM traffic
GROUP BY Weather_Conditions
ORDER BY avg_congestion DESC;

-- ============================================================================
-- 6. ROADWORK IMPACT ANALYSIS
-- ============================================================================

-- 6a. Impact of construction on traffic
SELECT
    Roadwork_Activity,
    COUNT(*) AS record_count,
    ROUND(AVG(Traffic_Volume), 0) AS avg_traffic_volume,
    ROUND(AVG(Congestion_Level), 2) AS avg_congestion,
    ROUND(AVG(Average_Speed), 2) AS avg_speed,
    ROUND(AVG(Road_Capacity_Utilization), 2) AS avg_utilization
FROM traffic
GROUP BY Roadwork_Activity;

-- ============================================================================
-- 7. ENVIRONMENTAL & PUBLIC TRANSPORT ANALYSIS
-- ============================================================================

-- 7a. Correlation between public transport usage and congestion
SELECT
    CASE
        WHEN Public_Transport_Usage < 30 THEN 'Low (<30%)'
        WHEN Public_Transport_Usage BETWEEN 30 AND 60 THEN 'Medium (30-60%)'
        ELSE 'High (>60%)'
    END AS pt_usage_level,
    COUNT(*) AS record_count,
    ROUND(AVG(Congestion_Level), 2) AS avg_congestion,
    ROUND(AVG(Environmental_Impact), 2) AS avg_env_impact,
    ROUND(AVG(Traffic_Volume), 0) AS avg_traffic_volume
FROM traffic
GROUP BY pt_usage_level
ORDER BY avg_congestion DESC;

-- 7b. Top areas by environmental impact
SELECT
    Area_Name,
    ROUND(AVG(Environmental_Impact), 2) AS avg_env_impact,
    ROUND(AVG(Traffic_Volume), 0) AS avg_traffic_volume,
    ROUND(AVG(Congestion_Level), 2) AS avg_congestion
FROM traffic
GROUP BY Area_Name
ORDER BY avg_env_impact DESC
LIMIT 10;

-- ============================================================================
-- 8. SAFETY ANALYSIS
-- ============================================================================

-- 8a. Traffic signal compliance by area
SELECT
    Area_Name,
    ROUND(AVG(Traffic_Signal_Compliance), 2) AS avg_compliance,
    SUM(Incident_Reports) AS total_incidents,
    ROUND(AVG(Congestion_Level), 2) AS avg_congestion
FROM traffic
GROUP BY Area_Name
ORDER BY avg_compliance ASC
LIMIT 10;

-- 8b. Pedestrian and cyclist activity by area
SELECT
    Area_Name,
    ROUND(AVG(Pedestrian_Cyclist_Count), 0) AS avg_ped_cyclist,
    ROUND(AVG(Traffic_Volume), 0) AS avg_traffic_volume,
    ROUND(AVG(Average_Speed), 2) AS avg_speed
FROM traffic
GROUP BY Area_Name
ORDER BY avg_ped_cyclist DESC
LIMIT 10;

-- ============================================================================
-- END OF SQL ANALYSIS
-- ============================================================================
