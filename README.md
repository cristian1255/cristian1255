# Airflow - Pipeline de Datos Viales SCT (Cloud Edition)

**Ejecutar Apache Airflow en la nube sin Docker local.** Usa Railway, Render, Heroku o cualquier plataforma containerizada.

## 🎯 Características

✅ **Sin Docker local** - Todo corre en la nube  
✅ **Auto-scalable** - Crece con tu data  
✅ **Fully automated** - Deploy desde GitHub  
✅ **Production-ready** - Monitoreo y logs  
✅ **Database includida** - PostgreSQL + Redis en la nube  

## 🚀 Deploy rápido (5 minutos)

### Opción A: Railway.app (Recomendado)

```bash
# 1. Login a railway.app
railway login

# 2. Crear proyecto
railway init

# 3. Agregar DB
railway add --postgres
railway add --redis

# 4. Deploy
railway up
```

### Opción B: Heroku

```bash
# 1. Login
heroku login

# 2. Crear app
heroku create tu-nombre-app

# 3. Agregar add-ons
heroku addons:create heroku-postgresql
heroku addons:create heroku-redis

# 4. Deploy
git push heroku main
```

### Opción C: Render

1. Push a GitHub
2. Conecta repo en https://render.com
3. Deploy automático

## 📋 Requisitos previos

- Cuenta en Railway, Heroku o Render
- Git
- GitHub (para auto-deploy)

## 📁 Estructura

```
.
├── dags/                    # Tus DAGs
├── Dockerfile              # Imagen containerizada
├── Procfile                # Definición de servicios
├── railway.toml            # Config Railway
├── requirements.txt        # Dependencias
├── .env.example           # Variables (copiar a .env)
└── docs/                  # Guías
```

## 🔧 Configuración local (opcional)

Para probar antes de deployar:

```bash
# Copiar variables
cp .env.example .env

# Editar .env con tus valores
nano .env

# Instalar dependencias
pip install -r requirements.txt

# Levantar servicios
docker-compose up -d  # Opcional, solo si tienes Docker

# O correr Airflow standalone
airflow standalone
```

## 📚 Documentación

- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Guía paso-a-paso de deployment
- **[CLOUD_SETUP.md](docs/CLOUD_SETUP.md)** - Setup en cada plataforma cloud
- **[LOCAL_TESTING.md](docs/LOCAL_TESTING.md)** - Testing local (si lo necesitas)

## 🔐 Variables de entorno

Copiar `.env.example` a `.env` y editar:

```bash
# Base de datos
DATABASE_URL=postgresql://user:pass@host/db
REDIS_URL=redis://:pass@host:6379/0

# Airflow
_AIRFLOW_WWW_USER_PASSWORD=tu_contraseña
AIRFLOW__CORE__FERNET_KEY=tu_clave_fernet
```

**IMPORTANTE:** `.env` NO se sube a GitHub (está en `.gitignore`)

## 📊 Servicios que corren

1. **Webserver** - UI de Airflow en puerto 8080
2. **Scheduler** - Ejecuta DAGs según schedule
3. **Worker** - Ejecuta tareas en paralelo (Celery)
4. **Flower** - Monitor de Celery (opcional)

## 🎯 Tu pipeline

**DAG:** `sct_viales_estrella_automatizado`

**Schedule:** Diario a las 2:00 AM (México)

**Qué hace:**
1. Scrape PDFs desde SCT
2. Busca datos de Yucatán
3. Parsea y carga a PostgreSQL

## 📈 Monitoreo

Accede a Airflow UI:
```
https://tu-app.railway.app
Usuario: airflow
Contraseña: (la que configuraste)
```

Logs:
```bash
# Railway
railway logs

# Heroku  
heroku logs --tail

# Render
# Ver en dashboard → Logs
```

## 🆘 Troubleshooting

**"DB connection failed"**
```bash
# Verificar variable DATABASE_URL
railway variables

# Recrear DB
railway down --postgres
railway add --postgres
```

**"Scheduler no corre"**
- Ver logs: `railway logs`
- Verificar conexión DB
- Reiniciar: `railway restart`

**"DAG no aparece"**
- Verificar sintaxis: `python dags/dag_sct_estrella.py`
- Revisar logs del webserver
- Esperar 1-2 minutos a que Airflow reescanee

## 💡 Tips

- **Escala:** Aumenta workers si necesitas paralelismo
- **Alertas:** Configura email en `default_args`
- **Backups:** Exporta datos regularmente
- **Logs:** Mantén limpio para no llenar storage

## 🚀 Próximos pasos

1. Deploy a cloud (Railway, Heroku, Render)
2. Verificar que Airflow funciona
3. Trigger DAG manualmente
4. Ajustar schedule si es necesario
5. Configurar alertas por email

## 📞 Ayuda

Ver documentación en `docs/`:
- **DEPLOYMENT.md** - Paso a paso
- **CLOUD_SETUP.md** - Cada plataforma
- **LOCAL_TESTING.md** - Pruebas locales

---

**Made with ❤️ para SCT Viales + Yucatán**
