# GitHub Miner Bot - Documentación del Sistema

## 1. Arquitectura del Sistema

### Descripción General
El **GitHub Miner Bot** es un sistema distribuido de mining de datos de GitHub que recolecta información de repositorios, usuarios y contribuidores, con integración opcional a Dolibarr (CRM).

### Componentes Principales

```
┌─────────────────────────────────────────────────────────────────┐
│                        DOCKER COMPOSE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐    │
│  │   API    │   │  Worker │   │  Worker │   │Scheduler │    │
│  │ FastAPI  │   │   (x2)  │   │         │   │          │    │
│  └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘    │
│       │              │              │              │           │
│       └──────────────┴──────────────┴──────────────┘           │
│                             │                                  │
│       ┌─────────────────────┼─────────────────────┐         │
│       │                     │                     │          │
│  ┌────▼────┐          ┌─────▼─────┐         ┌─────▼────┐    │
│  │ Postgres │          │   Redis   │         │Prometheus│    │
│  │   (15)   │          │  (Queue)  │         │          │    │
│  └──────────┘          └───────────┘         └──────────┘    │
│                                                        │       │
│                                              ┌─────────▼────┐  │
│                                              │   Grafana    │  │
│                                              │  (Dashboard) │  │
│                                              └──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 2. Tecnologías por Componente

### API (FastAPI)
- **Framework**: FastAPI 0.135+
- **Servidor**: Uvicorn
- **Puerto**: 8000
- **Funciones**:
  - Endpoints REST para control del scraper
  - Health checks
  - Métricas Prometheus
  - Gestión de jobs

### Workers (RQ - Redis Queue)
- **Biblioteca**: RQ (Redis Queue) 2.7+
- **Replicas**: 2 workers en paralelo
- **Funciones**:
  - `search_repos_task`: Busca repos en GitHub
  - `process_repo_task`: Procesa repositorios (obtiene contribuidores)
  - `process_user_task`: Procesa usuarios (envía a Dolibarr)

### Base de Datos (PostgreSQL)
- **Versión**: PostgreSQL 15
- **Puerto**: 5432
- **Usuario**: bot / botpass
- **Base**: githubminer
- **Tablas**:
  - `jobs`: Jobs de mining
  - `repositories`: Repositorios recolectados
  - `users`: Usuarios de GitHub
  - `technologies`: Tecnologías detectadas
  - `job_execution_logs`: Logs de ejecución

### Cola de Mensajes (Redis)
- **Versión**: Redis 7 (alpine)
- **Puerto**: 6379
- **Uso**: Cola de tareas asíncronas (RQ)

### Monitoreo
- **Prometheus**: Métricas en puerto 9090
- **Grafana**: Dashboard en puerto 3000 (admin/admin)

### Integración
- **Dolibarr**: Sistema CRM externo (opcional)

## 3. Instrucciones de Ejecución

### Requisitos Previos
- Docker Desktop instalado
- Puerto 8000, 5432, 6379, 9090, 3000 disponibles

### Iniciar el Sistema

```bash
# Opción 1: Usar el script de inicio
./scripts/start.sh

# Opción 2: Manual con docker-compose
docker-compose build
docker-compose up -d
```

### Verificar que todo está funcionando

```bash
# Ver estado de contenedores
docker-compose ps

# Ver logs de la API
docker-compose logs -f api

# Ver logs de workers
docker-compose logs -f worker

# Probar endpoint de salud
curl http://localhost:8000/health/
```

### Iniciar un Job de Mining

```bash
# Buscar repositorios Python
curl -X POST "http://localhost:8000/scraper/start?query=language:python"

# Buscar repositorios con más de 1000 estrellas
curl -X POST "http://localhost:8000/scraper/start?query=stars:>1000&pages=5"

# Ver estado del job
curl http://localhost:8000/scraper/status/1

# Detener un job
curl -X POST "http://localhost:8000/scraper/stop/1"
```

### Detener el Sistema

```bash
docker-compose down
```

## 4. Endpoints de la API

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/health/` | GET | Health check |
| `/metrics/` | GET | Métricas Prometheus |
| `/scraper/start` | POST | Iniciar job de mining |
| `/scraper/stop/{job_id}` | POST | Detener job |
| `/scraper/status/{job_id}` | GET | Ver estado del job |
| `/status/jobs/` | GET | Listar todos los jobs |
| `/control/workers/` | GET | Estado de workers |

## 5. Variables de Entorno (.env)

```env
POSTGRES_URL=postgresql://bot:botpass@postgres:5432/githubminer
REDIS_URL=redis://redis:6379/0

# Tokens de GitHub (separados por coma)
GITHUB_TOKENS=github_pat_xxx,token2,token3

# Configuración de Dolibarr (opcional)
DOLIBARR_API=http://localhost/dolibarr/htdocs/api/index.php/atsapi
DOLIBARR_KEY=your_api_key
```

## 6. Estructura del Proyecto

```
bot_github/
├── app/                      # Código principal
│   ├── api/                  # Endpoints FastAPI
│   │   └── routes/          # Rutas: scraper, health, metrics, etc.
│   ├── core/                # Clientes externos
│   │   ├── github_client.py
│   │   └── dolibarr_client.py
│   ├── db/                  # Base de datos
│   │   ├── models/         # Modelos SQLAlchemy
│   │   └── session.py      # Sesión de DB
│   ├── services/           # Lógica de negocio
│   │   ├── job_dispatcher.py
│   │   └── token_rotator.py
│   ├── workers/            # Tareas RQ
│   │   └── tasks/          # search_repos, process_repo, process_user
│   ├── utils/              # Utilidades
│   │   ├── logger.py
│   │   └── metrics.py
│   ├── config.py
│   └── main.py
├── docker/                 # Dockerfiles
│   ├── fastapi.Dockerfile
│   └── worker.Dockerfile
├── scripts/               # Scripts
│   ├── start.sh
│   └── init_db.py
├── monitoring/            # Configuración Prometheus
├── docker-compose.yml
└── requirements.txt
```

## 7. Troubleshooting

### La API no responde en puerto 8000
```bash
# Ver logs
docker-compose logs api

# Reiniciar
docker-compose restart api
```

### Workers no procesan tareas
```bash
# Ver logs de workers
docker-compose logs worker

# Ver cola de Redis
docker exec githubminer_redis redis-cli LLEN github_jobs
```

### Error de conexión a PostgreSQL
```bash
# Verificar que Postgres está corriendo
docker-compose ps

# Ver logs
docker-compose logs postgres
```
