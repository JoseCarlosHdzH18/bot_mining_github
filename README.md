# GitHub Miner Bot

> A high-performance, asynchronous GitHub data mining system built with FastAPI, PostgreSQL, and Redis. Automates repository discovery, contributor analysis, and CRM integration at scale.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Quick Start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [Docker Compose (Recommended)](#docker-compose-recommended)
  - [Development Mode (Local)](#development-mode-local)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [Search Queries](#search-queries)
- [API Reference](#api-reference)
- [Usage Examples](#usage-examples)
- [Project Structure](#project-structure)
- [Monitoring](#monitoring)
- [Output Format](#output-format)
- [Roadmap](#roadmap)
- [Contact](#contact)

---

## Overview

GitHub Miner Bot is a production-ready data mining platform designed to extract, process, and synchronize GitHub repository data at scale. It leverages the GitHub Search API to discover repositories based on custom queries, enriches the data with contributor profiles, and syncs results to Dolibarr CRM.

Key capabilities include automatic pagination, token rotation for rate limit handling, asynchronous job processing via Redis Queue, and full observability with Prometheus and Grafana.

---

## Features

| Feature | Description |
|---------|-------------|
| **Repository Search** | Custom queries via GitHub Search API with automatic pagination (up to 20 pages) |
| **Contributor Mining** | Extract contributor profiles and their repositories |
| **Async Job Processing** | Redis Queue (RQ) workers handle jobs asynchronously with multi-replica support |
| **Job Management** | Create, start, stop jobs with real-time progress tracking |
| **Token Rotation** | Automatic GitHub token rotation to handle API rate limits |
| **Retry Logic** | Exponential backoff with configurable retry attempts |
| **Dolibarr Integration** | Sync mined data directly to Dolibarr CRM |
| **Observability** | Prometheus metrics and Grafana dashboards included |
| **Docker Ready** | Full containerization with Docker Compose |
| **JSON Export** | Automatic export of mining results to structured JSON files |

---

## Technology Stack

### Core Technologies

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
- **XAMPP**: Local development server support

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Miner Bot                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────┐     ┌──────────┐     ┌─────────────┐
│   API       │────▶│  Redis   │────▶│  Workers   │
│  FastAPI    │     │  (RQ)    │     │  (python)   │
│   :8000     │     │          │     │             │
└─────────────┘     └──────────┘     └─────────────┘
       │                                   │
       ▼                                   ▼
┌─────────────┐                     ┌─────────────┐
│ PostgreSQL  │◀───────────────────│ GitHub API  │
│   :5432     │                     │             │
└─────────────┘                     └─────────────┘
       │
       ▼
┌─────────────┐
│  Dolibarr   │
│   (CRM)     │
└─────────────┘

    ┌──────────┐    ┌──────────┐
    │Prometheus│    │ Grafana  │
    │  :9090   │───▶│  :3000   │
    └──────────┘    └──────────┘
```

---

## Quick Start

### Prerequisites

| Requirement | Description | Version |
|-------------|-------------|---------|
| **Python** | Programming language | 3.10+ |
| **Docker** | Container platform | Latest |
| **Docker Compose** | Container orchestration | Latest |
| **PostgreSQL** | Database (local, optional) | 15+ |
| **Redis** | Cache/Queue (local, optional) | 7+ |
| **GitHub Token** | API access token(s) | - |

### Docker Compose (Recommended)

The fastest way to get the entire system running:

```bash
# Clone the repository
git clone <repo-url>
cd bot_github

# Make start script executable
chmod +x scripts/start.sh

# Run the startup script
./scripts/start.sh
```

The startup script will:
1. Build all Docker containers (`docker-compose build`)
2. Start all services in detached mode (`docker-compose up -d`)
3. Wait for services to be healthy
4. Display access URLs and quick commands

### Development Mode (Local)

For development without Docker, using local PostgreSQL and Redis:

```bash
# Make script executable
chmod +x scripts/run_dev.sh

# Run development script
./scripts/run_dev.sh
```

The development script will:
1. Check for `.env` file
2. Create and activate Python virtual environment (`venv`)
3. Install dependencies from `requirements.txt`
4. Initialize database tables
5. Start Redis server (if not running)
6. Start RQ worker in background
7. Start FastAPI API with hot reload

### Manual Setup

#### Step 1: Configure Environment

Create and edit `.env` file:

```bash
cp .env.example .env
```

```env
POSTGRES_URL=postgresql://bot:botpass@localhost:5432/githubminer
REDIS_URL=redis://localhost:6379/0
GITHUB_TOKENS=ghp_your_token_1,ghp_your_token_2
DOLIBARR_API=https://your-dolibarr.com/api
DOLIBARR_KEY=your_api_key
```

#### Step 2: Initialize Database

```bash
python scripts/init_db.py
```

#### Step 3: Start Services

```bash
# Docker
docker-compose up -d

# Local - start worker
rq worker github_jobs --url redis://localhost:6379/0

# Local - start API (in another terminal)
uvicorn app.main:app --reload --port 8000
```

---

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `POSTGRES_URL` | PostgreSQL connection string | Yes |
| `REDIS_URL` | Redis connection string | Yes |
| `GITHUB_TOKENS` | Comma-separated GitHub tokens | Yes |
| `DOLIBARR_API` | Dolibarr API URL | No |
| `DOLIBARR_KEY` | Dolibarr API Key | No |

### System Limits

| Setting | Default | Description |
|---------|---------|-------------|
| `MAX_RETRIES` | 3 | Retries per request |
| `RETRY_BACKOFF_FACTOR` | 2 | Exponential backoff multiplier |
| `REQUEST_TIMEOUT` | 30s | Request timeout |
| `PER_PAGE` | 100 | Results per page |
| `MAX_PAGES` | 10 (max 20) | Maximum pagination pages |

### Search Queries

Configure mining queries in `config/search_queries.json`:

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

| Field | Description |
|-------|-------------|
| `name` | Human-readable name for the query |
| `query` | GitHub search syntax (e.g., `language:python stars:>100`) |
| `limit` | Maximum number of pages to fetch |
| `fetch_contributors` | Whether to fetch repository contributors |
| `contributors_limit` | Max contributors per repo |
| `fetch_user_repos` | Whether to fetch user's repositories |

---

## API Reference

Base URL: `http://localhost:8000`

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health/*` | GET | Health check endpoints |
| `/metrics/*` | GET | Prometheus metrics |
| `/scraper/start` | POST | Start a mining job |
| `/scraper/stop/{job_id}` | POST | Stop a running job |
| `/scraper/status/{job_id}` | GET | Get job status |
| `/status/*` | GET | Job status endpoints |
| `/control/*` | POST | System control endpoints |
| `/docs` | GET | Interactive API documentation (Swagger UI) |

### Job Statuses

| Status | Description |
|--------|-------------|
| `pending` | Job created, waiting to start |
| `running` | Job currently executing |
| `completed` | Job finished successfully |
| `failed` | Job encountered an error |
| `cancelled` | Job was manually stopped |

---

## Usage Examples

### Health Check

```bash
curl "http://localhost:8000/health/ready"
```

### Start a Mining Job

```bash
# Using query parameters
curl -X POST "http://localhost:8000/scraper/start?query=language:python&pages=5"

# With stars filter
curl -X POST "http://localhost:8000/scraper/start?query=language:python%20stars:>100&pages=5"
```

### Check Job Status

```bash
curl "http://localhost:8000/scraper/status/1"
```

### Stop a Job

```bash
curl -X POST "http://localhost:8000/scraper/stop/1"
```

### View Metrics

```bash
curl "http://localhost:8000/metrics"
```

---

## Project Structure

```
bot_github/
├── app/
│   ├── api/
│   │   └── routes/          # API route handlers
│   ├── core/
│   │   └── github_client.py # GitHub API client with token rotation
│   ├── db/
│   │   └── models/          # SQLAlchemy database models
│   ├── services/
│   │   └── job_dispatcher.py # Job creation and task dispatching
│   ├── workers/
│   │   └── tasks/           # Async worker tasks
│   │       ├── search_repos.py
│   │       ├── process_repo.py
│   │       └── process_user.py
│   └── main.py              # FastAPI application entry point
├── config/
│   └── search_queries.json  # Search query configurations
├── scheduler/               # APScheduler job scheduling
│   ├── jobs.py
│   └── scheduler.py
├── scripts/                 # Utility scripts
│   ├── start.sh
│   ├── run_dev.sh
│   └── init_db.py
├── monitoring/              # Prometheus & Grafana configs
│   └── prometheus.yml
├── output/                  # Exported JSON results
├── tests/                   # Unit tests
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile.api           # API service Dockerfile
├── Dockerfile.worker        # Worker service Dockerfile
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
├── DOCUMENTATION.md         # Technical documentation
└── README.md                # This file
```

### Database Models

| Model | Description |
|-------|-------------|
| **Job** | Scraping jobs (query, status, progress) |
| **Repository** | Extracted repositories |
| **User** | GitHub users |
| **Tech** | Detected technologies |
| **ExecutionLog** | Execution logs |

---

## Monitoring

### Services

| Service | URL | Description |
|---------|-----|-------------|
| **API** | http://localhost:8000 | FastAPI REST API |
| **PostgreSQL** | localhost:5432 | Database |
| **Redis** | localhost:6379 | Message queue |
| **Prometheus** | http://localhost:9090 | Metrics collection |
| **Grafana** | http://localhost:3000 | Dashboards (admin/admin) |

### Access Grafana

1. Navigate to http://localhost:3000
2. Login with `admin` / `admin`
3. Configure Prometheus data source: `http://prometheus:9090`
4. Create dashboards to visualize mining metrics

---

## Output Format

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
      "topics": ["api", "apis", "dataset"],
      "license": "MIT License",
      "homepage": "https://APILayer.com/"
    }
  },
  "users": {
    "50463866": {
      "github_id": 50463866,
      "login": "matheusfelipeog",
      "name": "Matheus Felipe",
      "avatar_url": "https://avatars.githubusercontent.com/...",
      "html_url": "https://github.com/matheusfelipeog"
    }
  }
}
```

---

## Roadmap

### High Priority

| # | Task | Status |
|---|------|--------|
| 1 | Dolibarr Upload Endpoint | Pending |
| 2 | Schedule Job Automation | Pending |
| 3 | JSON Export Automation | Pending |

### Medium Priority

| # | Task | Status |
|---|------|--------|
| 4 | Grafana Dashboards | Pending |
| 5 | Prometheus Config | Pending |
| 6 | Unit Tests | Pending |

### Backlog

- Scheduled Queries from config
- Retry Failed Jobs endpoint
- Job History Cleanup
- API Authentication
- Rate Limiting
- Data Validation

---

## Common Commands

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

## Contact

**Developer**: Jose Carlos Hernandez Herrera

| Contact | Details |
|---------|---------|
| **Email** | josecarloshernandezherrera18@gmail.com |
| **Phone** | (+52) 449-36-25-821 |
| **LinkedIn** | [josecarloshernandezherrera](https://www.linkedin.com/in/josecarloshernandezherrera/) |


<div align="center">
  <p>Feel free to reach out if you have any questions or would like to get in contact!</p>
</div>
