# 🧪 LOCAL TESTING - Prueba antes de deployar (Opcional)

Si quieres probar localmente antes de subir a la nube.

## Requisitos

- Python 3.10+
- PostgreSQL (local o Docker)
- Redis (local o Docker)
- Docker (opcional pero recomendado)

## Opción A: Con Docker (Recomendado)

### Preparar

```bash
# 1. Copiar variables
cp .env.example .env

# 2. Editar .env
nano .env  # Cambiar valores si es necesario

# 3. Levantar servicios
docker-compose up -d

# 4. Esperar ~30 segundos
sleep 30

# 5. Ver status
docker-compose ps
```

### Acceder

- Airflow: http://localhost:8080
- User: airflow
- Pass: airflow

### Usar

```bash
# Ver logs
docker-compose logs -f airflow-webserver

# Parar
docker-compose down

# Limpiar todo
docker-compose down -v
```

---

## Opción B: Sin Docker (Standalone)

### Instalar dependencias

```bash
pip install -r requirements.txt
pip install airflow[postgres,celery,redis]  # Extras
```

### Inicializar

```bash
# Crear home
export AIRFLOW_HOME=./airflow

# Inicializar DB
airflow db init

# Crear usuario
airflow users create \
  --username admin \
  --password admin \
  --firstname Admin \
  --lastname User \
  --role Admin
```

### Levantar

**Terminal 1 - Webserver:**
```bash
airflow webserver --port 8080
```

**Terminal 2 - Scheduler:**
```bash
airflow scheduler
```

**Terminal 3 - Worker (opcional):**
```bash
airflow celery worker
```

### Acceder

http://localhost:8080

---

## Testing del DAG

### 1. Validar sintaxis

```bash
python dags/dag_sct_estrella.py
```

Si no hay error → sintaxis OK ✅

### 2. Verificar imports

```bash
python -c "from dags.dag_sct_estrella import dag"
python -c "from dags.pipelines.viales_scraper import obtener_urls_sct"
```

### 3. Ver DAG en UI

1. Abre http://localhost:8080
2. Busca `sct_viales_estrella_automatizado`
3. Verifica que aparece sin errores

### 4. Trigger manual

1. En UI, click en el DAG
2. Botón "Trigger DAG"
3. Espera a que termine
4. Verifica logs

### 5. Inspeccionar BD

```bash
psql -U airflow -d airflow -c "SELECT * FROM dim_ubicacion LIMIT 5;"
```

---

## Debugging

### Ver logs

```bash
# Docker
docker-compose logs -f airflow-scheduler

# Standalone
tail -f ~/airflow/logs/dag_id=sct_viales_estrella_automatizado/
```

### Conectar a BD

```bash
# Docker
docker-compose exec postgres psql -U airflow -d airflow

# Local
psql -U airflow -d airflow
```

### Variables de entorno

```bash
# Ver configuración de Airflow
airflow config list
```

---

## Solucionar problemas locales

### "Permission denied" al levantar

```bash
docker-compose down
sudo chown -R $(id -u):$(id -g) ./
docker-compose up -d
```

### "Port already in use"

```bash
# Ver qué ocupa puerto 8080
lsof -i :8080

# O cambiar puerto en docker-compose.yml
```

### "Cannot connect to postgres"

```bash
# Verificar que postgres está corriendo
docker-compose ps postgres

# Reiniciar
docker-compose restart postgres
```

### "ModuleNotFoundError"

```bash
# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall

# O en Docker
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## Checklist antes de deployar a cloud

- [ ] DAG valida sin errores
- [ ] Imports funcionan
- [ ] DAG aparece en UI
- [ ] Trigger manual funciona
- [ ] Logs muestran ejecución exitosa
- [ ] Datos cargados en BD
- [ ] No hay secretos hardcodeados
- [ ] Variables de entorno configuradas
- [ ] .env en .gitignore
- [ ] Todo commiteado en GitHub

Si todo esto está ✅, estás listo para cloud!

---

## Próximos pasos

1. Terminar testing local
2. Leer `DEPLOYMENT.md`
3. Elegir plataforma cloud
4. Seguir `CLOUD_SETUP.md`
5. Deploy! 🚀

---

**Tip:** Si algo falla localmente, también fallará en cloud. Mejor debuggear aquí primero!
