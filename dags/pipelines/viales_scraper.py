import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger("airflow.task")

def obtener_urls_sct():
    """
    Scraper que obtiene URLs de PDFs de vialidad desde el sitio de la SCT.
    
    Busca específicamente datos de Yucatán.
    
    Retorna:
        list: Lista de dicts con estructura:
            [
                {"year": 2024, "url": "https://..."},
                {"year": 2023, "url": "https://..."},
                ...
            ]
    
    Raises:
        requests.exceptions.RequestException: Si falla la descarga
    """
    
    BASE = "https://micrs.sct.gob.mx"
    URL = BASE + "/index.php/infraestructura/direccion-general-de-servicios-tecnicos/datos-viales"
    
    resultados = []
    
    try:
        logger.info(f"📥 Descargando página principal: {URL}")
        
        response = requests.get(URL, timeout=10, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # =========================================
        # 1. Obtener años disponibles
        # =========================================
        logger.info("🔍 Buscando años disponibles...")
        anios = []
        
        for a in soup.select("a[href*='datos-viales/20']"):
            texto = a.text.strip()
            if texto.isdigit():
                anios.append((texto, BASE + a.get("href")))
                logger.debug(f"  ✓ Encontrado año: {texto}")
        
        logger.info(f"📅 Años encontrados: {[a[0] for a in anios]}")
        
        # =========================================
        # 2. Por cada año, buscar Yucatán
        # =========================================
        logger.info("🔎 Buscando datos de Yucatán...")
        
        for year, url_anio in anios[:10]:  # Limitar a últimos 10 años
            
            try:
                logger.info(f"  📋 Procesando año {year}...")
                
                response_anio = requests.get(url_anio, timeout=10, verify=False)
                response_anio.raise_for_status()
                
                soup_anio = BeautifulSoup(response_anio.text, "html.parser")
                
                # Buscar link de descarga de Yucatán
                encontrado = False
                
                for a in soup_anio.select("a.download"):
                    if "yucat" in a.text.lower():
                        pdf_url = BASE + a.get("href")
                        resultados.append({
                            "year": int(year),
                            "url": pdf_url
                        })
                        logger.info(f"    ✅ Yucatán {year}: {pdf_url[:80]}...")
                        encontrado = True
                        break
                
                if not encontrado:
                    logger.warning(f"  ⚠️ No encontrado Yucatán para {year}")
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"  ❌ Error descargando año {year}: {e}")
                continue
            except Exception as e:
                logger.error(f"  ❌ Error procesando año {year}: {e}")
                continue
        
        logger.info(f"✅ Scraping completado. URLs encontradas: {len(resultados)}")
        
        return resultados
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error en scraper: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}", exc_info=True)
        raise
