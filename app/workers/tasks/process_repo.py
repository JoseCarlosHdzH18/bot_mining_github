import time

from app.core.github_client import github_client
from app.db.session import SessionLocal
from app.db.models import Repository, User, Technology, LogLevel
from app.services.job_dispatcher import job_dispatcher
from app.workers.job_queue import job_queue
from app.workers.tasks.process_user import process_user_task
from app.utils.logger import logger
from app.utils.metrics import repositories_processed_total, github_requests_total


def process_repo_task(repo_full_name: str, job_id) -> dict:
    """
    Process a repository: fetch contributors and enqueue user processing tasks.
    
    Args:
        repo_full_name: Full repository name (owner/repo)
        job_id: Job ID in the database
        
    Returns:
        Dict with task results
    """
    job_id = int(job_id) if isinstance(job_id, str) else job_id
    start_time = time.time()
    db = SessionLocal()
    
    try:
        logger.info(f"Processing repository {repo_full_name} for job {job_id}")
        
        owner, repo_name = repo_full_name.split("/")
        
        github_requests_total.labels(endpoint="repo_contributors", status="attempt").inc()
        
        contributors = github_client.get_repo_contributors(owner, repo_name)
        
        github_requests_total.labels(endpoint="repo_contributors", status="success").inc()
        
        repo = db.query(Repository).filter(Repository.full_name == repo_full_name).first()
        if repo:
            repo.processed = True
            db.commit()
        
        if repo and repo.language:
            tech = db.query(Technology).filter(Technology.name == repo.language).first()
            if tech:
                tech.repositories_count += 1
            else:
                tech = Technology(name=repo.language, repositories_count=1)
                db.add(tech)
            db.commit()
        
        users_enqueued = 0
        for contributor in contributors:
            username = contributor.get("login")
            if not username:
                continue
                
            existing_user = db.query(User).filter(User.login == username).first()
            
            if not existing_user:
                user = User(
                    github_id=contributor.get("id", 0),
                    login=username,
                    html_url=contributor.get("html_url", ""),
                    job_id=job_id,
                    processed=False
                )
                db.add(user)
                db.commit()
            
            job_queue.enqueue(
                process_user_task,
                username,
                job_id,
                result_ttl=86400
            )
            users_enqueued += 1
        
        job_dispatcher.increment_processed(job_id, users=users_enqueued)
        
        job_dispatcher.add_execution_log(
            job_id=job_id,
            level=LogLevel.INFO,
            message=f"Processed repo {repo_full_name}, enqueued {users_enqueued} users",
            duration=time.time() - start_time,
            entity_type="repository",
            entity_id=repo.id if repo else None
        )
        
        repositories_processed_total.labels(status="processed").inc()
        
        logger.info(f"Completed processing repo {repo_full_name}, enqueued {users_enqueued} users")
        
        return {
            "success": True,
            "repo": repo_full_name,
            "contributors_found": len(contributors),
            "users_enqueued": users_enqueued
        }
        
    except Exception as e:
        logger.error(f"Error processing repo {repo_full_name}: {str(e)}")
        
        job_dispatcher.add_execution_log(
            job_id=job_id,
            level=LogLevel.ERROR,
            message=f"Process repo {repo_full_name} failed: {str(e)}",
            duration=time.time() - start_time,
            entity_type="repository"
        )
        
        github_requests_labels = github_requests_total.labels(endpoint="repo_contributors", status="error")
        github_requests_labels.inc()
        
        repositories_processed_total.labels(status="error").inc()
        
        return {
            "success": False,
            "repo": repo_full_name,
            "error": str(e)
        }
    finally:
        db.close()
