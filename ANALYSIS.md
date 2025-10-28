# Analysis 


---

## Problem 1 — Log Level Distribution

### Approach
- Parsed the raw log dataset with Spark to extract the log level token per line.
- Filtered to known levels (`INFO`, `WARN`, `ERROR`) and counted occurrences using `groupBy`/`count`.
- Wrote out per-level counts and a short text summary.

```

================================================================================
PROBLEM1 - SUMMARY REPORT
================================================================================

Total log lines processed: 33,236,604
Total lines with log levels: 27,410,336
Unique log levels found: 3

Log level distribution:
  INFO  : 27,389,482 (99.92%)
  ERROR :     11,259 ( 0.04%)
  WARN  :      9,595 ( 0.04%)


The distribution is extremely skewed toward INFO, with WARN and ERROR representing a tiny fraction of total lines.


## Problem 2 — Cluster Usage & Job Duration

### Approach
- Aggregated application metadata by `clusterId` to compute the application counts and activity range per cluster.
- Built a simple bar chart for application counts and KDE plots for job-duration distributions (linear and log scales).
- Computed descriptive statistics for durations (min/median/mean/p95/p99) from the timeline data.

### Cluster Usage Summary
|    cluster_id |   application_count | first_app_start     | last_app_end        |
|--------------:|--------------------:|:--------------------|:--------------------|
| 1485248649253 |                 181 | 2017-01-24 17:00:28 | 2017-07-27 21:45:00 |
| 1472621869829 |                   8 | 2016-09-09 07:43:47 | 2016-09-09 10:07:06 |
| 1448006111297 |                   2 | 2016-04-07 10:45:21 | 2016-04-07 12:22:08 |
| 1474351042505 |                   1 | 2016-11-18 22:30:06 | 2016-11-19 00:59:04 |
| 1440487435730 |                   1 | 2015-09-01 18:14:40 | 2015-09-01 18:19:50 |
| 1460011102909 |                   1 | 2016-07-26 11:54:20 | 2016-07-26 12:19:25 |

### Duration Statistics
```
```
================================================================================
PROBLEM 2- SUMMARY REPORT
================================================================================

Total unique clusters: 6
Total applications: 194

Cluster usage distribution:

Cluster ID           Applications    First Start               Last End                 
-------------------------------------------------------------------------------------
1485248649253        181             2017-01-24 17:00:28       2017-07-27 21:45:00      
1472621869829        8               2016-09-09 07:43:47       2016-09-09 10:07:06      
1448006111297        2               2016-04-07 10:45:21       2016-04-07 12:22:08      
1474351042505        1               2016-11-18 22:30:06       2016-11-19 00:59:04      
1440487435730        1               2015-09-01 18:14:40       2015-09-01 18:19:50      
1460011102909        1               2016-07-26 11:54:20       2016-07-26 12:19:25      

Most heavily used cluster: 1485248649253
  - Applications: 181
  - First activity: 2017-01-24 17:00:28
  - Last activity: 2017-07-27 21:45:00

================================================================================
Analysis completed successfully!
================================================================================
```

### Visualizations
-

The linear plot shows the body of the distribution around short-to-medium jobs, while the log-scaled plot reveals the long tail of very large jobs (several orders of magnitude), which is otherwise compressed.

### Insights 

One cluster (**1485248649253**) dominates usage by application count; most other clusters show sporadic activity.
 The duration distribution is heavy–tailed: a concentration of short jobs with a meaningful long-tail of expensive runs. Monitoring should track both central tendency (median) and tail (p95/p99).



## Performance Observations

- The Spark workloads use wide aggregations (`groupBy` on levels and cluster IDs) which benefit from:
  - Enabling predicate pushdown and input file combining where possible.
  - Ensuring adequate shuffle partitions
   matched to cluster size.
  - Caching reused DataFrames only when reused downstream.



## Explanation of Visualizations

- **Bar chart (Applications per Cluster):** Highlights skew in cluster utilization and helps identify the primary execution environment for most jobs.
- **KDE (Linear scale):** Shows the main mass of job durations; useful to compare typical runs before/after optimizations.
- **KDE (Log scale):** Surfaces the long tail; essential for understanding extreme cases that can dominate costs and SLAs.

---


