from pyspark.sql import SparkSession
from pyspark.sql.functions import (col, regexp_extract, count, min as spark_min, 
                                    max as spark_max, input_file_name, to_timestamp,
                                    unix_timestamp, countDistinct)
import os
import glob
import shutil
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

spark = SparkSession.builder \
    .appName("Problem2_Cluster_Usage_Analysis") \
    .getOrCreate()

print("Problem 2: Cluster Usage Analysis")


# for S3 bucket, i had a error on configuration AWS- so this part i used AI to debug
# LOG_PATH_S3A = LOG_PATH.replace("s3://", "s3a://")
S3_BUCKET = os.environ.get('SPARK_LOGS_BUCKET', 's3://zp134-assignment-spark-cluster-logs')
LOG_PATH = S3_BUCKET + "/data/application_*/*.log"

print(f"\nReading log files from: {LOG_PATH}")
print("Loading all log files...\n")

LOG_PATH_S3A = LOG_PATH.replace("s3://", "s3a://")
print(f"Using S3A protocol: {LOG_PATH_S3A}\n")

logs_raw = spark.read.text(LOG_PATH_S3A)

logs_with_path = logs_raw.withColumn('file_path', input_file_name())

logs_with_ids = logs_with_path.withColumn(
    'application_id',
    regexp_extract('file_path', r'application_(\d+_\d+)', 1)
).withColumn(
    'cluster_id',
    regexp_extract('file_path', r'application_(\d+)_', 1)
).withColumn(
    'app_number',
    regexp_extract('file_path', r'application_\d+_(\d+)', 1)
)

logs_with_ids = logs_with_ids.filter(col('application_id') != "")

logs_with_timestamps = logs_with_ids.withColumn(
    'timestamp_str',
    regexp_extract('value', r'^(\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})', 1)
).filter(col('timestamp_str') != "")

logs_with_timestamps = logs_with_timestamps.withColumn(
    'timestamp',
    to_timestamp('timestamp_str', 'yy/MM/dd HH:mm:ss')
)

logs_with_timestamps.cache()

print("\n" + "=" * 80)
print("ANALYSIS 1: Application Timeline Data")
print("=" * 80)

timeline_df = logs_with_timestamps.groupBy('cluster_id', 'app_number', 'application_id').agg(
    spark_min('timestamp').alias('start_time'),
    spark_max('timestamp').alias('end_time'),
    count('*').alias('log_lines')
)

timeline_df = timeline_df.withColumn(
    'duration_seconds',
    unix_timestamp('end_time') - unix_timestamp('start_time')
)

# Sort by cluster_id and start_time
timeline_df = timeline_df.orderBy('cluster_id', 'start_time')

print(f"Total applications found: {timeline_df.count()}")
timeline_df.show(10, truncate=False)

os.makedirs("data/output", exist_ok=True)
timeline_pd = timeline_df.toPandas()
timeline_pd.to_csv("data/output/problem2_timeline.csv", index=False)

print("✓ Saved to data/output/problem2_timeline.csv")

print("\n" + "=" * 80)
print("ANALYSIS 2: Cluster Summary Statistics")
print("=" * 80)

cluster_summary = timeline_df.groupBy('cluster_id').agg(
    count('*').alias('application_count'),
    spark_min('start_time').alias('first_app_start'),
    spark_max('end_time').alias('last_app_end')
)

cluster_summary = cluster_summary.orderBy(col('application_count').desc())

cluster_summary.show(truncate=False)

cluster_summary_pd = cluster_summary.toPandas()
cluster_summary_pd.to_csv("data/output/problem2_cluster_summary.csv", index=False)

print("✓ Saved to data/output/problem2_cluster_summary.csv")

print("\n" + "=" * 80)
print("ANALYSIS 3: Statistics Summary")
print("=" * 80)

total_clusters = cluster_summary.count()
total_apps = timeline_df.count()
cluster_stats = cluster_summary.collect()

most_used_cluster = cluster_stats[0]

summary_lines = []
summary_lines.append("=" * 80)
summary_lines.append("PROBLEM 2: CLUSTER USAGE ANALYSIS - SUMMARY REPORT")
summary_lines.append("=" * 80)
summary_lines.append("")
summary_lines.append(f"Total unique clusters: {total_clusters}")
summary_lines.append(f"Total applications: {total_apps}")
summary_lines.append("")
summary_lines.append("Cluster usage distribution:")
summary_lines.append("")
summary_lines.append(f"{'Cluster ID':<20} {'Applications':<15} {'First Start':<25} {'Last End':<25}")
summary_lines.append("-" * 85)

for row in cluster_stats:
    cluster_id = row['cluster_id']
    app_count = row['application_count']
    first_start = row['first_app_start']
    last_end = row['last_app_end']
    summary_lines.append(f"{cluster_id:<20} {app_count:<15} {str(first_start):<25} {str(last_end):<25}")

summary_lines.append("")
summary_lines.append(f"Most heavily used cluster: {most_used_cluster['cluster_id']}")
summary_lines.append(f"  - Applications: {most_used_cluster['application_count']}")
summary_lines.append(f"  - First activity: {most_used_cluster['first_app_start']}")
summary_lines.append(f"  - Last activity: {most_used_cluster['last_app_end']}")
summary_lines.append("")
summary_lines.append("=" * 80)
summary_lines.append("Analysis completed successfully!")
summary_lines.append("=" * 80)

summary_text = "\n".join(summary_lines)

print(summary_text)

os.makedirs("data/output", exist_ok=True)
with open("data/output/problem2_stats.txt", "w") as f:
    f.write(summary_text)

print("\n✓ Saved to data/output/problem2_stats.txt")

print("\n" + "=" * 80)
print("VISUALIZATION 1: Applications per Cluster (Bar Chart)")
print("=" * 80)

cluster_summary_pd = cluster_summary.select('cluster_id', 'application_count').toPandas()

plt.figure(figsize=(12, 6))
sns.set_style("whitegrid")
plt.bar(range(len(cluster_summary_pd)), cluster_summary_pd['application_count'])

plt.xlabel('Cluster ID', fontsize=12)
plt.ylabel('Number of Applications', fontsize=12)
plt.title('Application Distribution Across Clusters', fontsize=14, fontweight='bold')
plt.xticks(range(len(cluster_summary_pd)), cluster_summary_pd['cluster_id'], rotation=45, ha='right')

for i, v in enumerate(cluster_summary_pd['application_count']):
    plt.text(i, v + 1, str(v), ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('data/output/problem2_bar_chart.png', dpi=300, bbox_inches='tight')
plt.close()

print("✓ Saved to data/output/problem2_bar_chart.png")

print("\n" + "=" * 80)
print("VISUALIZATION 2: Job Duration Distribution (Density Plot)")
print("=" * 80)

largest_cluster_id = most_used_cluster['cluster_id']
largest_cluster_timeline = timeline_df.filter(col('cluster_id') == largest_cluster_id)

duration_pd = largest_cluster_timeline.select('duration_seconds').toPandas()

duration_pd = duration_pd[duration_pd['duration_seconds'] > 0]

print(f"Analyzing {len(duration_pd)} applications from cluster {largest_cluster_id}")
print(f"Duration range: {duration_pd['duration_seconds'].min():.2f}s to {duration_pd['duration_seconds'].max():.2f}s")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

sns.kdeplot(data=duration_pd, x='duration_seconds', fill=True, ax=ax1)
ax1.set_xlabel('Duration (seconds)', fontsize=11)
ax1.set_ylabel('Density', fontsize=11)
ax1.set_title('Job Duration Distribution (Linear Scale)', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3)

sns.kdeplot(data=duration_pd, x='duration_seconds', fill=True, ax=ax2, log_scale=True)
ax2.set_xlabel('Duration (seconds, log scale)', fontsize=11)
ax2.set_ylabel('Density', fontsize=11)
ax2.set_title('Job Duration Distribution (Log Scale)', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3)

plt.suptitle(f'Application Duration Analysis - Cluster {largest_cluster_id}', 
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('data/output/problem2_density_plot.png', dpi=300, bbox_inches='tight')
plt.close()

print("✓ Saved to data/output/problem2_density_plot.png")

print("\n" + "=" * 80)
print("ALL OUTPUTS GENERATED SUCCESSFULLY")
print("=" * 80)
print("\nOutput files created:")
print("  1. data/output/problem2_timeline.csv         - Application timeline data")
print("  2. data/output/problem2_cluster_summary.csv  - Cluster summary statistics")
print("  3. data/output/problem2_stats.txt            - Statistics report")
print("  4. data/output/problem2_bar_chart.png        - Applications per cluster")
print("  5. data/output/problem2_density_plot.png     - Duration distribution")
print("=" * 80)

logs_with_timestamps.unpersist()
spark.stop()

