from prometheus_client import Counter, Histogram, Gauge

repositories_processed_total = Counter(
    "repositories_processed_total",
    "Total number of repositories processed",
    ["status"]
)

users_processed_total = Counter(
    "users_processed_total",
    "Total number of users processed",
    ["status"]
)

github_requests_total = Counter(
    "github_requests_total",
    "Total number of GitHub API requests",
    ["endpoint", "status"]
)

failed_jobs_total = Counter(
    "failed_jobs_total",
    "Total number of failed jobs"
)

job_duration_seconds = Histogram(
    "job_duration_seconds",
    "Job execution duration in seconds",
    ["job_type"]
)

active_jobs = Gauge(
    "active_jobs",
    "Number of currently active jobs"
)

queue_size = Gauge(
    "queue_size",
    "Number of jobs in the queue",
    ["queue_name"]
)
