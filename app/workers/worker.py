from rq import Worker, Queue
from redis import Redis
import os

redis_conn = Redis.from_url(os.getenv("REDIS_URL"))

if __name__ == "__main__":
    worker = Worker([Queue("github_jobs", connection=redis_conn)])
    worker.work()