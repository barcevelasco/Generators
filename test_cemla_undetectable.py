# test_cemla_undetectable.py
"""
Script avanzado con técnicas anti-detección para evitar el bloqueo de ScienceDirect
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import os
import random

def human_like_delay(min_seconds=1, max_seconds=3):
    """Simula retraso humano aleatorio"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def test_cemla_undetectable():
    url = "https://www.sciencedirect.com/journal/latin-american-journal-of-central-banking/articles-in-press"
    
    print("=" * 70)
    print("🔬 TEST CEMLA - MODO INDETECTABLE")
    print("=" * 70)
    
    # Configuración avanzada para evitar detección
    chrome_options = Options()
    
    # Opciones para evitar detección
    chrome_options.add_argument("--headless=new")  # Seguimos en modo headless pero con nuevas opciones
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # User agent realista y actualizado
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0")
    
    # Desactivar características que delatan automatización
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Añadir argumentos para parecer un navegador real
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    
    # Configuración adicional para evitar detección
    chrome_options.add_argument("--lang=en-US,en;q=0.9")
    chrome_options.add_argument("--disable-extensions")
    
    # Ruta de ChromeDriver
    chromedriver_path = "/usr/local/bin/chromedriver"
    
    if not os.path.exists(chromedriver_path):
        print(f"❌ No se encontró ChromeDriver en {chromedriver_path}")
        return
    
    driver = None
    try:
        print("🚀 Iniciando Chrome con configuración indetectable...")
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Ejecutar script para ocultar que es automatizado
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
        })
        
        print(f"📡 Accediendo a {url}...")
        driver.get(url)
        
        # Espera inicial para carga
        human_like_delay(5, 8)
        
        # Intentar aceptar cookies si aparece el banner
        try:
            # Buscar botones comunes de aceptar cookies
            selectores_cookies = [
                "button[id*='accept']",
                "button[id*='Accept']",
                "button[class*='accept']",
                "button[title*='Accept']",
                "#onetrust-accept-btn-handler",
                ".accept-cookies-button",
                "button:contains('Accept')",
                "button:contains('Aceptar')"
            ]
            
            for selector in selectores_cookies:
                try:
                    cookie_btn = driver.find_element(By.CSS_SELECTOR, selector)
                    cookie_btn.click()
                    print("🍪 Botón de cookies clickeado")
                    human_like_delay(2, 3)
                    break
                except:
                    continue
        except:
            print("ℹ️ No se encontró banner de cookies o ya estaba aceptado")
        
        # Scroll simulado para parecer humano
        print("🖱️ Simulando scroll humano...")
        for i in range(3):
            driver.execute_script(f"window.scrollTo(0, {i * 300 + random.randint(0, 100)});")
            human_like_delay(0.5, 1.5)
        
        # Obtener HTML después de todo
        current_url = driver.current_url
        html = driver.page_source
        
        print(f"📍 URL actual: {current_url}")
        
        # Guardar HTML
        with open("cemla_undetectable.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("✅ HTML guardado en 'cemla_undetectable.html'")
        
        # Analizar con BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # Verificar si hay artículos
        articulos = soup.find_all('li', class_='js-article-list-item')
        print(f"\n📚 Artículos encontrados: {len(articulos)}")
        
        if len(articulos) == 0:
            # Buscar otras pistas
            print("\n🔍 ANALIZANDO ESTRUCTURA DE ERROR:")
            
            # Buscar títulos de error
            errores = soup.find_all(['h1', 'h2', 'h3'], string=re.compile(r'error|problem|access|blocked', re.I))
            for err in errores:
                print(f"⚠️ Mensaje de error: {err.get_text()}")
            
            # Buscar si hay algún iframe
            iframes = soup.find_all('iframe')
            print(f"📦 Iframes encontrados: {len(iframes)}")
            
            # Buscar el título principal
            title = soup.find('title')
            if title:
                print(f"📌 Título de la página: {title.get_text()}")
            
            # Buscar elementos con texto "cookie" o "consent"
            cookies = soup.find_all(text=re.compile(r'cookie|consent', re.I))
            print(f"🍪 Menciones de cookies: {len(cookies)}")
            
            # Si hay un iframe, intentar analizar su contenido
            if len(iframes) > 0:
                print("\n🔍 Intentando acceder al iframe...")
                try:
                    # Cambiar al primer iframe
                    driver.switch_to.frame(iframes[0])
                    human_like_delay(2, 3)
                    
                    iframe_html = driver.page_source
                    with open("cemla_iframe.html", "w", encoding="utf-8") as f:
                        f.write(iframe_html)
                    print("✅ HTML del iframe guardado en 'cemla_iframe.html'")
                    
                    # Analizar iframe
                    iframe_soup = BeautifulSoup(iframe_html, 'html.parser')
                    iframe_articulos = iframe_soup.find_all('li', class_='js-article-list-item')
                    print(f"📚 Artículos en iframe: {len(iframe_articulos)}")
                    
                except Exception as e:
                    print(f"❌ Error al acceder al iframe: {e}")
        
        else:
            print(f"\n✅ ¡Éxito! Se encontraron {len(articulos)} artículos")
            # Mostrar primeros artículos
            for i, art in enumerate(articulos[:3]):
                titulo = art.find('a', class_='article-content-title')
                fecha = art.find('span', class_='js-article-item-aip-date')
                if titulo and fecha:
                    print(f"\n{i+1}. {titulo.get_text(strip=True)[:100]}...")
                    print(f"   📅 {fecha.get_text(strip=True)}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()
            print("\n🛑 Navegador cerrado.")

if __name__ == "__main__":
    import re
    test_cemla_undetectable()
    