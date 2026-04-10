from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional, List

from app.db.session import get_db
from app.db.models import Job, JobStatus, Repository, User, Technology
from app.services.job_dispatcher import job_dispatcher

router = APIRouter()


@router.get("/jobs")
def get_jobs(
    status: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all jobs with optional status filter.
    
    Args:
        status: Filter by job status (pending, running, completed, failed, cancelled)
        limit: Maximum number of jobs to return
        
    Returns:
        List of jobs
    """
    try:
        job_status = None
        if status:
            try:
                job_status = JobStatus(status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
        
        jobs = job_dispatcher.get_jobs(status=job_status, limit=limit, db=db)
        
        return {
            "jobs": [
                {
                    "id": job.id,
                    "query": job.query,
                    "status": job.status.value,
                    "total_repos": job.total_repos,
                    "processed_repos": job.processed_repos,
                    "total_users": job.total_users,
                    "processed_users": job.processed_users,
                    "error_message": job.error_message,
                    "created_at": job.created_at.isoformat() if job.created_at else None,
                    "started_at": job.started_at.isoformat() if job.started_at else None,
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                }
                for job in jobs
            ],
            "count": len(jobs)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get jobs: {str(e)}")


@router.get("/jobs/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    """
    Get a specific job by ID.
    
    Args:
        job_id: Job ID
        
    Returns:
        Job information
    """
    try:
        job = job_dispatcher.get_job(job_id, db)
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        repos_count = db.query(Repository).filter(Repository.job_id == job_id).count()
        users_count = db.query(User).filter(User.job_id == job_id).count()
        
        return {
            "id": job.id,
            "query": job.query,
            "status": job.status.value,
            "total_repos": job.total_repos,
            "processed_repos": job.processed_repos,
            "total_users": job.total_users,
            "processed_users": job.processed_users,
            "error_message": job.error_message,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "repositories_count": repos_count,
            "users_count": users_count,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job: {str(e)}")


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """
    Get system statistics.
    
    Returns:
        System statistics
    """
    try:
        total_jobs = db.query(Job).count()
        pending_jobs = db.query(Job).filter(Job.status == JobStatus.PENDING).count()
        running_jobs = db.query(Job).filter(Job.status == JobStatus.RUNNING).count()
        completed_jobs = db.query(Job).filter(Job.status == JobStatus.COMPLETED).count()
        failed_jobs = db.query(Job).filter(Job.status == JobStatus.FAILED).count()
        
        total_repos = db.query(Repository).count()
        processed_repos = db.query(Repository).filter(Repository.processed == True).count()
        
        total_users = db.query(User).count()
        processed_users = db.query(User).filter(User.processed == True).count()
        sent_to_dolibarr = db.query(User).filter(User.sent_to_dolibarr == True).count()
        
        top_languages = db.query(
            Technology.name,
            Technology.repositories_count
        ).order_by(Technology.repositories_count.desc()).limit(10).all()
        
        return {
            "jobs": {
                "total": total_jobs,
                "pending": pending_jobs,
                "running": running_jobs,
                "completed": completed_jobs,
                "failed": failed_jobs,
            },
            "repositories": {
                "total": total_repos,
                "processed": processed_repos,
            },
            "users": {
                "total": total_users,
                "processed": processed_users,
                "sent_to_dolibarr": sent_to_dolibarr,
            },
            "top_languages": [
                {"name": lang, "count": count}
                for lang, count in top_languages
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
