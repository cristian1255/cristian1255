# 🚀 DEPLOYMENT GUIDE - Llevar Airflow a la nube

Guía paso-a-paso para deployar tu Airflow en Railway, Heroku, Render o cualquier platform cloud.

## Requisitos

- GitHub account
- Código pusheado en GitHub
- Cuenta en servicio cloud (Railway, Heroku, Render)
- Variables de entorno configuradas

## Opción A: Railway.app (RECOMENDADO)

Railway es la opción más simple: Lee el archivo `CLOUD_SETUP.md` sección Railway.

Resumen:
1. Conectar GitHub a Railway
2. Railway auto-detecta Dockerfile
3. Agregar PostgreSQL + Redis
4. Deploy automático

## Opción B: Heroku

### Pasos

1. **Instalar Heroku CLI**
   ```bash
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Login**
   ```bash
   heroku login
   ```

3. **Crear app**
   ```bash
   heroku create tu-nombre-app
   ```

4. **Agregar base de datos**
   ```bash
   # PostgreSQL (addon gratuito)
   heroku addons:create heroku-postgresql:hobby-dev
   
   # Redis (para Celery)
   heroku addons:create heroku-redis:premium-0
   ```

5. **Configurar variables**
   ```bash
   heroku config:set _AIRFLOW_WWW_USER_PASSWORD=tu_contraseña
   heroku config:set AIRFLOW__CORE__FERNET_KEY=tu_clave
   # Las URLs de DB y Redis se auto-configuran
   ```

6. **Deploy**
   ```bash
   git push heroku main
   ```

7. **Inicializar DB**
   ```bash
   heroku run airflow db init
   heroku run airflow users create \
     --username admin \
     --password tu_contraseña \
     --firstname Admin \
     --lastname User \
     --role Admin \
     --email tu@email.com
   ```

8. **Ver app**
   ```bash
   heroku open
   # O manualment: https://tu-nombre-app.herokuapp.com
   ```

## Opción C: Render

### Pasos

1. **Ir a render.com**
2. **Conectar GitHub account**
3. **Crear servicio Web**
   - Repo: tu-repo
   - Build command: `echo "Build completado"`
   - Start command: `airflow webserver --port $PORT`
4. **Agregar variables**
   - DATABASE_URL (crear PostgreSQL)
   - REDIS_URL (crear Redis)
5. **Deploy automático**

## Opción D: GCP / AWS / Azure

Si usas servicios propios en la nube:

1. **Crear cluster Kubernetes o VM**
2. **Instalar Docker + Docker Compose**
3. **Crear PostgreSQL y Redis**
4. **Usar Dockerfile proporcionado**
   ```bash
   docker build -t airflow-cloud .
   docker run -p 8080:8080 airflow-cloud
   ```

---

## Pasos comunes a todos

### 1. Preparar GitHub

```bash
# Asegurarse de que todo está commiteado
git status

# Si hay cambios sin commitear:
git add .
git commit -m "prep: listo para cloud"
git push origin main
```

### 2. Inicializar base de datos

Después del primer deploy, ejecutar:

```bash
# Railway
railway run airflow db init

# Heroku
heroku run airflow db init

# Render
# Ve a logs y ejecuta el comando manualmente
```

### 3. Crear usuario admin

```bash
# Railway
railway run airflow users create \
  --username admin \
  --password tu_contraseña \
  --firstname Admin \
  --lastname User \
  --role Admin

# Heroku
heroku run airflow users create \
  --username admin \
  --password tu_contraseña \
  --firstname Admin \
  --lastname User \
  --role Admin
```

### 4. Acceder a Airflow UI

```
URL: https://tu-app.platform.com
Usuario: admin
Contraseña: (la que configuraste)
```

### 5. Crear conexión PostgreSQL

En Airflow UI:
1. Admin → Connections
2. Crear nueva conexión:
   - Conn ID: `postgres_viales`
   - Conn Type: PostgreSQL
   - Host: tu-db-host
   - Database: airflow
   - User: postgres
   - Password: tu_contraseña
   - Port: 5432

### 6. Trigger DAG manualmente

1. Abre Airflow UI
2. Busca `sct_viales_estrella_automatizado`
3. Click play (Trigger DAG)
4. Espera a que termine
5. Verifica logs

---

## Solucionar problemas

### "Dockerfile not found"

Asegúrate de que el archivo está en la raíz del repo.

```bash
ls -la Dockerfile
```

### "Can't connect to database"

Verificar:
1. DATABASE_URL está configurada
2. DB existe
3. Credenciales correctas

```bash
# Test connection
python -c "import psycopg2; psycopg2.connect('DATABASE_URL')"
```

### "Scheduler no está corriendo"

Verificar que el proceso está activo:

```bash
# Railway / Heroku
logs

# Esperar 2-3 minutos
# Reiniciar si es necesario
railway restart
# o
heroku restart
```

### "DAG no aparece"

1. Verificar sintaxis:
   ```bash
   python dags/dag_sct_estrella.py
   ```

2. Esperar 1-2 minutos (Airflow reescanea)

3. Revisar logs del scheduler

### "Out of memory"

Aumentar recursos:
- Railway: más memory
- Heroku: upgrade dyno
- Render: aumentar RAM

---

## Verificar que funcionó

Checklist:

- [ ] Airflow UI accesible
- [ ] DAG aparece en lista
- [ ] Puedo crear conexión PostgreSQL
- [ ] Trigger manual funciona
- [ ] Logs muestran ejecución

Si todo esto está ✅, tu pipeline está en la nube!

---

## Mantener actualizado

Cada cambio:

```bash
git add .
git commit -m "feat: cambio"
git push origin main
```

Plataforma auto-redeploya.

---

**¿Preguntas?** Ver `CLOUD_SETUP.md` para detalles específicos de cada plataforma.
