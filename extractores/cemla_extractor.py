# extractores/cemla_extractor.py
"""
Módulo para extraer artículos del Latin American Journal of Central Banking (CEMLA)
con técnicas anti-detección.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import datetime
import pandas as pd
import re
import time
import random
import os

def human_like_delay(min_seconds=1, max_seconds=3):
    """Simula retraso humano aleatorio (función interna)"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def extraer_articulos_cemla(start_date_str=None, end_date_str=None, max_paginas=3):
    """
    Extrae artículos del Latin American Journal of Central Banking.
    
    Parámetros:
        start_date_str (str): Fecha inicial en formato 'dd.mm.yyyy'
        end_date_str (str): Fecha final en formato 'dd.mm.yyyy'
        max_paginas (int): Número máximo de páginas a extraer
    
    Retorna:
        pandas.DataFrame: DataFrame con columnas Date, Title, Link
    """
    
    url = "https://www.sciencedirect.com/journal/latin-american-journal-of-central-banking/articles-in-press"
    
    # Configurar fechas
    try:
        if start_date_str:
            start_date = datetime.datetime.strptime(start_date_str, '%d.%m.%Y')
        else:
            start_date = datetime.datetime(2000, 1, 1)
            
        if end_date_str:
            end_date = datetime.datetime.strptime(end_date_str, '%d.%m.%Y')
        else:
            end_date = datetime.datetime.now()
    except:
        start_date = datetime.datetime(2000, 1, 1)
        end_date = datetime.datetime.now()

    # Configuración anti-detección de Selenium
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Ruta de ChromeDriver (ajusta si es necesario)
    chromedriver_path = "/usr/local/bin/chromedriver"
    if not os.path.exists(chromedriver_path):
        # Buscar en otras ubicaciones comunes
        posibles_rutas = [
            "/usr/bin/chromedriver",
            "/snap/bin/chromedriver",
            "chromedriver"  # Si está en PATH
        ]
        for ruta in posibles_rutas:
            if os.path.exists(ruta) or ruta == "chromedriver":
                chromedriver_path = ruta
                break
    
    rows = []
    driver = None
    pagina_actual = 1
    
    # Diccionario de meses (inglés)
    meses_en = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12,
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    
    try:
        print(f"🔍 Iniciando extracción de CEMLA (máx {max_paginas} páginas)...")
        
        # Iniciar Chrome
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Ocultar automatización
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        while pagina_actual <= max_paginas:
            # Construir URL con paginación
            if pagina_actual == 1:
                current_url = url
            else:
                current_url = f"{url}?page={pagina_actual}"
            
            print(f"📄 Procesando página {pagina_actual}...")
            driver.get(current_url)
            
            # Espera inicial
            human_like_delay(5, 8)
            
            # Intentar aceptar cookies (solo en primera página)
            if pagina_actual == 1:
                try:
                    selectores_cookies = [
                        "button[id*='accept']", "button[id*='Accept']",
                        "#onetrust-accept-btn-handler", ".accept-cookies-button",
                        "button[class*='accept']"
                    ]
                    for selector in selectores_cookies:
                        try:
                            cookie_btn = driver.find_element(By.CSS_SELECTOR, selector)
                            cookie_btn.click()
                            print("  🍪 Cookies aceptadas")
                            human_like_delay(2, 3)
                            break
                        except:
                            continue
                except:
                    pass
            
            # Scroll simulado
            for i in range(2):
                driver.execute_script(f"window.scrollTo(0, {i * 300 + random.randint(0, 100)});")
                human_like_delay(0.5, 1)
            
            # Obtener HTML
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Buscar artículos
            articulos = soup.find_all('li', class_='js-article-list-item')
            print(f"  📚 Artículos en página: {len(articulos)}")
            
            if len(articulos) == 0:
                print("  ⚠️ No hay más artículos")
                break
            
            articulos_pagina = 0
            for art in articulos:
                # Título y enlace
                title_elem = art.find('a', class_='article-content-title')
                if not title_elem:
                    continue
                
                titulo = title_elem.get_text(strip=True)
                link = title_elem.get('href', '')
                if not link.startswith('http'):
                    link = f"https://www.sciencedirect.com{link}"
                
                # Fecha
                fecha_span = art.find('span', class_='js-article-item-aip-date')
                if not fecha_span:
                    continue
                
                fecha_texto = fecha_span.get_text(strip=True)
                fecha_match = re.search(r'Available online\s+(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', fecha_texto)
                if not fecha_match:
                    continue
                
                dia = int(fecha_match.group(1))
                mes_str = fecha_match.group(2).lower()
                año = int(fecha_match.group(3))
                
                # Convertir mes a número
                mes_num = None
                for key, value in meses_en.items():
                    if key in mes_str or mes_str in key:
                        mes_num = value
                        break
                
                if not mes_num:
                    continue
                
                parsed_date = datetime.datetime(año, mes_num, dia)
                
                # Filtrar por fecha
                if parsed_date < start_date or parsed_date > end_date:
                    continue
                
                # Autores (opcional)
                autor = ""
                autor_elem = art.find('div', class_='js-article-author-list')
                if autor_elem:
                    autor = autor_elem.get_text(strip=True)
                
                titulo_final = f"{autor}: {titulo}" if autor else titulo
                
                rows.append({
                    "Date": parsed_date,
                    "Title": titulo_final,
                    "Link": link,
                    "Organismo": "CEMLA"
                })
                articulos_pagina += 1
            
            print(f"  ✅ Artículos agregados en esta página: {articulos_pagina}")
            
            # Si no encontramos artículos en esta página, probablemente llegamos al final
            if articulos_pagina == 0 and pagina_actual > 1:
                print("  📭 No se encontraron más artículos en el rango de fechas")
                break
            
            pagina_actual += 1
            human_like_delay(2, 4)  # Pausa entre páginas
    
    except Exception as e:
        print(f"❌ Error en extracción: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()
            print("🛑 Navegador cerrado.")
    
    # Crear DataFrame
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.drop_duplicates(subset=['Link'])
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date", ascending=False)
        print(f"✅ Total artículos extraídos: {len(df)}")
    
    return df

# Si el script se ejecuta directamente, hacer una prueba
if __name__ == "__main__":
    print("=" * 70)
    print("🔬 Probando extractor CEMLA directamente")
    print("=" * 70)
    
    # Probar con marzo 2026
    df = extraer_articulos_cemla("01.03.2026", "31.03.2026", max_paginas=2)
    
    if not df.empty:
        print("\n📋 RESULTADOS:")
        print(df[['Date', 'Title']].to_string())
    else:
        print("❌ No se encontraron artículos")