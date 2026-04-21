import logging
from etls.etl_viales_estrella import extract_viales, load_viales

logger = logging.getLogger("airflow.task")

def run_viales_pipeline(**kwargs):
    """
    Pipeline ETL para datos viales.
    
    Parámetros esperados (kwargs):
        - url (str): URL del PDF a procesar
        - year (int): Año del dato
    
    Retorna:
        dict: Resumen de la ejecución
    """
    url = kwargs.get("url")
    year = kwargs.get("year")
    
    if not url or not year:
        raise ValueError("Se requieren 'url' y 'year' en los parámetros")
    
    logger.info(f"🚀 Iniciando pipeline viales para {year}")
    logger.info(f"📥 Descargando desde: {url}")
    
    try:
        # Extracción
        data = extract_viales(url)
        
        if not data:
            logger.warning(f"⚠️ Sin datos para {year}")
            return {
                "status": "sin_datos",
                "year": year,
                "registros": 0,
            }
        
        logger.info(f"✅ Extraídos {len(data)} registros")
        
        # Carga
        load_viales(data, year)
        
        logger.info(f"✅ Pipeline completado para {year} - {len(data)} registros cargados")
        
        return {
            "status": "exitoso",
            "year": year,
            "registros": len(data),
        }
        
    except Exception as e:
        logger.error(f"❌ Error en pipeline: {e}", exc_info=True)
        raise
