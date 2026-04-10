# GitHub Miner Bot - Technical Documentation

## 1. Technologies

### Main Stack
| Technology | Purpose | Version |
|------------|---------|---------|
| **FastAPI** | REST API Framework | Latest |
| **PostgreSQL** | Primary Database | 15 |
| **Redis** | Message Queue & Cache | 7 |
| **RQ (Redis Queue)** | Async Workers | Latest |
| **SQLAlchemy** | Database ORM | Latest |
| **APScheduler** | Task Scheduler | Latest |
| **Prometheus** | Metrics Monitoring | Latest |
| **Grafana** | Metrics Visualization | Latest |

### Python Dependencies
```
fastapi, uvicorn, requests, redis, psycopg2-binary, sqlalchemy, 
prometheus-client, apscheduler, python-dotenv, rq
```

### Infrastructure
- **Docker & Docker Compose**: Full containerization
- **XAMPP**: Local server (development environment)

---

## 2. System Architecture

```
┌─────────────┐     ┌──────────┐     ┌─────────────┐
│   API       │────▶│  Redis   │────▶│  Workers   │
│  FastAPI    │     │  (RQ)    │     │  (python)   │
└─────────────┘     └──────────┘     └─────────────┘
       │                                   │
       ▼                                   ▼
┌─────────────┐                     ┌─────────────┐
│ PostgreSQL │◀───────────────────│ GitHub API  │
└─────────────┘                     └─────────────┘
       │
       ▼
┌─────────────┐
│  Dolibarr   │
│   (CRM)    │
└─────────────┘
```

---

## 3. Main Components

### REST API (`app/main.py`)
- Port: **8000**
- Available endpoints:
  - `/health/*` - Health checks
  - `/metrics/*` - Prometheus metrics
  - `/scraper/*` - Miner control
  - `/status/*` - Job status
  - `/control/*` - System control

### Database (`app/db/models/`)
- **Job**: Scraping jobs (query, status, progress)
- **Repository**: Extracted repositories
- **User**: GitHub users
- **Tech**: Detected technologies
- **ExecutionLog**: Execution logs

### Workers (`app/workers/`)
- Queue: `github_jobs`
- Async task processing
- Multiple replica support

### Scheduling (`scheduler/`)
- Automatic job scheduling
- APScheduler integration

---

## 4. Project Scope

### Implemented Features
1. **Repository Search**
   - Custom queries via GitHub Search API
   - Automatic pagination (up to 20 pages)
   - Star-based sorting

2. **Data Extraction**
   - Repositories: name, stars, forks, language, description
   - Repository contributors
   - User profiles

3. **Job Management**
   - Create, start, stop jobs
   - Real-time progress tracking
   - Statuses: pending, running, completed, failed, cancelled

4. **GitHub API Integration**
   - Automatic token management
   - Token rotation for rate limit handling
   - Automatic retries with backoff

5. **Dolibarr Integration**
   - Data synchronization to CRM
   - Configurable API

6. **Monitoring**
   - Prometheus metrics
   - Grafana dashboards
   - Health checks

### Stored Data
- Mined repositories with full metadata
- GitHub users
- Programming languages/technologies
- Execution logs
- Job history

---

## 5. Configuration

### Environment Variables (`.env`)
```env
POSTGRES_URL=postgresql://bot:botpass@localhost:5432/githubminer
REDIS_URL=redis://localhost:6379/0
GITHUB_TOKENS=token1,token2,token3
DOLIBARR_API=https://your-dolibarr.com/api
DOLIBARR_KEY=your_api_key
```

### Limits
- `MAX_RETRIES`: 3 retries per request
- `RETRY_BACKOFF_FACTOR`: 2 (exponential)
- `REQUEST_TIMEOUT`: 30 seconds
- `PER_PAGE`: 100 results
- `MAX_PAGES`: 10 default, 20 maximum

---

## 6. Building & Running the Project

### Prerequisites

| Requirement | Description | Version |
|-------------|-------------|---------|
| **Python** | Programming language | 3.10+ |
| **Docker** | Container platform | Latest |
| **Docker Compose** | Container orchestration | Latest |
| **PostgreSQL** | Database (local) | 15+ |
| **Redis** | Cache/Queue (local) | 7+ |

### Quick Start (Docker Compose)

The fastest way to get the entire system running:

```bash
# Make start script executable
chmod +x scripts/start.sh

# Run the startup script
./scripts/start.sh
```

**What `./scripts/start.sh` does:**
1. Builds all Docker containers (`docker-compose build`)
2. Starts all services in detached mode (`docker-compose up -d`)
3. Waits for services to be healthy
4. Displays access URLs and quick commands

**Services Started:**
| Service | URL | Description |
|---------|-----|-------------|
| API | http://localhost:8000 | FastAPI REST API |
| PostgreSQL | localhost:5432 | Database |
| Redis | localhost:6379 | Message queue |
| Prometheus | http://localhost:9090 | Metrics |
| Grafana | http://localhost:3000 | Dashboards (admin/admin) |

---

### Development Mode (Local)

For development without Docker, using local PostgreSQL and Redis:

```bash
# Make script executable
chmod +x scripts/run_dev.sh

# Run development script
./scripts/run_dev.sh
```

**What `./scripts/run_dev.sh` does:**
1. Checks for `.env` file
2. Creates and activates Python virtual environment (`venv`)
3. Installs dependencies from `requirements.txt`
4. Initializes database tables
5. Starts Redis server (if not running)
6. Starts RQ worker in background
7. Starts FastAPI API with hot reload

---

### Manual Execution Steps

#### Step 1: Clone and Setup

```bash
# Clone the repository
git clone <repo-url>
cd bot_github

# Create .env file
cp .env.example .env
# Edit .env with your credentials
```

#### Step 2: Configure Environment

Edit `.env` file:
```env
POSTGRES_URL=postgresql://bot:botpass@localhost:5432/githubminer
REDIS_URL=redis://localhost:6379/0
GITHUB_TOKENS=ghp_your_token_1,ghp_your_token_2
DOLIBARR_API=https://your-dolibarr.com/api
DOLIBARR_KEY=your_api_key
```

#### Step 3: Build Docker Images

```bash
# Build all images
docker-compose build

# Or build specific service
docker-compose build api
docker-compose build worker
```

#### Step 4: Start Services

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d api

# Start with logs visible
docker-compose up
```

#### Step 5: Verify Running Services

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f
docker-compose logs -f api
docker-compose logs -f worker
```

#### Step 6: Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop and remove images
docker-compose down --rmi all
```

---

### Database Initialization

```bash
# Initialize database tables
python scripts/init_db.py
```

This creates all tables:
- `jobs` - Mining job records
- `repositories` - Extracted repositories
- `users` - GitHub users
- `technologies` - Programming languages
- `execution_logs` - Job execution logs

---

### Running Workers Manually

```bash
# Start worker (Docker)
docker-compose exec worker rq worker github_jobs

# Start worker (local)
rq worker github_jobs --url redis://localhost:6379/0
```

---

### Common Commands Reference

| Command | Description |
|---------|-------------|
| `./scripts/start.sh` | Start all services with Docker |
| `./scripts/run_dev.sh` | Start in development mode (local) |
| `docker-compose ps` | Check service status |
| `docker-compose logs -f` | View live logs |
| `docker-compose restart` | Restart all services |
| `docker-compose down` | Stop all services |
| `python scripts/init_db.py` | Initialize database |
| `rq info github_jobs` | View queue status |

---

## 7. Testing the API

```bash
# Health check
curl "http://localhost:8000/health/ready"

# Start mining job
curl -X POST "http://localhost:8000/scraper/start?query=language:python&pages=5"

# Check job status
curl "http://localhost:8000/scraper/status/1"

# Stop job
curl -X POST "http://localhost:8000/scraper/stop/1"

# View metrics
curl "http://localhost:8000/metrics"
```

---

## 8. File Structure

| Service | Port | Description |
|----------|--------|--------------|
| API | 8000 | Documentation at `/docs` |
| Prometheus | 9090 | System metrics |
| Grafana | 3000 | Dashboards (admin/admin) |

---

## 9. Current Project Status

### Functional
- REST API operational
- Job system working
- GitHub repository mining operational
- Async workers active
- Monitoring configured
- Docker Compose deployable

---

## 10. Pending Work & Next Steps

### High Priority

| # | Task | Description | Files to Modify |
|---|------|-------------|-----------------|
| 1 | **Dolibarr Upload Endpoint** | Create API endpoint to upload JSON results to Dolibarr CRM | `app/api/routes/dolibarr.py` (new), `app/core/dolibarr_client.py` |
| 2 | **Schedule Job Automation** | Implement APScheduler to run mining jobs automatically | `scheduler/jobs.py`, `scheduler/scheduler.py` |
| 3 | **JSON Export Automation** | Auto-export mining results to `/output/` folder after job completion | `app/workers/tasks/search_repos.py`, `app/services/job_dispatcher.py` |

### Medium Priority

| # | Task | Description | Files to Modify |
|---|------|-------------|-----------------|
| 4 | **Grafana Dashboards** | Create meaningful Grafana dashboards for monitoring | `monitoring/` (add dashboards) |
| 5 | **Prometheus Config** | Add scrape configs for application metrics | `monitoring/prometheus.yml` |
| 6 | **Unit Tests** | Write unit tests for core functionality | `tests/test_*.py` (fill in content) |

### Low Priority / Backlog

| # | Task | Description | Files to Modify |
|---|------|-------------|-----------------|
| 7 | **Scheduled Queries** | Pre-defined query configurations for automatic mining | `config/search_queries.json` |
| 8 | **Retry Failed Jobs** | Endpoint to retry failed mining jobs | `app/api/routes/control.py` |
| 9 | **Job History Cleanup** | Cleanup old jobs and execution logs | `app/services/job_dispatcher.py` |
| 10 | **API Authentication** | Add authentication/authorization to API endpoints | `app/dependencies.py`, `app/api/routes/` |
| 11 | **Rate Limiting** | Implement API rate limiting for external requests | `app/api/middleware/` (new) |
| 12 | **Data Validation** | Add validation for imported JSON data | `app/api/schemas/` |

### Known Issues

| Issue | Status | Workaround |
|-------|--------|-----------|
| Dolibarr integration not fully tested | Pending | Manual sync via API |
| No automatic JSON export | Pending | Database queries |
| Grafana empty dashboards | Pending | Create from scratch |
| Test files empty | Pending | Write tests |

---

## 11. Customizing Mining Queries

### Files to Modify

#### 1. Query Configuration (`config/search_queries.json`)
```json
{
  "queries": [
    {
      "name": "Python repos with >20 stars",
      "query": "language:python stars:>20",
      "limit": 1,
      "fetch_contributors": true,
      "contributors_limit": 100,
      "fetch_user_repos": true
    }
  ]
}
```

**Fields:**
| Field | Description |
|-------|-------------|
| `name` | Human-readable name for the query |
| `query` | GitHub search syntax (e.g., `language:python stars:>100`) |
| `limit` | Maximum number of pages to fetch |
| `fetch_contributors` | Whether to fetch repository contributors |
| `contributors_limit` | Max contributors per repo |
| `fetch_user_repos` | Whether to fetch user's repositories |

#### 2. Start Mining via API

```bash
# Single query
curl -X POST "http://localhost:8000/scraper/start?query=language:python%20stars:>100&pages=5"

# Predefined queries from config
# (requires automation script integration)
```

#### 3. Key Files for Mining Logic

| File | Purpose |
|------|---------|
| `app/services/job_dispatcher.py` | Job creation and task dispatching |
| `app/workers/tasks/search_repos.py` | Repository search task |
| `app/workers/tasks/process_repo.py` | Repository processing (contributors) |
| `app/workers/tasks/process_user.py` | User profile processing |
| `app/core/github_client.py` | GitHub API client with token rotation |

---

## 12. Output JSON Format

### File Location
Extracted data is saved to: `output/<query_name>_<timestamp>.json`

### JSON Structure
```json
{
  "metadata": {
    "query": "language:python stars:>100",
    "query_name": "Python repos with >100 stars",
    "fetched_at": "2026-03-22T23:40:03.041871",
    "total_repos_fetched": 1,
    "total_users_found": 5
  },
  "repositories": {
    "54346799": {
      "github_id": 54346799,
      "name": "public-apis",
      "full_name": "public-apis/public-apis",
      "owner_login": "public-apis",
      "description": "A collective list of free APIs",
      "stars": 414613,
      "forks": 44898,
      "language": "Python",
      "url": "https://github.com/public-apis/public-apis",
      "created_at": "2016-03-20T23:49:42Z",
      "updated_at": "2026-03-23T05:39:31Z",
      "pushed_at": "2026-03-18T16:28:22Z",
      "open_issues": 1054,
      "watchers": 414613,
      "topics": ["api", "apis", "dataset", ...],
      "license": "MIT License",
      "homepage": "https://APILayer.com/..."
    }
  },
  "users": {
    "50463866": {
      "github_id": 50463866,
      "login": "matheusfelipeog",
      "name": "Matheus Felipe",
      "avatar_url": "https://avatars.githubusercontent.com/...",
      "html_url": "https://github.com/matheusfelipeog",
      ...
    }
  }
}
```

### Repository Fields
| Field | Description |
|-------|-------------|
| `github_id` | Unique GitHub ID |
| `name` | Repository name |
| `full_name` | Owner/repo format |
| `owner_login` | Owner username |
| `description` | Repo description |
| `stars` | Star count |
| `forks` | Fork count |
| `language` | Primary language |
| `url` | GitHub URL |
| `topics` | Repository topics |
| `license` | License name |

### User Fields
| Field | Description |
|-------|-------------|
| `github_id` | Unique GitHub ID |
| `login` | Username |
| `name` | Full name |
| `avatar_url` | Profile picture URL |
| `html_url` | Profile URL |

---

## 13. Developer & Contact

### Developer
**Jose Carlos Hernandez Herrera**

| Contact | Details |
|---------|---------|
| **Email** | josecarloshernandezherrera18@gmail.com |
| **Phone** | (+52)449-36-25-821 |
| **LinkedIn** | https://www.linkedin.com/in/josecarloshernandezherrera/ |

Feel free to reach out if you have any questions or would like to get in contact!

---

## 14. Additional Support

For more information or support:
- Check files in `/info/` for additional documentation
- Review logs in `./output/` for extracted data
- Job status via API: `/status/*`