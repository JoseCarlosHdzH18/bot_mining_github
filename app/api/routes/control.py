from fastapi import APIRouter, HTTPException
from app.workers.job_queue import job_queue
from app.utils.metrics import queue_size
from app.utils.logger import logger
import redis

router = APIRouter()


@router.post("/pause")
def pause_queue():
    """
    Pause the job queue (drain workers).
    
    Returns:
        Status message
    """
    try:
        job_queue.pause()
        logger.info("Queue paused")
        return {"status": "paused", "message": "Queue paused - workers will finish current jobs"}
    except Exception as e:
        logger.error(f"Error pausing queue: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to pause queue: {str(e)}")


@router.post("/resume")
def resume_queue():
    """
    Resume the job queue.
    
    Returns:
        Status message
    """
    try:
        job_queue.resume()
        logger.info("Queue resumed")
        return {"status": "resumed", "message": "Queue resumed"}
    except Exception as e:
        logger.error(f"Error resuming queue: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to resume queue: {str(e)}")


@router.get("/info")
def queue_info():
    """
    Get queue information.
    
    Returns:
        Queue statistics
    """
    try:
        queued_jobs = len(job_queue)
        failed_jobs = job_queue.failed_job_registry.count
        workers = job_queue.get_worker_ids()
        
        return {
            "queue_name": job_queue.name,
            "queued_jobs": queued_jobs,
            "failed_jobs": failed_jobs,
            "active_workers": len(workers) if workers else 0,
            "worker_ids": list(workers) if workers else [],
        }
    except Exception as e:
        logger.error(f"Error getting queue info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get queue info: {str(e)}")


@router.delete("/failed")
def clear_failed_jobs():
    """
    Clear all failed jobs from the queue.
    
    Returns:
        Status message
    """
    try:
        failed_registry = job_queue.failed_job_registry
        count = failed_registry.count
        
        failed_registry.cleanup()
        
        logger.info(f"Cleared {count} failed jobs")
        return {"status": "success", "cleared_count": count}
    except Exception as e:
        logger.error(f"Error clearing failed jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear failed jobs: {str(e)}")


@router.delete("/queued")
def clear_queued_jobs():
    """
    Clear all queued jobs from the queue.
    
    Returns:
        Status message
    """
    try:
        count = len(job_queue)
        
        job_queue.empty()
        
        logger.info(f"Cleared {count} queued jobs")
        return {"status": "success", "cleared_count": count}
    except Exception as e:
        logger.error(f"Error clearing queued jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear queued jobs: {str(e)}")
