import time
from typing import Optional

from app.core.github_client import github_client
from app.core.dolibarr_client import dolibarr_client
from app.db.session import SessionLocal
from app.db.models import User, LogLevel
from app.services.job_dispatcher import job_dispatcher
from app.utils.logger import logger
from app.utils.metrics import users_processed_total, github_requests_total


def process_user_task(username: str, job_id) -> dict:
    """
    Process a user: fetch user data and send to Dolibarr.
    
    Args:
        username: GitHub username
        job_id: Job ID in the database
    """
    job_id = int(job_id) if isinstance(job_id, str) else job_id
    start_time = time.time()
    db = SessionLocal()
    
    try:
        logger.info(f"Processing user {username} for job {job_id}")
        
        github_requests_total.labels(endpoint="user", status="attempt").inc()
        
        user_data = github_client.get_user(username)
        
        github_requests_total.labels(endpoint="user", status="success").inc()
        
        github_requests_total.labels(endpoint="user_repos", status="attempt").inc()
        
        repos = github_client.get_user_repos(username)
        
        github_requests_total.labels(endpoint="user_repos", status="success").inc()
        
        user = db.query(User).filter(User.login == username).first()
        
        if user:
            user.name = user_data.get("name")
            user.email = user_data.get("email")
            user.company = user_data.get("company")
            user.location = user_data.get("location")
            user.bio = user_data.get("bio")
            user.followers = user_data.get("followers", 0)
            user.following = user_data.get("following", 0)
            user.public_repos = user_data.get("public_repos", 0)
            user.avatar_url = user_data.get("avatar_url")
            user.html_url = user_data.get("html_url")
            user.processed = True
            db.commit()
        
        languages = list(set([r.get("language") for r in repos if r.get("language")]))
        
        dolibarr_payload = {
            "login": user_data.get("login"),
            "name": user_data.get("name") or user_data.get("login"),
            "email": user_data.get("email"),
            "followers": user_data.get("followers", 0),
            "public_repos": user_data.get("public_repos", 0),
            "languages": languages,
            "company": user_data.get("company"),
            "location": user_data.get("location"),
            "bio": user_data.get("bio"),
            "html_url": user_data.get("html_url"),
        }
        
        try:
            dolibarr_result = dolibarr_client.send_user(dolibarr_payload)
            logger.info(f"Sent user {username} to Dolibarr: {dolibarr_result}")
            
            if user:
                user.sent_to_dolibarr = True
                db.commit()
                
        except Exception as dolibarr_error:
            logger.error(f"Failed to send user {username} to Dolibarr: {str(dolibarr_error)}")
        
        job_dispatcher.add_execution_log(
            job_id=job_id,
            level=LogLevel.INFO,
            message=f"Processed user {username}",
            duration=time.time() - start_time,
            entity_type="user",
            entity_id=user.id if user else None
        )
        
        users_processed_total.labels(status="processed").inc()
        
        logger.info(f"Completed processing user {username}")
        
        return {
            "success": True,
            "username": username,
            "repos_count": len(repos),
            "sent_to_dolibarr": user.sent_to_dolibarr if user else False
        }
        
    except Exception as e:
        logger.error(f"Error processing user {username}: {str(e)}")
        
        job_dispatcher.add_execution_log(
            job_id=job_id,
            level=LogLevel.ERROR,
            message=f"Process user {username} failed: {str(e)}",
            duration=time.time() - start_time,
            entity_type="user"
        )
        
        github_requests_total.labels(endpoint="user", status="error").inc()
        
        users_processed_total.labels(status="error").inc()
        
        return {
            "success": False,
            "username": username,
            "error": str(e)
        }
    finally:
        db.close()
