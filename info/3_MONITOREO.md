# Guía de Monitoreo y Observabilidad

## 1. Endpoints de la API

### Health Check
```bash
curl http://localhost:8000/health/
```
Respuesta esperada: `{"status":"ok"}`

### Estado de Jobs
```bash
# Ver un job específico
curl http://localhost:8000/scraper/status/1

# Listar todos los jobs
curl http://localhost:8000/status/jobs/
```

### Estado de Workers
```bash
curl http://localhost:8000/control/workers/
```

## 2. Métricas Prometheus

### Acceder a Métricas
```bash
# 直接 en navegador
http://localhost:9090

# O mediante curl
curl http://localhost:9090/metrics
```

### Métricas Personalizadas Disponibles

| Métrica | Tipo | Descripción |
|---------|------|-------------|
| `repositories_processed_total` | Counter | Total de repositorios procesados |
| `users_processed_total` | Counter | Total de usuarios procesados |
| `github_requests_total` | Counter | Total de requests a GitHub API |
| `queue_size` | Gauge | Tamaño de la cola de jobs |

### Querys Útiles en Prometheus

```promql
# Ver rate de requests a GitHub
rate(github_requests_total[5m])

# Repositorios procesados por status
repositories_processed_total by (status)

# Jobs en cola
queue_size
```

## 3. Grafana Dashboards

### Acceder
- **URL**: http://localhost:3000
- **Usuario**: admin
- **Contraseña**: admin

### Dashboards Recomendados

1. **API Overview**
   - Requests por segundo
   - Latencia de respuestas
   - Errores

2. **Workers Overview**
   - Jobs procesados
   - Jobs en cola
   - Tiempo de ejecución

3. **GitHub API Usage**
   - Rate limit remaining
   - Requests por endpoint
   - Errores por tipo

## 4. Logs del Sistema

### API Logs
```bash
# Ver logs en tiempo real
docker-compose logs -f api

# Últimas 50 líneas
docker logs githubminer_api --tail 50
```

### Worker Logs
```bash
# Worker 1
docker-compose logs -f worker

# Worker específico
docker logs bot_github-worker-1

# Ambos workers
docker logs bot_github-worker-1
docker logs bot_github-worker-2
```

### PostgreSQL Logs
```bash
docker-compose logs postgres
```

### Redis Logs
```bash
docker-compose logs redis
```

## 5. Estado de Contenedores

### Ver todos los contenedores
```bash
docker-compose ps
```

### Estado detallado
```bash
docker ps -a
```

### Ver recursos utilizados
```bash
docker stats
```

## 6. Cola de Redis

### Ver jobs en cola
```bash
# Número de jobs en cola
docker exec githubminer_redis redis-cli LLEN github_jobs

# Ver jobs fallidos
docker exec githubminer_redis redis-cli LRANGE rq:failed 0 -1

# Ver workers registrados
docker exec githubminer_redis redis-cli SMEMBERS rq:workers:github_jobs
```

## 7. Base de Datos PostgreSQL

### Conectar a la base de datos
```bash
docker exec -it githubminer_postgres psql -U bot -d githubminer
```

### Queries útiles

```sql
-- Ver todos los jobs
SELECT * FROM jobs ORDER BY created_at DESC LIMIT 10;

-- Jobs en ejecución
SELECT * FROM jobs WHERE status = 'running';

-- Ver repositorios encontrados
SELECT COUNT(*) FROM repositories;

-- Ver usuarios encontrados
SELECT COUNT(*) FROM users;

-- Ver tecnologías
SELECT name, repositories_count FROM technologies ORDER BY repositories_count DESC LIMIT 10;

-- Ver logs de ejecución
SELECT * FROM job_execution_logs ORDER BY created_at DESC LIMIT 20;
```

### Schema de tablas

```sql
-- Jobs
\d jobs

-- Repositories  
\d repositories

-- Users
\d users

-- Technologies
\d technologies
```

## 8. Monitoreo de API de GitHub

### Rate Limit Remaining
```bash
# Hacer una request y revisar headers
curl -I https://api.github.com/rate_limit
```

### Ver consumo en logs
```bash
# Buscar requests a GitHub en logs
docker-compose logs api | grep "GitHub"

# Ver en worker logs
docker-compose logs worker | grep "Found"
```

## 9. Alertas y Notificaciones (Grafana)

### Configurar alertas en Grafana

1. Ir a http://localhost:3000
2. Alerting → Alert rules
3. Create alert rule

### Ejemplos de alertas recomendadas

- **Workers offline**: Si no hay workers procesando por más de 5 minutos
- **Cola llena**: Si hay más de 1000 jobs en cola
- **Rate limit**: Si rate limit de GitHub está bajo
- **Errores en jobs**: Si hay jobs fallidos

## 10. Scripts de Monitoreo

### Ver estado completo del sistema
```bash
#!/bin/bash
echo "=== Estado del Sistema ==="
echo ""
echo "--- Contenedores ---"
docker-compose ps
echo ""
echo "--- Jobs en cola ---"
docker exec githubminer_redis redis-cli LLEN github_jobs
echo ""
echo "--- Último job ---"
curl -s http://localhost:8000/status/jobs/ | jq '.[0]'
echo ""
echo "--- Workers ---"
curl -s http://localhost:8000/control/workers/
```

### Guardar como script
```bash
chmod +x scripts/monitor.sh
./scripts/monitor.sh
```

## 11. Logs Estructurados

Los logs siguen el formato:
```
2026-03-03 07:12:34,416 [INFO] github_jobs: Job OK (e8582d82-...)
2026-03-03 07:12:35,598 [INFO] Completed processing repo ...
2026-03-03 07:12:35,956 [ERROR] Error in search task for job ...
```

### Niveles de log
- `[INFO]` - Información general
- `[WARNING]` - Advertencias
- `[ERROR]` - Errores

## 12. URLs de Acceso Rápido

| Servicio | URL |
|----------|-----|
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |
| Health | http://localhost:8000/health/ |
