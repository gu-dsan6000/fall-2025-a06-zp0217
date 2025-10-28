from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_extract, count, countDistinct, lit
import os
import glob
import shutil

spark = SparkSession.builder \
    .appName("Problem1_LogLevel_Distribution") \
    .getOrCreate()

print("=" * 80)
print("Problem 1: Log Level Distribution Analysis")
print("=" * 80)

# for S3 bucket, i had a error on configuration AWS- so this part i used AI to debug
# LOG_PATH_S3A = LOG_PATH.replace("s3://", "s3a://")
S3_BUCKET = os.environ.get('SPARK_LOGS_BUCKET', 's3://zp134-assignment-spark-cluster-logs')
LOG_PATH = S3_BUCKET + "/data/application_*/*.log"

print("\nReading log files from: {LOG_PATH}")
print("This may take a few minutes for large datasets...\n")

LOG_PATH_S3A = LOG_PATH.replace("s3://", "s3a://")
print(f"Using S3A protocol: {LOG_PATH_S3A}\n")

logs_raw = spark.read.text(LOG_PATH_S3A)

print(f"Total lines loaded: {logs_raw.count()}")


logs_parsed = logs_raw.select(
    col("value").alias("log_entry"),
    regexp_extract(col("value"), r'\b(INFO|WARN|ERROR|DEBUG)\b', 1).alias("log_level")
)

logs_with_level = logs_parsed.filter(col("log_level") != "")

logs_with_level.cache()

print("\n" + "=" * 80)
print("ANALYSIS 1: Log Level Counts")
print("=" * 80)

log_level_counts = logs_with_level.groupBy("log_level") \
    .agg(count("*").alias("count")) \
    .orderBy(col("count").desc())

log_level_counts.show()


os.makedirs("data/output", exist_ok=True)
counts_pd = log_level_counts.toPandas()
counts_pd.to_csv("data/output/problem1_counts.csv", index=False)

print("✓ Saved to data/output/problem1_counts.csv")

print("\n" + "=" * 80)
print("ANALYSIS 2: Random Sample of Log Entries")
print("=" * 80)

sample_logs = logs_with_level.sample(False, 0.001).limit(10)

sample_logs.show(10, truncate=True)

sample_pd = sample_logs.select("log_entry", "log_level").toPandas()
sample_pd.to_csv("data/output/problem1_sample.csv", index=False)

print("✓ Saved to data/output/problem1_sample.csv")

print("\n" + "=" * 80)
print("ANALYSIS 3: Summary Statistics")
print("=" * 80)

total_lines = logs_raw.count()
total_with_level = logs_with_level.count()
unique_levels = logs_with_level.select("log_level").distinct().count()

level_counts = log_level_counts.collect()

summary_lines = []
summary_lines.append("=" * 80)
summary_lines.append("PROBLEM 1: LOG LEVEL DISTRIBUTION - SUMMARY REPORT")
summary_lines.append("=" * 80)
summary_lines.append("")
summary_lines.append(f"Total log lines processed: {total_lines:,}")
summary_lines.append(f"Total lines with log levels: {total_with_level:,}")
summary_lines.append(f"Unique log levels found: {unique_levels}")
summary_lines.append("")
summary_lines.append("Log level distribution:")

for row in level_counts:
    level = row["log_level"]
    cnt = row["count"]
    percentage = (cnt / total_with_level) * 100
    summary_lines.append(f"  {level:6s}: {cnt:10,} ({percentage:5.2f}%)")

summary_lines.append("")
summary_lines.append("=" * 80)
summary_lines.append("Analysis completed successfully!")
summary_lines.append("=" * 80)

summary_text = "\n".join(summary_lines)

print(summary_text)

os.makedirs("data/output", exist_ok=True)
with open("data/output/problem1_summary.txt", "w") as f:
    f.write(summary_text)

print("\n✓ Saved to data/output/problem1_summary.txt")

print("\n" + "=" * 80)
print("ALL OUTPUTS GENERATED SUCCESSFULLY")
print("=" * 80)
print("\nOutput files created:")
print("  1. data/output/problem1_counts.csv    - Log level counts")
print("  2. data/output/problem1_sample.csv    - Random sample of 10 log entries")
print("  3. data/output/problem1_summary.txt   - Summary statistics report")
print("=" * 80)

logs_with_level.unpersist()
spark.stop()

# also i had issue with scp for dowenloading file- used AI to solve, it was due to file path error 