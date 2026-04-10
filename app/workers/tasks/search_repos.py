import time
from typing import Optional

from app.core.github_client import github_client
from app.db.session import SessionLocal
from app.db.models import Repository, JobStatus, LogLevel
from app.services.job_dispatcher import job_dispatcher
from app.workers.job_queue import job_queue
from app.workers.tasks.process_repo import process_repo_task
from app.utils.logger import logger
from app.utils.metrics import repositories_processed_total, github_requests_total


def search_repos_task(query: str, page: int, job_id) -> dict:
    """
    Search repositories task that fetches repos from GitHub and enqueues processing tasks.
    
    Args:
        query: GitHub search query
        page: Page number for pagination
        job_id: Job ID in the database
        
    Returns:
        Dict with task results
    """
    job_id = int(job_id) if isinstance(job_id, str) else job_id
    start_time = time.time()
    db = SessionLocal()
    
    try:
        logger.info(f"Starting search task for job {job_id}, query: {query}, page: {page}")
        
        github_requests_total.labels(endpoint="search_repositories", status="attempt").inc()
        
        result = github_client.search_repositories(query=query, page=page)
        items = result.get("items", [])
        
        github_requests_total.labels(endpoint="search_repositories", status="success").inc()
        
        logger.info(f"Found {len(items)} repositories for job {job_id}, page {page}")
        
        repos_enqueued = 0
        for repo_data in items:
            existing = db.query(Repository).filter(Repository.github_id == repo_data["id"]).first()
            
            if not existing:
                repo = Repository(
                    github_id=repo_data["id"],
                    name=repo_data["name"],
                    full_name=repo_data["full_name"],
                    owner=repo_data["owner"]["login"],
                    description=repo_data.get("description"),
                    stars=repo_data.get("stargazers_count", 0),
                    forks=repo_data.get("forks_count", 0),
                    language=repo_data.get("language"),
                    url=repo_data["html_url"],
                    job_id=job_id,
                    processed=False
                )
                db.add(repo)
            
            job_queue.enqueue(
                process_repo_task,
                repo_data["full_name"],
                int(job_id) if isinstance(job_id, str) else job_id,
                result_ttl=86400
            )
            repos_enqueued += 1
        
        db.commit()
        
        job_dispatcher.increment_processed(job_id, repos=repos_enqueued)
        
        job_dispatcher.add_execution_log(
            job_id=job_id,
            level=LogLevel.INFO,
            message=f"Search page {page} completed, enqueued {repos_enqueued} repos",
            duration=time.time() - start_time,
            entity_type="search_page",
            entity_id=page
        )
        
        repositories_processed_total.labels(status="discovered").inc(repos_enqueued)
        
        logger.info(f"Completed search task for job {job_id}, page {page}, enqueued {repos_enqueued} repos")
        
        return {
            "success": True,
            "page": page,
            "repos_found": len(items),
            "repos_enqueued": repos_enqueued
        }
        
    except Exception as e:
        logger.error(f"Error in search task for job {job_id}, page {page}: {str(e)}")
        
        job_dispatcher.add_execution_log(
            job_id=job_id,
            level=LogLevel.ERROR,
            message=f"Search page {page} failed: {str(e)}",
            duration=time.time() - start_time,
            entity_type="search_page",
            entity_id=page
        )
        
        github_requests_total.labels(endpoint="search_repositories", status="error").inc()
        
        repositories_processed_total.labels(status="error").inc(len(items) if 'items' in locals() else 0)
        
        return {
            "success": False,
            "page": page,
            "error": str(e)
        }
    finally:
        db.close()
