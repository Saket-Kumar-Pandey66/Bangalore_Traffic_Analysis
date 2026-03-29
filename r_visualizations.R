# ============================================================================
# Bangalore City Traffic Dataset - R Visualizations
# ============================================================================
# This script creates advanced visualizations using ggplot2
# Run after python_analysis.py (which exports data_for_r.csv)
# Usage: Rscript r_visualizations.R
# ============================================================================

# --- Setup user library path ---
user_lib <- Sys.getenv("R_LIBS_USER")
if (user_lib == "") user_lib <- file.path(Sys.getenv("HOME"), "R", "library")
dir.create(user_lib, showWarnings = FALSE, recursive = TRUE)
.libPaths(c(user_lib, .libPaths()))

# --- Install and load required packages ---
required_packages <- c("ggplot2", "dplyr", "tidyr", "scales",
                       "RColorBrewer", "viridis", "corrplot",
                       "gridExtra", "lubridate")

for (pkg in required_packages) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    install.packages(pkg, repos = "https://cran.r-project.org", quiet = TRUE,
                     lib = user_lib)
  }
  library(pkg, character.only = TRUE)
}

cat("============================================================\n")
cat("  BANGALORE TRAFFIC DATASET - R VISUALIZATIONS (ggplot2)\n")
cat("============================================================\n\n")

# --- Configuration ---
input_file <- "outputs/data_for_r.csv"
output_dir <- "outputs/r_plots"
dir.create(output_dir, showWarnings = FALSE, recursive = TRUE)

# --- Load Data ---
cat("Loading data...\n")
df <- read.csv(input_file, stringsAsFactors = FALSE)
df$Date <- as.Date(df$Date)
df$Month <- factor(df$Month, levels = 1:12,
                   labels = month.abb)
df$Day_of_Week <- factor(df$Day_of_Week,
                         levels = c("Monday", "Tuesday", "Wednesday",
                                    "Thursday", "Friday", "Saturday", "Sunday"))
df$Weekend <- ifelse(df$Is_Weekend == 1, "Weekend", "Weekday")

cat(sprintf("  Loaded %d rows, %d columns\n", nrow(df), ncol(df)))
cat(sprintf("  Date range: %s to %s\n", min(df$Date), max(df$Date)))
cat(sprintf("  Areas: %d, Roads: %d\n\n",
            length(unique(df$Area_Name)),
            length(unique(df$Road_Name))))

# --- Custom Theme ---
theme_traffic <- function() {
  theme_minimal() +
    theme(
      plot.title = element_text(size = 14, face = "bold", hjust = 0.5,
                                margin = margin(b = 10)),
      plot.subtitle = element_text(size = 11, hjust = 0.5, color = "gray40"),
      axis.title = element_text(size = 11, face = "bold"),
      axis.text = element_text(size = 9),
      legend.position = "bottom",
      legend.title = element_text(face = "bold"),
      panel.grid.minor = element_blank(),
      plot.margin = margin(15, 15, 15, 15)
    )
}

# ============================================================================
# PLOT 1: Boxplot - Traffic Volume by Day of Week
# ============================================================================
cat("Creating Plot 1: Boxplot - Traffic Volume by Day of Week...\n")

p1 <- ggplot(df, aes(x = Day_of_Week, y = Traffic_Volume, fill = Day_of_Week)) +
  geom_boxplot(alpha = 0.8, outlier.size = 1, outlier.alpha = 0.3) +
  scale_fill_viridis_d(option = "D") +
  labs(title = "Traffic Volume Distribution by Day of Week",
       subtitle = "Bangalore City Traffic Dataset",
       x = "Day of Week", y = "Traffic Volume") +
  theme_traffic() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1),
        legend.position = "none")

ggsave(file.path(output_dir, "r_01_boxplot_day_of_week.png"),
       p1, width = 10, height = 6, dpi = 150)
cat("  [SAVED] r_01_boxplot_day_of_week.png\n")

# ============================================================================
# PLOT 2: Boxplot - Congestion Level by Area
# ============================================================================
cat("Creating Plot 2: Boxplot - Congestion by Area...\n")

area_order <- df %>%
  group_by(Area_Name) %>%
  summarize(med = median(Congestion_Level, na.rm = TRUE)) %>%
  arrange(desc(med)) %>%
  pull(Area_Name)

df$Area_Ordered <- factor(df$Area_Name, levels = area_order)

p2 <- ggplot(df, aes(x = Area_Ordered, y = Congestion_Level, fill = Area_Ordered)) +
  geom_boxplot(alpha = 0.8, outlier.size = 0.8, outlier.alpha = 0.3) +
  scale_fill_viridis_d(option = "C") +
  labs(title = "Congestion Level Distribution by Area",
       subtitle = "Areas ordered by median congestion (descending)",
       x = "Area", y = "Congestion Level (%)") +
  theme_traffic() +
  theme(axis.text.x = element_text(angle = 60, hjust = 1, size = 7),
        legend.position = "none")

ggsave(file.path(output_dir, "r_02_boxplot_congestion_by_area.png"),
       p2, width = 14, height = 7, dpi = 150)
cat("  [SAVED] r_02_boxplot_congestion_by_area.png\n")

# ============================================================================
# PLOT 3: Monthly Trend Line Plot
# ============================================================================
cat("Creating Plot 3: Monthly Trend Plot...\n")

monthly_trend <- df %>%
  group_by(Month) %>%
  summarize(
    avg_volume = mean(Traffic_Volume, na.rm = TRUE),
    avg_congestion = mean(Congestion_Level, na.rm = TRUE),
    avg_speed = mean(Average_Speed, na.rm = TRUE),
    .groups = "drop"
  )

p3 <- ggplot(monthly_trend, aes(x = as.numeric(Month))) +
  geom_line(aes(y = avg_congestion, color = "Avg Congestion"),
            linewidth = 1.2) +
  geom_point(aes(y = avg_congestion, color = "Avg Congestion"), size = 3) +
  geom_line(aes(y = avg_speed, color = "Avg Speed"),
            linewidth = 1.2) +
  geom_point(aes(y = avg_speed, color = "Avg Speed"), size = 3) +
  scale_x_continuous(breaks = 1:12, labels = month.abb) +
  scale_color_manual(values = c("Avg Congestion" = "#E53935",
                                "Avg Speed" = "#1E88E5")) +
  labs(title = "Monthly Traffic Trends",
       subtitle = "Average Congestion Level and Speed by Month",
       x = "Month", y = "Value", color = "Metric") +
  theme_traffic()

ggsave(file.path(output_dir, "r_03_monthly_trends.png"),
       p3, width = 10, height = 6, dpi = 150)
cat("  [SAVED] r_03_monthly_trends.png\n")

# ============================================================================
# PLOT 4: Daily Time Series with Smoothing
# ============================================================================
cat("Creating Plot 4: Daily Time Series...\n")

daily_avg <- df %>%
  group_by(Date) %>%
  summarize(avg_volume = mean(Traffic_Volume, na.rm = TRUE),
            .groups = "drop")

p4 <- ggplot(daily_avg, aes(x = Date, y = avg_volume)) +
  geom_line(color = "#90CAF9", alpha = 0.6, linewidth = 0.4) +
  geom_smooth(method = "loess", span = 0.1, color = "#1565C0",
              se = TRUE, fill = "#BBDEFB", alpha = 0.3) +
  labs(title = "Daily Average Traffic Volume Over Time",
       subtitle = "With LOESS smoothing curve and confidence band",
       x = "Date", y = "Average Traffic Volume") +
  theme_traffic()

ggsave(file.path(output_dir, "r_04_daily_time_series.png"),
       p4, width = 12, height = 6, dpi = 150)
cat("  [SAVED] r_04_daily_time_series.png\n")

# ============================================================================
# PLOT 5: Correlation Heatmap
# ============================================================================
cat("Creating Plot 5: Correlation Heatmap...\n")

numeric_cols <- df %>%
  select(Traffic_Volume, Average_Speed, Congestion_Level,
         Road_Capacity_Utilization, Environmental_Impact,
         Public_Transport_Usage, Incident_Reports,
         Pedestrian_Cyclist_Count) %>%
  na.omit()

cor_matrix <- cor(numeric_cols)

# Long format for ggplot
cor_long <- as.data.frame(as.table(cor_matrix))
names(cor_long) <- c("Var1", "Var2", "Correlation")

p5 <- ggplot(cor_long, aes(x = Var1, y = Var2, fill = Correlation)) +
  geom_tile(color = "white", linewidth = 0.5) +
  geom_text(aes(label = round(Correlation, 2)), size = 3) +
  scale_fill_gradient2(low = "#1565C0", mid = "white", high = "#C62828",
                       midpoint = 0, limits = c(-1, 1)) +
  labs(title = "Correlation Heatmap of Traffic Variables",
       x = "", y = "") +
  theme_traffic() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1, size = 8),
        axis.text.y = element_text(size = 8))

ggsave(file.path(output_dir, "r_05_correlation_heatmap.png"),
       p5, width = 10, height = 9, dpi = 150)
cat("  [SAVED] r_05_correlation_heatmap.png\n")

# ============================================================================
# PLOT 6: Distribution Plots (Histograms + Density)
# ============================================================================
cat("Creating Plot 6: Distribution Plots...\n")

p6a <- ggplot(df, aes(x = Traffic_Volume)) +
  geom_histogram(aes(y = after_stat(density)), bins = 40,
                 fill = "#42A5F5", alpha = 0.7, color = "white") +
  geom_density(color = "#1565C0", linewidth = 1) +
  labs(title = "Distribution of Traffic Volume",
       x = "Traffic Volume", y = "Density") +
  theme_traffic()

p6b <- ggplot(df, aes(x = Average_Speed)) +
  geom_histogram(aes(y = after_stat(density)), bins = 40,
                 fill = "#66BB6A", alpha = 0.7, color = "white") +
  geom_density(color = "#2E7D32", linewidth = 1) +
  labs(title = "Distribution of Average Speed",
       x = "Average Speed (km/h)", y = "Density") +
  theme_traffic()

p6c <- ggplot(df, aes(x = Congestion_Level)) +
  geom_histogram(aes(y = after_stat(density)), bins = 40,
                 fill = "#EF5350", alpha = 0.7, color = "white") +
  geom_density(color = "#C62828", linewidth = 1) +
  labs(title = "Distribution of Congestion Level",
       x = "Congestion Level (%)", y = "Density") +
  theme_traffic()

p6d <- ggplot(df, aes(x = Environmental_Impact)) +
  geom_histogram(aes(y = after_stat(density)), bins = 40,
                 fill = "#FFA726", alpha = 0.7, color = "white") +
  geom_density(color = "#E65100", linewidth = 1) +
  labs(title = "Distribution of Environmental Impact",
       x = "Environmental Impact", y = "Density") +
  theme_traffic()

p6_combined <- grid.arrange(p6a, p6b, p6c, p6d, ncol = 2,
                            top = "Distribution of Key Traffic Variables")

ggsave(file.path(output_dir, "r_06_distributions.png"),
       p6_combined, width = 14, height = 10, dpi = 150)
cat("  [SAVED] r_06_distributions.png\n")

# ============================================================================
# PLOT 7: Weekday vs Weekend Comparison
# ============================================================================
cat("Creating Plot 7: Weekday vs Weekend...\n")

wk_compare <- df %>%
  group_by(Weekend) %>%
  summarize(
    avg_volume = mean(Traffic_Volume, na.rm = TRUE),
    avg_congestion = mean(Congestion_Level, na.rm = TRUE),
    avg_speed = mean(Average_Speed, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  pivot_longer(cols = starts_with("avg_"),
               names_to = "Metric", values_to = "Value") %>%
  mutate(Metric = case_when(
    Metric == "avg_volume" ~ "Traffic Volume",
    Metric == "avg_congestion" ~ "Congestion Level",
    Metric == "avg_speed" ~ "Average Speed"
  ))

p7 <- ggplot(wk_compare, aes(x = Metric, y = Value, fill = Weekend)) +
  geom_bar(stat = "identity", position = position_dodge(width = 0.7),
           width = 0.6, alpha = 0.9) +
  geom_text(aes(label = round(Value, 1)),
            position = position_dodge(width = 0.7),
            vjust = -0.5, size = 3.5, fontface = "bold") +
  scale_fill_manual(values = c("Weekday" = "#1E88E5", "Weekend" = "#43A047")) +
  labs(title = "Weekday vs Weekend Traffic Comparison",
       x = "", y = "Average Value", fill = "Day Type") +
  theme_traffic() +
  facet_wrap(~ Metric, scales = "free_y", nrow = 1)

ggsave(file.path(output_dir, "r_07_weekday_vs_weekend.png"),
       p7, width = 14, height = 6, dpi = 150)
cat("  [SAVED] r_07_weekday_vs_weekend.png\n")

# ============================================================================
# PLOT 8: Weather Impact
# ============================================================================
cat("Creating Plot 8: Weather Impact...\n")

weather_stats <- df %>%
  group_by(Weather_Conditions) %>%
  summarize(
    avg_congestion = mean(Congestion_Level, na.rm = TRUE),
    avg_volume = mean(Traffic_Volume, na.rm = TRUE),
    count = n(),
    .groups = "drop"
  ) %>%
  arrange(desc(avg_congestion))

p8 <- ggplot(weather_stats, aes(x = reorder(Weather_Conditions, avg_congestion),
                                y = avg_congestion,
                                fill = avg_congestion)) +
  geom_bar(stat = "identity", width = 0.6, alpha = 0.9) +
  geom_text(aes(label = round(avg_congestion, 1)),
            hjust = -0.2, size = 4, fontface = "bold") +
  scale_fill_gradient(low = "#FFF9C4", high = "#D32F2F") +
  coord_flip() +
  labs(title = "Average Congestion by Weather Condition",
       x = "Weather Condition", y = "Average Congestion Level (%)") +
  theme_traffic() +
  theme(legend.position = "none")

ggsave(file.path(output_dir, "r_08_weather_impact.png"),
       p8, width = 10, height = 6, dpi = 150)
cat("  [SAVED] r_08_weather_impact.png\n")

# ============================================================================
# PLOT 9: Scatter Plot - Speed vs Congestion
# ============================================================================
cat("Creating Plot 9: Speed vs Congestion Scatter...\n")

p9 <- ggplot(df, aes(x = Average_Speed, y = Congestion_Level,
                      color = Traffic_Volume)) +
  geom_point(alpha = 0.3, size = 1) +
  geom_smooth(method = "lm", color = "#D32F2F", linewidth = 1,
              se = TRUE, fill = "#FFCDD2") +
  scale_color_viridis_c(option = "B", name = "Traffic\nVolume") +
  labs(title = "Average Speed vs Congestion Level",
       subtitle = "Colored by Traffic Volume",
       x = "Average Speed (km/h)", y = "Congestion Level (%)") +
  theme_traffic()

ggsave(file.path(output_dir, "r_09_speed_vs_congestion.png"),
       p9, width = 10, height = 7, dpi = 150)
cat("  [SAVED] r_09_speed_vs_congestion.png\n")

# ============================================================================
# PLOT 10: Violin Plot - Congestion by Day Type
# ============================================================================
cat("Creating Plot 10: Violin Plot...\n")

p10 <- ggplot(df, aes(x = Weekend, y = Congestion_Level, fill = Weekend)) +
  geom_violin(alpha = 0.7, draw_quantiles = c(0.25, 0.5, 0.75)) +
  geom_jitter(width = 0.15, alpha = 0.03, size = 0.5) +
  scale_fill_manual(values = c("Weekday" = "#5C6BC0", "Weekend" = "#26A69A")) +
  labs(title = "Congestion Level Distribution: Weekday vs Weekend",
       subtitle = "Violin plot with quartile lines",
       x = "", y = "Congestion Level (%)") +
  theme_traffic() +
  theme(legend.position = "none")

ggsave(file.path(output_dir, "r_10_violin_congestion.png"),
       p10, width = 8, height = 6, dpi = 150)
cat("  [SAVED] r_10_violin_congestion.png\n")

# ============================================================================
# SUMMARY
# ============================================================================
cat("\n============================================================\n")
cat("  R VISUALIZATION COMPLETE\n")
cat("============================================================\n")
cat(sprintf("  Total plots saved: %d\n", length(list.files(output_dir))))
cat(sprintf("  Output directory: %s/\n", output_dir))
cat("============================================================\n")
