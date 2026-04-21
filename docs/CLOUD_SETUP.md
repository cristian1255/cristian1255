# ☁️ CLOUD SETUP - Configure según tu plataforma

Elije la plataforma que prefieres y sigue los pasos.

## Railway.app (Más fácil) ⭐

### Crear proyecto

1. Ir a https://railway.app
2. "New Project" → "Deploy from GitHub repo"
3. Conectar GitHub y seleccionar tu repo
4. Railway auto-detecta Dockerfile

### Agregar servicios

```bash
# Desde CLI
railway login
railway link  # Conecta al proyecto

# Agregar PostgreSQL
railway add --postgres

# Agregar Redis
railway add --redis
```

**O desde UI:**
1. Dashboard → "Add Service"
2. Agregar PostgreSQL
3. Agregar Redis
4. Railway auto-configura las URLs

### Variables de entorno

```bash
railway variables set \
  _AIRFLOW_WWW_USER_PASSWORD=tu_contraseña \
  AIRFLOW__CORE__FERNET_KEY=tu_clave
```

O en UI: Project → Variables

### Servicios (Procfile)

Railway lee `Procfile` automáticamente:
- `web`: Webserver (puerto 8080)
- `scheduler`: Scheduler
- `worker`: Celery worker
- `flower`: Monitor

### Ver logs

```bash
railway logs -s webserver
railway logs -s scheduler
railway logs -s worker
```

### Acceder

```bash
railway open  # Abre URL en navegador
```

URL será: `https://tu-proyecto-production.up.railway.app`

---

## Heroku

### Preparación

1. Instalar Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli

### Crear app

```bash
heroku login
heroku create tu-nombre-app
```

### Agregar add-ons

```bash
# PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Redis
heroku addons:create heroku-redis:premium-0
```

URL auto-se configura como `DATABASE_URL` y `REDIS_URL`.

### Variables

```bash
heroku config:set _AIRFLOW_WWW_USER_PASSWORD=tu_contraseña
heroku config:set AIRFLOW__CORE__FERNET_KEY=tu_clave
```

Ver todas:
```bash
heroku config
```

### Deploy

```bash
git push heroku main
```

### Inicializar

```bash
heroku run airflow db init
```

### Logs

```bash
heroku logs --tail
```

### Acceder

```bash
heroku open
```

URL será: `https://tu-nombre-app.herokuapp.com`

---

## Render

### Conectar GitHub

1. Ir a https://render.com
2. "New +" → "Web Service"
3. Conectar repo GitHub
4. Render detecta Dockerfile

### Configuración

**Build Command:**
```
echo "Usando Dockerfile"
```

**Start Command:**
```
airflow db init && airflow webserver --port $PORT
```

### Agregar base de datos

1. "New +" → "PostgreSQL"
   - Name: `airflow-db`
   - Guardar credenciales

2. "New +" → "Redis"
   - Name: `airflow-redis`

### Variables de entorno

En Web Service → Environment:

```
DATABASE_URL=postgresql://usuario:pass@host:5432/airflow
REDIS_URL=redis://:password@host:6379/0
_AIRFLOW_WWW_USER_PASSWORD=tu_contraseña
AIRFLOW__CORE__FERNET_KEY=tu_clave
```

### Deploy

Auto-deploy desde GitHub cuando hagas push.

### Logs

Dashboard → Logs

### Acceder

URL en dashboard. Formato: `https://tu-app.onrender.com`

---

## AWS (ECS / Lambda)

### Opción A: ECS + CloudFormation

```bash
# Template CloudFormation
aws cloudformation create-stack \
  --stack-name airflow-stack \
  --template-body file://cloudformation.yaml
```

### Opción B: ECS Fargate

1. Crear cluster ECS
2. Task definition con Dockerfile
3. Service para cada proceso:
   - webserver
   - scheduler
   - worker

### RDS + ElastiCache

- RDS PostgreSQL
- ElastiCache Redis
- Security groups abiertos entre servicios

### Variables

AWS Systems Manager Parameter Store:
```bash
aws ssm put-parameter \
  --name /airflow/fernet_key \
  --value "tu_clave"
```

---

## GCP (Cloud Run / App Engine)

### Cloud Run

```bash
gcloud run deploy airflow-webserver \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Cloud SQL + Memorystore

1. Cloud SQL: PostgreSQL
2. Memorystore: Redis
3. Conectar desde Cloud Run

### Variables

Cloud Build:
```bash
gcloud run deploy airflow \
  --set-env-vars="DATABASE_URL=..."
```

---

## Azure (Container Instances / App Service)

### Container Instances

```bash
az container create \
  --resource-group mygroup \
  --name airflow-web \
  --image tu-repo/airflow-cloud \
  --ports 8080 \
  --environment-variables \
    DATABASE_URL="..." \
    REDIS_URL="..."
```

### Azure Database + Redis

- Azure Database for PostgreSQL
- Azure Cache for Redis

---

## Comparativa rápida

| Plataforma | Facilidad | Costo | Escalabilidad |
|-----------|-----------|-------|---------------|
| **Railway** | ⭐⭐⭐⭐⭐ | $$ | ⭐⭐⭐⭐ |
| **Render** | ⭐⭐⭐⭐ | $$ | ⭐⭐⭐ |
| **Heroku** | ⭐⭐⭐⭐ | $$$  | ⭐⭐⭐ |
| **AWS** | ⭐⭐ | $/$$$ | ⭐⭐⭐⭐⭐ |
| **GCP** | ⭐⭐ | $/$$$ | ⭐⭐⭐⭐⭐ |
| **Azure** | ⭐⭐ | $/$$$ | ⭐⭐⭐⭐⭐ |

**Recomendación:** Usa Railway para empezar (más simple), migra a AWS/GCP si necesitas escala.

---

## Troubleshooting común

### "Health check failing"

Dockerfile tiene HEALTHCHECK. Asegúrate que el puerto está correcto:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1
```

### "Database connection timeout"

Verificar:
1. DATABASE_URL tiene credenciales correctas
2. DB existe
3. Firewall abierto (si requiere)

### "Scheduler no inicia"

```bash
# Ver logs específicamente del scheduler
railway logs -s scheduler

# O Heroku
heroku logs --tail --dyno scheduler
```

### "Out of memory"

Aumentar recursos en plataforma:
- Railway: Settings → Memory
- Heroku: dyno type
- Render: Instance type

---

**¿Dudas de tu plataforma?** Ve a sección específica arriba.

Después de setup, leer `DEPLOYMENT.md` para pasos finales.
