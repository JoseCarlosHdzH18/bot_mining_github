# Documentación de Tecnologías Utilizadas

## 1. FastAPI

### ¿Qué es?
FastAPI es un framework moderno y rápido (high-performance) para construir APIs con Python 3.7+ basado en type hints de Python.

### Importancia en el Proyecto
- **Backend principal**: Toda la API REST del sistema está construida con FastAPI
- **Documentación automática**: Genera documentación interactiva en `/docs`
- **Validación automática**: Valida tipos de datos automáticamente
- **Alto rendimiento**: Ideal para microservices

### Uso en el Proyecto
```python
from fastapi import FastAPI, APIRouter, Query

app = FastAPI(title="GitHub Miner Bot")

@app.get("/health/")
def health_check():
    return {"status": "ok"}
```

### Documentación
- Web: https://fastapi.tiangolo.com/
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 2. Uvicorn

### ¿Qué es?
Uvicorn es un servidor ASGI (Asynchronous Server Gateway Interface) de implementación mínima, escrito en Python.

### Importancia en el Proyecto
- **Servidor de producción**: Corre la aplicación FastAPI
- **Alto rendimiento**: Asíncrono y rápido
- **Hot reload**: Recarga automática en desarrollo

### Uso en el Proyecto
```bash
# En Dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Configuración Recomendada
```bash
# Produção
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Desarrollo
uvicorn app.main:app --reload
```

---

## 3. PostgreSQL

### ¿Qué es?
PostgreSQL es un sistema de gestión de bases de datos relacional objeto (ORDBMS) de código abierto, conocido por su robustez y características avanzadas.

### Importancia en el Proyecto
- **Almacenamiento principal**: Guarda todos los datos del sistema
- **Jobs**: Control de jobs de mining
- **Repositories**: Repositorios recolectados
- **Users**: Usuarios de GitHub
- **Logs**: Historial de ejecuciones

### Uso en el Proyecto
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

POSTGRES_URL = "postgresql://bot:botpass@postgres:5432/githubminer"
engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(bind=engine)
```

### Conexión Directa
```bash
docker exec -it githubminer_postgres psql -U bot -d githubminer

# Queries útiles
SELECT COUNT(*) FROM repositories;
SELECT COUNT(*) FROM users;
SELECT * FROM jobs ORDER BY created_at DESC;
```

---

## 4. Redis

### ¿Qué es?
Redis es un almacén de estructura de datos en memoria (in-memory data store), usado como base de datos, caché y message broker.

### Importancia en el Proyecto
- **Cola de tareas**: Gestiona las tareas asíncronas con RQ
- **Cache**: Almacena datos temporales
- **Pub/Sub**: Comunicación entre servicios

### Uso en el Proyecto
```python
from redis import Redis
from rq import Queue

redis_conn = Redis.from_url("redis://redis:6379/0")
job_queue = Queue("github_jobs", connection=redis_conn)

# Enqueue de tareas
job = job_queue.enqueue("module.function", arg1, arg2)
```

### Comandos Útiles
```bash
# Ver jobs en cola
docker exec githubminer_redis redis-cli LLEN github_jobs

# Ver workers registrados
docker exec githubminer_redis redis-cli SMEMBERS rq:workers:github_jobs

# Ver keys
docker exec githubminer_redis redis-cli KEYS "*"
```

---

## 5. RQ (Redis Queue)

### ¿Qué es?
RQ (Redis Queue) es una biblioteca Python simple para colas de trabajo y procesamiento en background.

### Importancia en el Proyecto
- **Workers asíncronos**: Procesa tareas en background
- **Distribución**: Permite múltiples workers
- **Retry automático**: Reintenta tareas fallidas
- **Persistencia**: Jobs guardados en Redis

### Uso en el Proyecto
```python
# En API (enqueue)
from app.workers.job_queue import job_queue

job = job_queue.enqueue(
    "app.workers.tasks.search_repos.search_repos_task",
    query, page, job_id
)

# En Worker (procesar)
def search_repos_task(query, page, job_id):
    # Lógica de procesamiento
    return result
```

### Configuración
```bash
# Iniciar worker
rq worker github_jobs --url redis://redis:6379/0

# Multiple workers
rq worker github_jobs --url redis://redis:6379/0 --concurrency 4
```

---

## 6. SQLAlchemy

### ¿Qué es?
SQLAlchemy es un toolkit y ORM (Object-Relational Mapper) para Python que proporciona flexibilidad al trabajar con bases de datos SQL.

### Importancia en el Proyecto
- **Modelos de datos**: Define las tablas del sistema
- **Abstracción**: Permite cambiar de DB sin cambiar código
- **Queries**: Construcción de consultas SQL

### Uso en el Proyecto
```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Repository(Base):
    __tablename__ = "repositories"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    stars = Column(Integer, default=0)
```

---

## 7. Prometheus

### ¿Qué es?
Prometheus es un sistema de monitoreo de código abierto con un modelo de datos multidimensional, lenguaje de query flexible y tiempo serie.

### Importancia en el Proyecto
- **Métricas**: Recolecta métricas del sistema
- **Alertas**: Configurar alertas
- **Dashboards**: Visualización de datos
- **Histórico**: Almacena datos de métricas

### Métricas del Proyecto
```python
from prometheus_client import Counter, Gauge

repositories_processed_total = Counter(
    'repositories_processed_total',
    'Total repositories processed',
    ['status']
)

github_requests_total = Counter(
    'github_requests_total', 
    'Total GitHub API requests',
    ['endpoint', 'status']
)
```

### Acceso
- **URL**: http://localhost:9090
- **Métricas**: http://localhost:9090/metrics

### Queries de Ejemplo
```promql
# Rate de requests
rate(github_requests_total[5m])

# Jobs fallidos
sum(github_requests_total{status="error"})

# Repos por status
repositories_processed_total by (status)
```

---

## 8. Grafana

### ¿Qué es?
Grafana es una plataforma open source de análisis y monitoreo que permite visualizar datos de múltiples fuentes.

### Importancia en el Proyecto
- **Dashboards**: Visualización gráfica de métricas
- **Alertas**: Notificaciones cuando hay problemas
- **Análisis**: Gr estadísticasáficos y
- **Integración**: Se conecta con Prometheus

### Uso en el Proyecto
- **URL**: http://localhost:3000
- **Usuario**: admin
- **Contraseña**: admin

### Configuración
1. Agregar Data Source: Prometheus (http://prometheus:9090)
2. Crear Dashboards con queries de Prometheus

### Dashboards Recomendados

#### Dashboard: GitHub Miner Overview
- Jobs activos
- Repositorios por día
- Usuarios procesados
- Errores

#### Dashboard: API Performance
- Requests por segundo
- Latencia
- Errores por endpoint

#### Dashboard: Workers
- Jobs en cola
- Tiempo de procesamiento
- Workers activos

---

## 9. Docker Compose

### ¿Qué es?
Docker Compose es una herramienta para definir y ejecutar aplicaciones multi-contenedor con Docker.

### Importancia en el Proyecto
- **Orquestación**: Gestiona todos los servicios
- **Redes**: Conecta los contenedores
- **Volúmenes**: Persistencia de datos
- **Variables**: Configuración por entorno

### Uso en el Proyecto
```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down

# Rebuild
docker-compose build
docker-compose up -d
```

### Servicios Configurados
- `api`: FastAPI
- `worker`: RQ Workers (x2)
- `postgres`: Base de datos
- `redis`: Cola de tareas
- `prometheus`: Métricas
- `grafana`: Visualización

---

## 10. Dolibarr (Integración)

### ¿Qué es?
Dolibarr es un ERP/CRM open source para gestión empresarial.

### Importancia en el Proyecto
- **CRM**: Registro de usuarios como terceros
- **Sincronización**: Envía datos de GitHub a Dolibarr
- **Gestión**: Permite gestionar usuarios encontrados

### Uso en el Proyecto
```python
# Envío de usuario a Dolibarr
from app.core.dolibarr_client import dolibarr_client

dolibarr_client.create_thirdparty(
    name="Usuario GitHub",
    email="user@github.com",
    data={"github_url": "..."}
)
```

### Configuración (.env)
```env
DOLIBARR_API=http://localhost/dolibarr/htdocs/api/index.php/atsapi
DOLIBARR_KEY=your_api_key
```

---

## 11. GitHub API

### ¿Qué es?
La API de GitHub permite interactuar programáticamente con GitHub (repos, users, organizations, etc.).

### Importancia en el Proyecto
- **Búsqueda**: Buscar repositorios con queries
- **Datos**: Obtener información de repos y usuarios
- **Contributors**: Listar contribuidores de repos

### Uso en el Proyecto
```python
from app.core.github_client import github_client

# Buscar repos
result = github_client.search_repositories(
    query="language:python",
    page=1
)

# Obtener contribuidores
contributors = github_client.get_repo_contributors(owner, repo)
```

### Rate Limits
- Sin token: 60 requests/hora
- Con token autenticado: 5000 requests/hora

### Configuración
```env
GITHUB_TOKENS=token1,token2,token3
```

---

## 12. Requests

### ¿Qué es?
Requests es una librería HTTP elegant para Python, simplifica HTTP requests.

### Importancia en el Proyecto
- **HTTP Client**: Comunicarse con APIs externas
- **GitHub API**: Fetch de datos
- **Dolibarr API**: Envío de datos

### Uso
```python
import requests

response = requests.get(
    "https://api.github.com/search/repositories",
    params={"q": "language:python"},
    headers={"Authorization": f"token {token}"}
)
```

---

## Resumen de Tecnologías

| Tecnología | Función | Puerto |
|------------|---------|--------|
| FastAPI | API REST | 8000 |
| PostgreSQL | Base de datos | 5432 |
| Redis | Cola de tareas | 6379 |
| RQ | Workers | - |
| Prometheus | Métricas | 9090 |
| Grafana | Dashboards | 3000 |
| Dolibarr | CRM (ext) | - |
| GitHub API | Datos (ext) | - |
