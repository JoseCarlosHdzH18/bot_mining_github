from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Job, JobStatus
from app.services.job_dispatcher import job_dispatcher
from app.config import MAX_PAGES
from app.utils.logger import logger

router = APIRouter()


@router.post("/start")
def start_scraper(
    query: str = Query(..., description="GitHub search query"),
    pages: int = Query(MAX_PAGES, description="Number of pages to search"),
    db: Session = Depends(get_db)
):
    """
    Start a new mining job.
    
    Examples:
    - /scraper/start?query=language:python
    - /scraper/start?query=stars:>1000&pages=5
    """
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    if pages > 20:
        raise HTTPException(status_code=400, detail="Maximum pages limit is 20")
    
    try:
        job = job_dispatcher.create_job(query=query, db=db)
        
        task_info = job_dispatcher.dispatch_search_tasks(job.id, query, pages)
        
        logger.info(f"Started scraper job {job.id} with query '{query}', {pages} pages")
        
        return {
            "status": "started",
            "job_id": job.id,
            "query": query,
            "pages": pages,
            "tasks_enqueued": len(task_info)
        }
        
    except Exception as e:
        logger.error(f"Error starting scraper: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start scraper: {str(e)}")


@router.post("/stop/{job_id}")
def stop_scraper(job_id: int, db: Session = Depends(get_db)):
    """Stop a running job."""
    try:
        job = job_dispatcher.get_job(job_id, db)
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        if job.status not in [JobStatus.PENDING, JobStatus.RUNNING]:
            raise HTTPException(status_code=400, detail=f"Job is not in a stoppable state: {job.status}")
        
        job_dispatcher.update_job_status(job_id, JobStatus.CANCELLED, db=db)
        
        logger.info(f"Stopped scraper job {job_id}")
        
        return {
            "status": "stopped",
            "job_id": job_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping scraper job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to stop job: {str(e)}")


@router.get("/status/{job_id}")
def job_status(job_id: int, db: Session = Depends(get_db)):
    """Get job status."""
    try:
        job = job_dispatcher.get_job(job_id, db)
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        return {
            "job_id": job.id,
            "query": job.query,
            "status": job.status.value,
            "processed_repos": job.processed_repos,
            "processed_users": job.processed_users,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
