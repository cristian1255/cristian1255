# Procfile - Define los procesos que corren en la nube
# Heroku, Railway y otros servicios usan esto

# Webserver - El interfaz web de Airflow
web: airflow webserver --port $PORT

# Scheduler - El que ejecuta los DAGs automáticamente
scheduler: airflow scheduler

# Worker - Ejecuta las tareas en paralelo (Celery)
worker: airflow celery worker

# Flower - Monitor de Celery (opcional pero recomendado)
flower: airflow celery flower
