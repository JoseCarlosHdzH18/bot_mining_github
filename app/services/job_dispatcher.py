from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.db.models import Job, JobStatus, Repository, JobExecutionLog, LogLevel
from app.db.session import SessionLocal
from app.config import MAX_PAGES, PER_PAGE
from app.utils.logger import logger


class JobDispatcher:
    """Manages job creation, dispatching, and tracking."""

    def __init__(self):
        pass

    def create_job(self, query: str, db: Optional[Session] = None) -> Job:
        """Create a new job in the database."""
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True

        try:
            job = Job(
                query=query,
                status=JobStatus.PENDING,
                created_at=datetime.utcnow()
            )
            db.add(job)
            db.commit()
            db.refresh(job)
            logger.info(f"Created job {job.id} for query: {query}")
            return job
        finally:
            if close_db:
                db.close()

    def update_job_status(self, job_id: int, status: JobStatus, error_message: Optional[str] = None, db: Optional[Session] = None):
        """Update job status."""
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True

        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = status
                if status == JobStatus.RUNNING:
                    job.started_at = datetime.utcnow()
                elif status == JobStatus.COMPLETED or status == JobStatus.FAILED:
                    job.completed_at = datetime.utcnow()
                if error_message:
                    job.error_message = error_message
                db.commit()
                logger.info(f"Updated job {job_id} status to {status}")
        finally:
            if close_db:
                db.close()

    def increment_processed(self, job_id: int, repos: int = 0, users: int = 0, db: Optional[Session] = None):
        """Increment processed counts for a job."""
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True

        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.processed_repos += repos
                job.processed_users += users
                db.commit()
        finally:
            if close_db:
                db.close()

    def add_execution_log(self, job_id: int, level: LogLevel, message: str, duration: Optional[float] = None, entity_type: Optional[str] = None, entity_id: Optional[int] = None, db: Optional[Session] = None):
        """Add an execution log entry."""
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True

        try:
            log = JobExecutionLog(
                job_id=job_id,
                level=level,
                message=message,
                duration_seconds=duration,
                entity_type=entity_type,
                entity_id=entity_id
            )
            db.add(log)
            db.commit()
        finally:
            if close_db:
                db.close()

    def get_job(self, job_id: int, db: Optional[Session] = None) -> Optional[Job]:
        """Get job by ID."""
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True

        try:
            return db.query(Job).filter(Job.id == job_id).first()
        finally:
            if close_db:
                db.close()

    def get_jobs(self, status: Optional[JobStatus] = None, limit: int = 100, db: Optional[Session] = None) -> List[Job]:
        """Get jobs with optional status filter."""
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True

        try:
            query = db.query(Job)
            if status:
                query = query.filter(Job.status == status)
            return query.order_by(Job.created_at.desc()).limit(limit).all()
        finally:
            if close_db:
                db.close()

    def dispatch_search_tasks(self, job_id: int, query: str, pages: int = MAX_PAGES) -> List[Dict[str, Any]]:
        """Dispatch search tasks to the queue for each page."""
        from app.workers.job_queue import job_queue
        from app.workers.tasks.search_repos import search_repos_task

        task_info = []
        for page in range(1, pages + 1):
            job = job_queue.enqueue(
                search_repos_task,
                query,
                page,
                job_id,
                result_ttl=86400
            )
            task_info.append({"job_id": str(job.id), "page": page})
            logger.info(f"Enqueued search task for page {page}, job: {job.id}")

        self.update_job_status(job_id, JobStatus.RUNNING)
        return task_info


job_dispatcher = JobDispatcher()
