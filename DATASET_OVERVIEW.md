# Spark Cluster Log Dataset Overview

## Dataset Summary

This dataset contains real-world Apache Spark cluster logs from production workloads running on YARN (Yet Another Resource Negotiator). The dataset provides students with hands-on experience analyzing large-scale distributed computing logs to understand cluster behavior, performance patterns, and operational characteristics.

## Dataset Statistics

- **Total Applications**: 194 Spark applications
- **Total Log Files**: 3,852 container log files
- **Total Size**: ~2.8 GB (uncompressed log data)
- **Time Period**: Logs from 2015-2017 (based on timestamps)
- **Platform**: Apache Spark 1.6.0 running on Hadoop YARN

## Folder Structure

```
data/
├── application_<cluster_id>_<app_number>/
│   ├── container_<cluster_id>_<app_number>_01_000001.log  (ApplicationMaster)
│   ├── container_<cluster_id>_<app_number>_01_000002.log  (Executor)
│   ├── container_<cluster_id>_<app_number>_01_000003.log  (Executor)
│   └── ... (additional executor logs)
└── Spark.tar.gz  (archive of all logs)
```

### Directory Naming Convention

Each application directory follows the pattern: `application_<cluster_id>_<app_number>`

- **cluster_id**: Unix timestamp (in milliseconds) when the YARN ResourceManager started
- **app_number**: Sequential application number within that cluster

Example: `application_1485248649253_0052`
- Cluster ID: 1485248649253 (January 24, 2017)
- Application Number: 0052 (the 52nd application on this cluster)

### Container Naming Convention

Each log file follows the pattern: `container_<cluster_id>_<app_number>_<attempt>_<container_id>.log`

- **attempt**: Application attempt number (usually 01)
- **container_id**: Unique container ID starting from 000001

Container 000001 is always the ApplicationMaster, and subsequent containers are executors.

## Cluster Distribution

The dataset includes logs from 6 different YARN clusters:

| Cluster ID        | Start Date (approx) | Number of Applications |
|-------------------|---------------------|------------------------|
| 1440487435730     | Aug 2015            | 1                      |
| 1448006111297     | Nov 2015            | 2                      |
| 1460011102909     | Apr 2016            | 1                      |
| 1472621869829     | Aug 2016            | 8                      |
| 1474351042505     | Sep 2016            | 1                      |
| 1485248649253     | Jan 2017            | 181                    |

The majority of applications (181) come from cluster 1485248649253, providing substantial data for analysis.

## Log File Types

### ApplicationMaster Log (container_*_01_000001.log)

The ApplicationMaster is the first container launched for each Spark application. It manages the application lifecycle and coordinates with the YARN ResourceManager.

**Key Information Found in ApplicationMaster Logs:**
- Application registration and configuration
- Executor allocation requests
- Resource requirements (memory, CPU cores)
- Container launch details
- Cluster topology (which nodes executors run on)
- Application progress and heartbeat information

**Example ApplicationMaster Log Entry:**
```
17/03/29 10:04:43 INFO YarnAllocator: Will request 16 executor containers, each with 5 cores and 28160 MB memory including 2560 MB overhead
```

### Executor Logs (container_*_01_00000X.log)

Executors are worker processes that run tasks and store data for the Spark application.

**Key Information Found in Executor Logs:**
- Executor startup and registration
- Task execution details (task IDs, stages)
- Data processing operations (RDD operations, broadcast variables)
- Memory usage (block storage, cache)
- Performance metrics (task timing, data shuffle)
- Python/PySpark execution details

**Example Executor Log Entry:**
```
17/03/29 10:11:10 INFO executor.Executor: Running task 8.0 in stage 1.0 (TID 9)
17/03/29 10:11:10 INFO rdd.HadoopRDD: Input split: hdfs://10.10.34.11:9000/pjhe/input/orderHDFSseq.txt:11902664+1487833
17/03/29 10:11:13 INFO python.PythonRunner: Times: total = 2282, boot = 1190, init = 59, finish = 1033
```

## Sample Application Analysis: application_1485248649253_0052

This application demonstrates a typical PySpark job running on YARN:

- **Total Containers**: 15 files
- **Size**: 236 KB
- **Executors**: 16 requested executors
- **Resources per Executor**: 5 CPU cores, 25.6 GB memory
- **Programming Language**: PySpark (Python on Spark)
- **Input Data**: HDFS file at `/pjhe/input/orderHDFSseq.txt`
- **Cluster Topology**: Multi-node cluster with mesos-slave-X hostnames

### Log File Sizes in This Application

Log files vary significantly in size:
- Small logs (39-41 lines): Short-lived executors or failed containers
- Medium logs (265-282 lines): Normal executor logs with task execution
- Large log (513 lines): ApplicationMaster with detailed coordination logs

## Understanding Spark on YARN Architecture

### Key Components Visible in Logs

1. **ResourceManager**: Central YARN service managing cluster resources
2. **ApplicationMaster**: Per-application coordinator running in container_*_01_000001
3. **NodeManagers**: Services on each worker node managing containers
4. **Executors**: Worker processes running Spark tasks in containers 000002+

### Execution Flow

1. Client submits Spark application to YARN
2. YARN launches ApplicationMaster in first container
3. ApplicationMaster requests executor containers from ResourceManager
4. NodeManagers launch executor containers on worker nodes
5. Executors register with Spark Driver (running in ApplicationMaster)
6. Driver assigns tasks to executors
7. Executors process data and report results
8. Application completes and containers are released

## Common Log Patterns to Analyze

### Resource Allocation
```
INFO YarnAllocator: Will request X executor containers, each with Y cores and Z MB memory
INFO YarnAllocator: Container request (host: Any, capability: <memory:X, vCores:Y>)
```

### Task Execution
```
INFO executor.Executor: Running task X.Y in stage Z.W (TID N)
INFO executor.Executor: Finished task X.Y in stage Z.W (TID N)
```

### Data Processing
```
INFO rdd.HadoopRDD: Input split: hdfs://host:port/path/file:offset+length
INFO python.PythonRunner: Times: total = X, boot = Y, init = Z, finish = W
```

### Memory Management
```
INFO storage.MemoryStore: MemoryStore started with capacity X GB
INFO storage.MemoryStore: Block broadcast_X stored as bytes in memory (estimated size Y, free Z)
```

### Performance Metrics
```
INFO python.PythonRunner: Times: total = 2282, boot = 1190, init = 59, finish = 1033
```
This shows: total execution time, Python interpreter boot time, initialization, and task finish time.

## Assignment Ideas and Learning Objectives

### Beginner Level
1. **Basic Statistics**: Count applications, containers, and log entries
2. **Pattern Extraction**: Extract all unique log levels (INFO, WARN, ERROR)
3. **Resource Analysis**: Parse and aggregate requested memory and CPU cores

### Intermediate Level
1. **Performance Analysis**: Calculate average task execution times per application
2. **Cluster Utilization**: Analyze container distribution across worker nodes
3. **Failure Analysis**: Identify failed tasks and containers
4. **Timeline Reconstruction**: Build execution timeline from timestamps

### Advanced Level
1. **Bottleneck Detection**: Identify performance bottlenecks using task timing
2. **Resource Optimization**: Recommend optimal resource configurations
3. **Data Skew Analysis**: Detect data skew from task duration variations
4. **Shuffle Performance**: Analyze data shuffle patterns and costs
5. **Memory Usage Patterns**: Track memory allocation and cache efficiency

## Key Spark Concepts Demonstrated

### RDD Operations
Logs show RDD (Resilient Distributed Dataset) operations:
- `HadoopRDD`: Reading from HDFS
- `CacheManager`: Caching RDD partitions in memory
- Broadcast variables: Shared read-only data

### Stages and Tasks
- **Stage**: Set of tasks that can run in parallel
- **Task**: Unit of work sent to one executor
- **TID**: Task ID (unique across application)

### Broadcast Variables
Used to efficiently distribute large read-only values:
```
INFO broadcast.TorrentBroadcast: Started reading broadcast variable X
```

### Memory Storage
```
INFO storage.MemoryStore: Block rdd_X_Y stored as bytes in memory (estimated size A, free B)
```

## Technical Details

### Spark Version
Apache Spark 1.6.0 with Hadoop 2.2.0

### Python Integration
- PySpark with py4j-0.9 bridge
- Python interpreter bootstrap visible in logs
- Execution timing broken down by phase

### HDFS Integration
- Input files read from HDFS (Hadoop Distributed File System)
- Files staged in HDFS: spark-assembly JAR, pyspark.zip, py4j.zip

### Security
```
INFO SecurityManager: authentication disabled; ui acls disabled
```
Cluster runs without authentication (test/development environment).

## Data Source Information

This dataset appears to be production or test cluster logs from a real deployment. The logs have been collected and archived for educational purposes.

### Data Privacy
- Usernames visible: "yarn", "curi"
- Internal IP addresses: 10.10.34.0/24 network
- Hostnames: mesos-slave-X, mesos-master-X pattern

## Getting Started with Analysis

### Using Spark to Analyze Spark Logs

This dataset is perfect for a meta-learning exercise: using Apache Spark to analyze Apache Spark logs!

**Recommended Approach:**
1. Load log files as text files into Spark RDD or DataFrame
2. Parse log entries (timestamp, log level, component, message)
3. Apply transformations to extract insights
4. Use Spark SQL for aggregations and queries
5. Visualize results using matplotlib or similar tools

### Sample PySpark Code Structure

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import regexp_extract, col

# Initialize Spark
spark = SparkSession.builder.appName("LogAnalysis").getOrCreate()

# Load all log files
logs_df = spark.read.text("data/application_*/*.log")

# Parse log entries
parsed_logs = logs_df.select(
    regexp_extract('value', r'^(\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})', 1).alias('timestamp'),
    regexp_extract('value', r'(INFO|WARN|ERROR|DEBUG)', 1).alias('level'),
    regexp_extract('value', r'(INFO|WARN|ERROR|DEBUG)\s+([^:]+):', 2).alias('component'),
    col('value').alias('message')
)

# Analyze log levels
log_level_counts = parsed_logs.groupBy('level').count()
log_level_counts.show()

# Find most active components
component_counts = parsed_logs.groupBy('component').count().orderBy('count', ascending=False)
component_counts.show(20)
```

### Alternative: Python with Polars

For faster analysis on a single machine:

```python
import polars as pl
from pathlib import Path

# Read all logs
log_files = list(Path('data').glob('application_*/*.log'))
logs = pl.concat([pl.read_csv(f, has_header=False) for f in log_files])

# Parse and analyze
# ... use polars expressions for efficient processing
```

## Common Challenges and Tips

### Challenge 1: Log Format Variations
**Issue**: Not all log lines follow the same format
**Solution**: Use flexible regex patterns and handle parse failures gracefully

### Challenge 2: Large Data Volume
**Issue**: 2.8GB of text data can be slow to process
**Solution**:
- Use Spark for distributed processing
- Sample data initially for rapid prototyping
- Use efficient parsers (avoid line-by-line Python loops)

### Challenge 3: Multiline Log Entries
**Issue**: Some log entries span multiple lines (e.g., launch context details)
**Solution**: Implement multiline aggregation logic or focus on single-line entries

### Challenge 4: Timestamp Formats
**Issue**: Timestamps are in YY/MM/DD format
**Solution**: Parse using datetime with format string `%y/%m/%d %H:%M:%S`

## Expected Insights

Students should be able to discover:

1. **Resource Patterns**: Most applications request similar resource configurations
2. **Execution Times**: Task execution times follow a distribution (some fast, some slow)
3. **Data Locality**: Tasks try to run on nodes with data (see host preferences)
4. **Stage Dependencies**: Applications have multiple stages with dependencies
5. **Memory Usage**: Memory usage patterns and cache efficiency
6. **Failure Rates**: Some containers/tasks may fail and retry
7. **Cluster Utilization**: How work is distributed across cluster nodes

## References and Further Reading

- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [YARN Architecture](https://hadoop.apache.org/docs/current/hadoop-yarn/hadoop-yarn-site/YARN.html)
- [Spark on YARN](https://spark.apache.org/docs/latest/running-on-yarn.html)
- [Spark Monitoring and Instrumentation](https://spark.apache.org/docs/latest/monitoring.html)

## Dataset Attribution

This dataset is intended for educational purposes. Students should focus on learning distributed computing concepts and log analysis techniques.

## File and Folder Inventory

```
Total: 194 application directories
Total: 3,852 log files
Average: ~20 containers per application
Size range per application: 40 KB - 50 MB
Average application size: ~14 MB
```

## Quick Start Command Examples

```bash
# Count total applications
ls -d data/application_*/ | wc -l

# Count total log files
find data -name "*.log" | wc -l

# Find largest application by file count
for dir in data/application_*/; do echo "$(ls "$dir" | wc -l) $dir"; done | sort -rn | head -5

# Extract all ERROR messages
grep -r "ERROR" data/application_*/*.log > all_errors.txt

# Count log messages by severity
grep -roh "\(INFO\|WARN\|ERROR\|DEBUG\)" data/application_*/*.log | sort | uniq -c

# Find Python execution times
grep -r "python.PythonRunner: Times" data/application_*/*.log | head -20
```

## Conclusion

This dataset provides a rich, real-world foundation for understanding Apache Spark internals, distributed computing challenges, and log analysis techniques. Students will gain practical experience with big data technologies while developing valuable data engineering and analytical skills.

Good luck with your analysis!
