from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

# Imports de nuestros módulos
from pipelines.viales_scraper import obtener_urls_sct
from pipelines.viales_estrella_pipeline import run_viales_pipeline

# Argumentos por defecto
default_args = {
    "owner": "Cristian",
    "start_date": datetime(2026, 1, 1),
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": True,
    "email": ["tu_email@ejemplo.com"],
}

def ejecutar_ciclo_viales(**kwargs):
    """
    Orquesta la extracción y carga del pipeline de viales.
    """
    try:
        # 1. Ejecutar scraper
        lista_viales = obtener_urls_sct()
        
        if not lista_viales:
            print("⚠️ No se encontraron URLs de viales")
            return {"status": "no_data", "count": 0}
        
        # 2. Por cada PDF, ejecutar pipeline
        resultados = []
        for item in lista_viales:
            print(f"Iniciando carga para {item['year']} - URL: {item['url']}")
            resultado = run_viales_pipeline(url=item['url'], year=item['year'])
            resultados.append(resultado)
        
        return {"status": "success", "count": len(resultados), "detalles": resultados}
        
    except Exception as e:
        print(f"❌ Error en ciclo viales: {e}")
        raise

# Definir DAG
with DAG(
    dag_id="sct_viales_estrella_automatizado",
    schedule_interval="0 2 * * *",  # Diario a las 2 AM
    timezone="America/Mexico_City",
    catchup=False,
    default_args=default_args,
    description="Pipeline ETL automatizado para datos viales de la SCT",
    tags=["viales", "sct", "produccion"],
) as dag:

    # Tarea 1: Crear tablas (idempotente)
    crear_tablas = PostgresOperator(
        task_id="crear_tablas",
        postgres_conn_id="postgres_viales",
        sql="""
        CREATE TABLE IF NOT EXISTS dim_ubicacion (
            id_ubicacion SERIAL PRIMARY KEY,
            ruta VARCHAR(50),
            carretera VARCHAR(255),
            segmento_tramo VARCHAR(255),
            kilometro DECIMAL(10,2),
            latitud DECIMAL(10,6),
            longitud DECIMAL(10,6),
            fecha_creacion TIMESTAMP DEFAULT NOW(),
            UNIQUE(carretera, kilometro, segmento_tramo, latitud, longitud)
        );

        CREATE TABLE IF NOT EXISTS dim_vehiculo (
            id_vehiculo SERIAL PRIMARY KEY,
            clasificacion_sct VARCHAR(10) UNIQUE,
            descripcion TEXT,
            fecha_creacion TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS dim_tiempo (
            id_tiempo SERIAL PRIMARY KEY,
            anio INTEGER UNIQUE,
            fecha_creacion TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS fact_movilidad (
            id_hecho SERIAL PRIMARY KEY,
            id_ubicacion INTEGER REFERENCES dim_ubicacion(id_ubicacion),
            id_vehiculo INTEGER REFERENCES dim_vehiculo(id_vehiculo),
            id_tiempo INTEGER REFERENCES dim_tiempo(id_tiempo),
            cantidad_vehiculos_tdpa INTEGER,
            porcentaje_composicion DECIMAL(10,2),
            fecha_carga TIMESTAMP DEFAULT NOW(),
            UNIQUE(id_ubicacion, id_vehiculo, id_tiempo)
        );

        -- Índices para performance
        CREATE INDEX IF NOT EXISTS idx_fact_ubicacion ON fact_movilidad(id_ubicacion);
        CREATE INDEX IF NOT EXISTS idx_fact_vehiculo ON fact_movilidad(id_vehiculo);
        CREATE INDEX IF NOT EXISTS idx_fact_tiempo ON fact_movilidad(id_tiempo);
        CREATE INDEX IF NOT EXISTS idx_ubicacion_carretera ON dim_ubicacion(carretera);
        """,
    )

    # Tarea 2: Ejecutar scraper y cargar datos
    proceso_etl_completo = PythonOperator(
        task_id="ejecutar_scraper_y_carga",
        python_callable=ejecutar_ciclo_viales,
        provide_context=True,
    )

    # Dependencias
    crear_tablas >> proceso_etl_completo

# Metadatos útiles del DAG
dag.doc = """
# DAG: SCT Viales Estrella Automatizado

## Descripción
Pipeline ETL que:
1. Hace scraping de PDFs desde el sitio de la SCT
2. Busca datos de vialidad de Yucatán
3. Parsea y carga a PostgreSQL en modelo dimensional

## Schedule
- Diario a las 2:00 AM (hora de México)
- Timezone: America/Mexico_City

## Dependencias
- PostgreSQL (conexión 'postgres_viales')
- Requests + BeautifulSoup + pdfplumber
- Selenium (para navegación)

## Contacto
Propietario: Cristian
"""
