import pdfplumber
import requests
import tempfile
import re
import logging
from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger("airflow.task")

# ================================
# FUNCIONES DE LIMPIEZA
# ================================

def clean_text(val):
    """Limpia y normaliza texto."""
    if not val:
        return ""
    return str(val).replace("\n", " ").strip()

def extraer_ruta(texto):
    """Extrae el código de ruta desde el texto."""
    if not texto:
        return None
    
    # Patrón: RUTA: MEX-001
    match = re.search(r'RUTA\s*:\s*([A-Z0-9\-]+)', texto)
    if match:
        return match.group(1).strip()
    
    return None

def extract_header_info(text):
    """Extrae ruta y carretera desde el encabezado del PDF."""
    ruta = None
    carretera = None
    
    # Normalizar espacios
    text = re.sub(r"\s+", " ", text)
    
    # Extraer carretera: CARR: ...
    carretera_match = re.search(r"CARR:\s*(.*?)\s*CLAVE:", text)
    if carretera_match:
        carretera = carretera_match.group(1).strip()
    
    # Extraer ruta
    ruta = extraer_ruta(text)
    
    return ruta, carretera

# ================================
# EXTRACCIÓN
# ================================

def extract_viales(url):
    """
    Descarga y parsea un PDF de vialidad de la SCT.
    
    Args:
        url (str): URL del PDF
    
    Returns:
        list: Lista de diccionarios con datos extraídos
    
    Raises:
        requests.exceptions.RequestException: Si falla la descarga
        pdfplumber.PDFException: Si falla el parseo
    """
    
    logger.info(f"📥 Descargando PDF: {url}")
    
    try:
        response = requests.get(url, verify=False, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error descargando PDF: {e}")
        raise
    
    data = []
    
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(response.content)
            tmp.flush()
            
            with pdfplumber.open(tmp.name) as pdf:
                
                ruta = None
                carretera = None
                
                for page_num, page in enumerate(pdf.pages, 1):
                    
                    try:
                        text = page.extract_text()
                        
                        if not text:
                            logger.debug(f"  ⚠️ Página {page_num} sin texto")
                            continue
                        
                        # Extraer encabezado
                        r, c = extract_header_info(text)
                        if r:
                            ruta = r
                        if c:
                            carretera = c
                        
                        # Procesar líneas
                        lines = text.split("\n")
                        
                        for line in lines:
                            line = re.sub(r"\s+", " ", line).strip()
                            
                            # Patrón: segmento km tdpa A B C2 C3 T3S2 T3S3 OTROS lat lon
                            # Total 20+ campos numéricos
                            match = re.match(
                                r"(.+?)\s+"                    # Segmento
                                r"(\d+\.\d+)\s+"               # KM
                                r"(\d+)\s+(\d+)\s+"            # 2 campos
                                r"(\d+)\s+"                    # TDPA
                                r"([\d\.]+)\s+"                # A
                                r"([\d\.]+)\s+"                # B
                                r"([\d\.]+)\s+"                # C2
                                r"([\d\.]+)\s+"                # C3
                                r"([\d\.]+)\s+"                # T3S2
                                r"([\d\.]+)\s+"                # T3S3
                                r"([\d\.]+)\s+"                # OTROS
                                r"([\d\.]+)\s+"                # más números
                                r"([\d\.]+)\s+"                # más números
                                r"([\d\.]+)\s+"                # más números
                                r"([\d\.]+)\s+"                # más números
                                r"([\d\.]+)\s+"                # más números
                                r"([\d\.]+)\s+"                # más números
                                r"([\d\.]+)\s+"                # más números
                                r"([-]?[\d\.]+)\s+"            # Latitud
                                r"([-]?[\d\.]+)",               # Longitud
                                line
                            )
                            
                            if not match:
                                continue
                            
                            try:
                                registro = {
                                    "ruta": ruta,
                                    "carretera": carretera,
                                    "segmento": match.group(1),
                                    "km": float(match.group(2)),
                                    "tdpa": int(match.group(5)),
                                    "A": float(match.group(6)),
                                    "B": float(match.group(7)),
                                    "C2": float(match.group(8)),
                                    "C3": float(match.group(9)),
                                    "T3S2": float(match.group(10)),
                                    "T3S3": float(match.group(11)),
                                    "OTROS": float(match.group(12)),
                                    "lat": float(match.group(19)),
                                    "lon": float(match.group(20)),
                                }
                                
                                data.append(registro)
                                
                            except (ValueError, IndexError) as e:
                                logger.debug(f"  ⚠️ Error parseando: {line} - {e}")
                                continue
                        
                    except Exception as e:
                        logger.warning(f"  ⚠️ Error en página {page_num}: {e}")
                        continue
        
        logger.info(f"✅ Extracción completada: {len(data)} registros")
        return data
        
    except Exception as e:
        logger.error(f"❌ Error procesando PDF: {e}", exc_info=True)
        raise

# ================================
# CARGA
# ================================

def load_viales(data, year):
    """
    Carga datos a PostgreSQL.
    
    Args:
        data (list): Datos extraídos
        year (int): Año de los datos
    """
    
    logger.info(f"📤 Cargando {len(data)} registros para año {year}")
    
    hook = PostgresHook(postgres_conn_id="postgres_viales")
    
    try:
        # Crear/obtener ID de tiempo
        id_tiempo = hook.get_first("""
            INSERT INTO dim_tiempo (anio)
            VALUES (%s)
            ON CONFLICT (anio)
            DO UPDATE SET anio = EXCLUDED.anio
            RETURNING id_tiempo;
        """, (year,))[0]
        
        logger.info(f"  ✓ Año {year} con ID {id_tiempo}")
        
        registros_cargados = 0
        registros_fallidos = 0
        
        for i, row in enumerate(data, 1):
            try:
                # Insertar ubicación
                id_ubicacion = hook.get_first("""
                    INSERT INTO dim_ubicacion (
                        ruta, carretera, segmento_tramo, kilometro, latitud, longitud
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id_ubicacion;
                """, (
                    row["ruta"],
                    row["carretera"],
                    row["segmento"],
                    row["km"],
                    row["lat"],
                    row["lon"],
                ))[0]
                
                # Insertar vehículos y hechos
                for clasificacion in ["A", "B", "C2", "C3", "T3S2", "T3S3", "OTROS"]:
                    
                    id_vehiculo = hook.get_first("""
                        INSERT INTO dim_vehiculo (clasificacion_sct)
                        VALUES (%s)
                        ON CONFLICT (clasificacion_sct)
                        DO UPDATE SET clasificacion_sct = EXCLUDED.clasificacion_sct
                        RETURNING id_vehiculo;
                    """, (clasificacion,))[0]
                    
                    # Insertar hecho
                    hook.run("""
                        INSERT INTO fact_movilidad (
                            id_ubicacion, id_vehiculo, id_tiempo,
                            cantidad_vehiculos_tdpa, porcentaje_composicion
                        )
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (id_ubicacion, id_vehiculo, id_tiempo)
                        DO UPDATE SET
                            cantidad_vehiculos_tdpa = EXCLUDED.cantidad_vehiculos_tdpa,
                            porcentaje_composicion = EXCLUDED.porcentaje_composicion
                    """, (
                        id_ubicacion,
                        id_vehiculo,
                        id_tiempo,
                        row["tdpa"],
                        row[clasificacion],
                    ))
                
                registros_cargados += 1
                
                if i % 50 == 0:
                    logger.info(f"  ✓ Cargados {i}/{len(data)} registros")
                
            except Exception as e:
                registros_fallidos += 1
                logger.warning(f"  ❌ Error en registro {i}: {e}")
                continue
        
        logger.info(f"✅ Carga completada:")
        logger.info(f"   - Exitosos: {registros_cargados}")
        logger.info(f"   - Fallidos: {registros_fallidos}")
        
        if registros_cargados == 0:
            raise ValueError("No se cargó ningún registro")
        
    except Exception as e:
        logger.error(f"❌ Error en carga: {e}", exc_info=True)
        raise
